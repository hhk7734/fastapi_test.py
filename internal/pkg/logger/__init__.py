from internal.pkg.logger.ctxlogger import CtxLogger as _CtxLogger
from internal.pkg.logger.ctxlogger import CtxLoggerConfig

logger = _CtxLogger(CtxLoggerConfig())

__all__ = ["logger", "CtxLoggerConfig"]
