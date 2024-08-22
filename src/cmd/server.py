from ..logger import LoggerConfig, set_logger
from ..restapi import RestAPI

set_logger(LoggerConfig())

app = RestAPI().create_app()
