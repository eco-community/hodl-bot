import os
from dotenv import load_dotenv


# load env variables
load_dotenv()


pg_user = os.getenv("POSTGRES_USER")
pg_password = os.getenv("POSTGRES_PASSWORD")
pg_db = os.getenv("POSTGRES_DB")


SENTRY_ENV_NAME = "eco_hodl_bot"
GUILD_INDEX = 0


TORTOISE_ORM = {
    "connections": {"default": f"postgres://{pg_user}:{pg_password}@localhost:5435/{pg_db}"},
    "apps": {
        "app": {
            "models": ["app.models", "aerich.models"],
        }
    },
}
