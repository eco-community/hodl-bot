import sys
import logging

from discord import Intents, Activity, ActivityType
from tortoise import Tortoise
from discord.ext import commands
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from discord_slash import SlashCommand

import config
from constants import SENTRY_ENV_NAME, TORTOISE_ORM
from app.utils import use_sentry


if __name__ == "__main__":
    # initialize bot params
    intents = Intents.default()
    intents.members = True
    intents.messages = True
    activity = Activity(type=ActivityType.playing, name=f"{config.PROJECT_NAME} APY".upper())
    bot = commands.Bot(command_prefix="!hodl_bot.", help_command=None, intents=intents, activity=activity)
    SlashCommand(bot)

    # init sentry SDK
    use_sentry(
        bot,
        dsn=config.SENTRY_API_KEY,
        environment=SENTRY_ENV_NAME,
        integrations=[AioHttpIntegration()],
    )

    # setup logger
    file_handler = logging.FileHandler(filename="hodl-bot.log")
    stdout_handler = logging.StreamHandler(sys.stdout)

    logging.basicConfig(
        level=logging.getLevelName(config.LOG_LEVEL),
        format="%(asctime)s %(levelname)s:%(message)s",
        handlers=[file_handler if config.LOG_TO_FILE else stdout_handler],
    )
    bot.loop.run_until_complete(Tortoise.init(config=TORTOISE_ORM))
    bot.load_extension("app.extensions.sync_discord")
    bot.load_extension("app.extensions.onboarding")
    bot.load_extension("app.extensions.epochs")
    bot.run(config.TOKEN)
