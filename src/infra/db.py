import loggingx as logging
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import Engine
from sqlalchemy import create_engine as _create_engine


class DBConfig(BaseSettings):
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = Field(exclude=True)
    database: str = "fastapi_test"
    connection_options: str | None = None

    model_config = SettingsConfigDict(env_prefix="db_", env_file=(".env", ".env.local"), extra="ignore")

    def to_url(self) -> str:
        url = f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        if self.connection_options:
            url += f"?{self.connection_options}"
        return url


def create_engine(config: DBConfig) -> Engine:
    logging.info("database config", extra={"config": config.model_dump()})
    return _create_engine(config.to_url())
