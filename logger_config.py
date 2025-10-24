import logging
import logging.config
import sys
from pythonjsonlogger import jsonlogger
from config import Config

class SensitiveDataFilter(logging.Filter):
    
    SENSITIVE_PATTERNS = ['apiKey', 'signature', 'API_KEY', 'API_SECRET']
    
    def filter(self, record):
        if hasattr(record, 'msg'):
            msg_str = str(record.msg)
            for pattern in self.SENSITIVE_PATTERNS:
                if pattern in msg_str:
                    record.msg = msg_str.replace(pattern, '[REDACTED]')
        return True

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "sensitive_filter": {
            "()": SensitiveDataFilter,
        }
    },
    "formatters": {
        "json": {
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%SZ",
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
        },
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": Config.LOG_FILE,
            "maxBytes": 10485760,
            "backupCount": 5,
            "formatter": "json",
            "filters": ["sensitive_filter"],
        },
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "standard",
            "filters": ["sensitive_filter"],
        }
    },
    "loggers": {
        "": {
            "handlers": ["file", "console"],
            "level": Config.LOG_LEVEL,
            "propagate": False
        }
    }
}

def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
    return logging.getLogger(__name__)
