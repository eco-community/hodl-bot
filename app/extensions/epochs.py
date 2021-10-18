import logging
import asyncio
import datetime

from tortoise import timezone
from discord.ext import commands, tasks
from sentry_sdk import capture_exception, Hub

from app.models import Epoch
from app.constants import CHECK_EPOCH_IN_MINUTES
from app.utils import generate_start_datetime_for_latest_epoch, generate_end_datetime_for_latest_epoch


class EpochCog(commands.Cog):
    """Cog which is responsible for creating and updating epochs"""

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.epoch_cron_task_lock = asyncio.Lock()
        self.epoch_cron_task.start()

    def cog_unload(self):
        self.epoch_cron_task.cancel()

    @tasks.loop(minutes=CHECK_EPOCH_IN_MINUTES)
    async def epoch_cron_task(self):
        with Hub(Hub.current):
            # ensure that only one instance of job is running, other instances will be discarded
            if not self.epoch_cron_task_lock.locked():
                await self.epoch_cron_task_lock.acquire()
                try:
                    await self.check_increment_epoch()
                except Exception as e:
                    logging.debug(f":::hodl_bot: {e}")
                    capture_exception(e)
                finally:
                    self.epoch_cron_task_lock.release()

    @epoch_cron_task.before_loop
    async def before_epoch_cron_task(self):
        await self.bot.wait_until_ready()

    async def check_increment_epoch(self) -> None:
        """Always keep current epoch in database, increment epoch if needed"""
        latest_epoch = await Epoch.all().order_by("-id").first()
        if not latest_epoch:
            # init genesis epoch
            await Epoch.create(
                start_datetime=generate_start_datetime_for_latest_epoch(),
                end_datetime=generate_end_datetime_for_latest_epoch(),
            )
            return None
        # check if latest epoch end date isn't too close and if it is generate subsequent epoch
        is_too_close = (
            latest_epoch.end_datetime - datetime.timedelta(minutes=2 * CHECK_EPOCH_IN_MINUTES) < timezone.now()
        )
        if is_too_close:
            await Epoch.create(
                start_datetime=generate_start_datetime_for_latest_epoch(latest_epoch),
                end_datetime=generate_end_datetime_for_latest_epoch(latest_epoch),
            )
            return None


def setup(bot):
    bot.add_cog(EpochCog(bot))
