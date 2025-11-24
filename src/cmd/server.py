from ..logger import LoggerConfig, set_logger
from ..tracer import set_tracer

set_logger(LoggerConfig())
set_tracer()

from ..restapi import RestAPI  # noqa: E402

app = RestAPI().create_app()
