# BaseSettings is a ready made class that knows how to read settings.
from pydantic_settings import BaseSettings, SettingsConfigDict


# settings means is a kind of base settings, so it reads settings
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

# each line means name: type = default value
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "tasks_api"
    db_user: str = "postgres"
    db_password: str


# this reads .env and stores the result in settings.
settings = Settings()