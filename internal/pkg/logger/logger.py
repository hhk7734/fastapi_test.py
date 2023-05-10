import json
import logging
import sys
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

from loguru import logger as _logger

_LEVEL_TO_LOWER_NAME = {
    logging.CRITICAL: "fatal",
    logging.ERROR: "error",
    logging.WARNING: "warn",
    logging.INFO: "info",
    logging.DEBUG: "debug",
}


def _patching(record: dict[str, Any]):
    subset = {
        "level": _LEVEL_TO_LOWER_NAME[record["level"].no],
        "time": record["time"].timestamp(),
        "caller": "/".join(record["file"].path.split("/")[-2:]) + f":{record['line']}",
        "msg": record["message"],
        **record["extra"],
    }
    record["extra"]["serialized"] = json.dumps(subset)


class _LevelFilter:
    def __init__(self, level: str):
        self.level = level

    def __call__(self, record: dict[str, Any]):
        levelno = _logger.level(self.level).no
        return record["level"].no >= levelno


_logger.remove(0)

_logger = _logger.patch(_patching)

_level_filter = _LevelFilter("DEBUG")
_logger.add(sys.stderr, format="{extra[serialized]}", filter=_level_filter)

_ctx = ContextVar[dict[str, Any]]("logger_context", default={})


def set_level(level: str) -> None:
    _level_filter.level = level


@contextmanager
def new_context(**kwargs) -> None:
    new_ctx = {**_ctx.get(), **kwargs}
    token = _ctx.set(new_ctx)
    yield
    _ctx.reset(token)


def set_fields(**kwargs) -> None:
    _ctx.get().update(kwargs)


def get_field(key: str) -> tuple[Any, bool]:
    try:
        return _ctx.get()[key], True
    except KeyError:
        return None, False


def fileds() -> dict[str, Any]:
    return _ctx.get()


def delete_field(key: str) -> None:
    _ctx.get().pop(key, None)


def contextual_logger():
    kwargs = _ctx.get()
    if len(kwargs) == 0:
        return _logger

    return _logger.bind(**kwargs)


def debug(msg: str, *args, **kwargs) -> None:
    contextual_logger().debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs) -> None:
    contextual_logger().info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs) -> None:
    contextual_logger().warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs) -> None:
    contextual_logger().error(msg, *args, **kwargs)
