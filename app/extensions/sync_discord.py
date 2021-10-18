import re
from decimal import Decimal

import discord
from discord.ext import commands
from tortoise.query_utils import Q
from tortoise.transactions import in_transaction

import config
from app.models import User, Epoch
from app.utils import update_balance_and_epoch_lowest_balance


class SyncDiscordCog(commands.Cog):
    """Cog which is responsible for keeping points from discord in sync with database"""

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.points_regex = re.compile("<:points:819648258112225316>(\\d*\\.?\\d+)")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # ignore bot's own messages
        if message.author == self.bot.user:
            return None

        # ignore messages from DM
        if not message.guild:
            return None

        # only react to messages from points log channel
        if not message.channel.id == config.POINTS_LOG_CHANNEL_ID:
            return None

        # parse message event
        sender_id = message.raw_mentions[0]
        receivers_ids = message.raw_mentions[1:]
        # remove comma from string (because of The Accountant Bot)
        points = Decimal(self.points_regex.findall(message.system_content.replace(",", ""))[0])

        # check which users are in database and are staking
        stacking_users_ids = await User.filter(Q(id__in=[*receivers_ids, sender_id]) & Q(is_staking=True)).values_list(
            "id", flat=True
        )
        is_sender_staking = sender_id in stacking_users_ids
        receivers_who_stake_ids = list(set(receivers_ids).intersection(set(stacking_users_ids)))

        # get current epoch
        current_epoch = await Epoch.all().order_by("-id").first()

        async with in_transaction():
            # update sender points if they are staking
            if is_sender_staking:
                await update_balance_and_epoch_lowest_balance(
                    user_id=sender_id,
                    points=points,
                    epoch_id=current_epoch.id,
                    is_sender=True,
                )

            # update receivers if they are staking
            if receivers_who_stake_ids:
                for receiver_id in receivers_who_stake_ids:
                    await update_balance_and_epoch_lowest_balance(
                        user_id=receiver_id,
                        points=points,
                        epoch_id=current_epoch.id,
                        is_sender=False,
                    )

        return None


def setup(bot):
    bot.add_cog(SyncDiscordCog(bot))
