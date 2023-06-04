import inspect
import json
import logging
import time
from contextvars import ContextVar
from logging import Formatter, LogRecord
from typing import Any

# https://docs.python.org/3/howto/logging.html#optimization
logging._srcfile = None  # pylint: disable=protected-access
logging.logThreads = False
logging.logProcesses = False
logging.logMultiprocessing = False

# https://docs.python.org/3/library/logging.html#logrecord-attributes
_DEFAULT_KEYS = (
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
)

_LEVEL_TO_LOWER_NAME = {
    logging.CRITICAL: "fatal",
    logging.ERROR: "error",
    logging.WARNING: "warn",
    logging.INFO: "info",
    logging.DEBUG: "debug",
}


class JsonFormatter(Formatter):
    def __init__(
        self,
        context: ContextVar[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__()
        self._context = context

    def format(self, record: LogRecord):
        msg_dict = {
            "time": record.created,
            "level": _LEVEL_TO_LOWER_NAME[record.levelno],
        }

        frames = inspect.getouterframes(inspect.currentframe())
        depth = 7
        while frames[depth].filename.endswith("logging/__init__.py"):
            depth += 1
        depth += 1

        msg_dict["caller"] = (
            "/".join(frames[depth].filename.split("/")[-2:]) + f":{frames[depth].lineno}"
        )

        msg_dict["msg"] = record.getMessage()

        if self._context is not None:
            for k, v in self._context.get().items():
                msg_dict[k] = v

        # extra
        if (extra := record.__dict__.get("extra", None)) is None:
            extra = record.__dict__
        for k, v in extra.items():
            if k not in _DEFAULT_KEYS and not k.startswith("_"):
                msg_dict[k] = v

        # Set ensure_ascii to False to output the message as it is typed.
        return json.dumps(msg_dict, ensure_ascii=False)


class TextFormatter(Formatter):
    def __init__(self, context: ContextVar[dict[str, Any]] | None) -> None:
        super().__init__()
        self._context = context

    @staticmethod
    def _iso8601(record: LogRecord) -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%S.%%03dZ", time.gmtime(record.created)) % record.msecs

    def format(self, record: LogRecord):
        frames = inspect.getouterframes(inspect.currentframe())
        depth = 7
        while frames[depth].filename.endswith("logging/__init__.py"):
            depth += 1
        depth += 1

        caller = "/".join(frames[depth].filename.split("/")[-2:]) + f":{frames[depth].lineno}"

        msg_dict = {}
        if self._context is not None:
            for k, v in self._context.get().items():
                msg_dict[k] = v

        # extra
        if (extra := record.__dict__.get("extra", None)) is None:
            extra = record.__dict__
        for k, v in extra.items():
            if k not in _DEFAULT_KEYS and not k.startswith("_"):
                msg_dict[k] = v

        # Set ensure_ascii to False to output the message as it is typed.
        return f"{self._iso8601(record)} | {record.levelname:7} | {caller} | {record.getMessage()} | {json.dumps(msg_dict, ensure_ascii=False)}"
