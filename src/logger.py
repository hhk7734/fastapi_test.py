from enum import StrEnum

import loggingx as logging
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(StrEnum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warn"
    ERROR = "error"
    CRITICAL = "critical"

    def get_level(self) -> int:
        return getattr(logging, self.value.upper())


class LogFormat(StrEnum):
    JSON = "json"
    CONSOLE = "console"


class LoggerConfig(BaseSettings):
    level: LogLevel = LogLevel.INFO
    format: LogFormat = LogFormat.JSON

    model_config = SettingsConfigDict(env_prefix="LOG_", env_file=(".env", ".env.local"), extra="ignore")


def set_logger(config: LoggerConfig) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.ConsoleFormatter() if config.format == LogFormat.CONSOLE else logging.JSONFormatter())
    logging.basicConfig(level=config.level.get_level(), handlers=[handler])
    logging.info("logger config", extra={"config": config.model_dump()})

    for logger in logging.getLogger().manager.loggerDict.values():
        if isinstance(logger, logging.Logger):
            logger.handlers.clear()

    logging.getLogger("uvicorn.error").addHandler(handler)
    logging.getLogger("uvicorn.error").propagate = False
