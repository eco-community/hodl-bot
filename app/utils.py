import datetime
from decimal import Decimal

import aiohttp
import sentry_sdk
from tortoise import timezone
from discord.ext import commands

import config
from app.models import User, UserEpoch
from app.constants import EPOCH_DURATION_IN_DAYS, SPACE_BETWEEN_EPOCHS_IN_SECONDS


def use_sentry(client, **sentry_args):
    """
    Use this compatibility library as a bridge between Discord and Sentry.
    Arguments:
        client: The Discord client object (e.g. `discord.AutoShardedClient`).
        sentry_args: Keyword arguments to pass to the Sentry SDK.
    """

    sentry_sdk.init(**sentry_args)

    @client.event
    async def on_error(event, *args, **kwargs):
        """Don't ignore the error, causing Sentry to capture it."""
        raise

    @client.event
    async def on_command_error(msg, error):
        # don't report errors to sentry related to wrong permissions
        if not isinstance(
            error,
            (
                commands.MissingRole,
                commands.MissingAnyRole,
                commands.BadArgument,
                commands.MissingRequiredArgument,
                commands.errors.CommandNotFound,
            ),
        ):
            raise error


async def ensure_registered(user_id: int) -> User:
    """Ensure that user is registered in our database"""

    user, _ = await User.get_or_create(id=user_id)
    return user


async def get_user_balance(user_id: int) -> Decimal:
    """Get current user balance"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{config.ACCOUNTANT_API_PATH}/balances", json={"ids": [str(user_id)]}) as response:
                response_json = await response.json()
                str_points = response_json[0]["points"]
                return Decimal(str_points)
        except IndexError:
            return Decimal(0)


def generate_start_datetime_for_latest_epoch(latest_epoch=None) -> datetime.datetime:
    if not latest_epoch:
        # generate genesis epoch start_datetime
        return timezone.now()
    else:
        return latest_epoch.end_datetime + datetime.timedelta(seconds=SPACE_BETWEEN_EPOCHS_IN_SECONDS)


def generate_end_datetime_for_latest_epoch(latest_epoch=None) -> datetime.datetime:
    if not latest_epoch:
        # generate genesis epoch end_datetime
        return timezone.now() + datetime.timedelta(days=EPOCH_DURATION_IN_DAYS)
    else:
        return latest_epoch.end_datetime + datetime.timedelta(
            days=EPOCH_DURATION_IN_DAYS, seconds=SPACE_BETWEEN_EPOCHS_IN_SECONDS
        )


async def update_balance_and_epoch_lowest_balance(user_id: int, points: Decimal, epoch_id: int, is_sender=False):
    """Note: you need to use these inside a transaction for better performance and to prevent race conditions"""
    user = await User.filter(id=user_id).select_for_update().get(id=user_id)
    user.balance = user.balance - points if is_sender else user.balance + points
    await user.save(update_fields=["balance", "modified_at"])
    # update epoch_lowest_balance
    user_epoch, is_created = await UserEpoch.get_or_create(
        user_id=user_id, epoch_id=epoch_id, defaults={"epoch_lowest_balance": user.balance}
    )
    if not is_created and user.balance < user_epoch.epoch_lowest_balance:
        user_epoch.epoch_lowest_balance = user.balance
        await user_epoch.save(update_fields=["epoch_lowest_balance", "modified_at"])


def pp_points(balance: Decimal) -> str:
    """Pretty print points"""
    str_balance = f"{balance:.1f}"
    suffix = ".0"
    # backport from Python 3.9 https://docs.python.org/3/library/stdtypes.html#str.removesuffix
    if suffix and str_balance.endswith(suffix):
        return str_balance[: -len(suffix)]
    else:
        return str_balance[:]


def display_staking_info(points: Decimal, epoch_lowest_balance: Decimal, current_epoch) -> str:
    return f"Your Points Balance: `{pp_points(points)}`{config.POINTS_EMOJI}\nHow many Points you are staking: `{pp_points(epoch_lowest_balance * current_epoch.portfolio_percentage)}`{config.POINTS_EMOJI}\nWhen the Epoch ends: <t:{int(current_epoch.end_datetime.timestamp())}>\nEstimated Reward: `{pp_points(epoch_lowest_balance * current_epoch.apy * current_epoch.portfolio_percentage)}`{config.POINTS_EMOJI}"  # noqa: E501
