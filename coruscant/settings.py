import os
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse


BASE_DIR = Path(__file__).resolve().parent.parent

API_URL = os.getenv("API_URL", "http://192.168.1.100/api/v1")

SYNC_API_URL = os.getenv("SYNC_API_URL", f"{API_URL}/sensors/logs/")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://odin:odin@192.168.1.100/odin")
DATABASE_PATH = os.getenv("DATABASE_PATH", "/var/lib/coruscant/db.sqlite")

"""
28000007176e41 - rad
280000071766e4 - wf-1-in, 28000007173569 - wf-1-out
28000007162e15 - wf-2-in, 28000007177269 - wf-1-out
"""
TEMP_SENSORS = {"28000007176e41", "28000007162e15", "28000007173569", "280000071766e4", "28000007177269"}

VALVE_SENSOR_ID = "28000007173569"

RELAY_HEAT_PIN = 15
RELAY_COOL_PIN = 16

PUMP_MAP = {
    11: "PUMP-WF-2",
    12: "PUMP-RD",
}

SERVO_MAP = {
    35: "SERVO-WR",
    36: "SERVO-GR",
}

SERVO_TEMP_HYSTERESIS = Decimal("0.5")

VALVE_ACT_TIMEOUT = 60
VALVE_TEMP_HYSTERESIS = Decimal("0.5")

logs_api = urlparse(os.getenv("LOGS_API_URL", "http://192.168.1.100/api/v1/core/logs/"))

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)-6s: %(filename)-8s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
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
    "loggers": {"": {"handlers": ["console", "file", "http"], "level": "INFO", "propagate": True}},
}
