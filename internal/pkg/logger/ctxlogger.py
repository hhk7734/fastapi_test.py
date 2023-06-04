import logging
from contextlib import contextmanager
from contextvars import ContextVar
from enum import StrEnum
from typing import Any

from pydantic import BaseSettings

from internal.pkg.logger.formatter import JsonFormatter, TextFormatter

_ctx = ContextVar[dict[str, Any]]("ctxLoggerContext", default={})


class CtxLoggerConfig(BaseSettings):
    class Format(StrEnum):
        json = "json"
        text = "text"

    class Level(StrEnum):
        fatal = "fatal"
        error = "error"
        warn = "warn"
        info = "info"
        debug = "debug"

    format: Format = Format.json
    level: Level = Level.info

    class Config:
        env_prefix = "LOG_"
        env_file = ".env"
        env_file_encoding = "utf-8"


class CtxLogger:
    def __init__(self, config: CtxLoggerConfig, name: str = "ctxLogger") -> None:
        self._logger = logging.getLogger(name)
        self._handler = logging.StreamHandler()
        self._logger.addHandler(self._handler)
        self._logger.propagate = False

        self.setConfig(config)

    def setLevel(self, level: int | str) -> None:
        if isinstance(level, str):
            level = getattr(logging, level.upper(), None)
            if level is None:
                raise ValueError(f"CtxLogger not support {level} level")
        self._logger.setLevel(level)

    def setFormat(self, format: str) -> None:  # pylint: disable=redefined-builtin
        match format:
            case "json":
                self._handler.setFormatter(JsonFormatter(_ctx))
            case "text":
                self._handler.setFormatter(TextFormatter(_ctx))
            case _:
                raise ValueError("CtxLogger supports only json or text format")

    def setConfig(self, config: CtxLoggerConfig) -> None:
        self.setLevel(config.level)
        self.setFormat(config.format)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.debug(msg, *args, extra=kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.info(msg, *args, extra=kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.warning(msg, *args, extra=kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.error(msg, *args, extra=kwargs)

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.exception(msg, *args, extra=kwargs)

    @staticmethod
    @contextmanager
    def newContext(**kwargs) -> None:
        new_ctx = {**_ctx.get(), **kwargs}
        token = _ctx.set(new_ctx)
        yield
        _ctx.reset(token)
