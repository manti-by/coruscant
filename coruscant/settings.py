import inspect
import logging
import os
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse


BASE_DIR = Path(__file__).resolve().parent.parent

API_URL = os.getenv("API_URL", "http://192.168.1.100/api/v1")

SYNC_API_URL = os.getenv("SYNC_API_URL", f"{API_URL}/sensors/logs/")

KAFKA_SERVERS = os.getenv("KAFKA_SERVERS", "192.168.1.100:9092").split()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://odin:odin@192.168.1.100/odin")
DATABASE_PATH = os.getenv("DATABASE_PATH", "/var/lib/coruscant/db.sqlite")

"""
28000007176e41 - rad
280000071766e4 - wf-1-in, 28000007173569 - wf-1-out
28000007162e15 - wf-2-in, 28000007177269 - wf-1-out
"""
TEMP_SENSORS = {"28000007176e41", "28000007162e15", "28000007173569", "280000071766e4", "28000007177269"}

VALVE_SENSOR_ID = "28000007173569"

VALVE_MAP = {
    15: "VALVE-OPEN",
    16: "VALVE-CLOSED",
}

PUMP_MAP = {
    11: "PUMP-RD",
    12: "PUMP-WF-2",
}

SERVO_MAP = {
    35: "SERVO-WR",
    36: "SERVO-GR",
}

SERVO_TEMP_HYSTERESIS = Decimal("0.5")

VALVE_ACT_TIMEOUT = 60
VALVE_TEMP_HYSTERESIS = Decimal("0.5")

logs_api = urlparse(os.getenv("LOGS_API_URL", "http://192.168.1.100/api/v1/core/logs/"))


class VerboseFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        result = super().format(record)
        if record.exc_info:
            extra = self._get_stack_info()
            if extra:
                result = f"{result}\nLocal variables: {extra}"
        return result

    def _get_stack_info(self) -> str | None:
        """Collect local variables from the innermost exception frame."""
        try:
            frame = inspect.trace()[-1][0] if inspect.trace() else None
            if frame is None:
                return None
            local_vars = {k: v for k, v in frame.f_locals.items() if not k.startswith("__") and not callable(v)}
            if not local_vars:
                return None
            return ", ".join(f"{k}={v!r}" for k, v in local_vars.items())
        except Exception:
            return None
        finally:
            del frame


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)-6s: %(filename)-8s - %(message)",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "()": VerboseFormatter,
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.getenv("LOG_PATH", "/var/log/coruscant/events.log"),
            "formatter": "standard",
        },
        "http": {
            "class": "logging.handlers.HTTPHandler",
            "host": logs_api.netloc,
            "url": logs_api.path,
            "method": "POST",
            "level": "INFO",
            "formatter": "standard",
        },
    },
    "loggers": {
        "": {"handlers": ["console", "file", "http"], "level": "DEBUG", "propagate": True},
        "kafka": {"handlers": ["console", "file"], "level": "WARNING", "propagate": True},
    },
}
