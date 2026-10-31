# BaseSettings is a ready made class that reads settings from environment
# variables and from the .env file
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # extra="ignore": other lines in .env (like TEST_DATABASE_URL) are skipped
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # e.g. postgresql://postgres:password@localhost:5432/tasks_api
    database_url: str


# reads .env once and keeps the result in settings.
# without DATABASE_URL the API doesn't start, and the message says why
try:
    settings = Settings()
except ValidationError:
    raise SystemExit(
        "Missing environment variable: DATABASE_URL (copy .env.example to .env)"
    ) from None
