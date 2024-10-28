from ..logger import LoggerConfig, set_logger

set_logger(LoggerConfig())

from ..restapi import RestAPI  # noqa: E402

app = RestAPI().create_app()
