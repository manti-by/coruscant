import os
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse


BASE_DIR = Path(__file__).resolve().parent.parent

API_URL = os.getenv("API_URL", "http://192.168.1.100/api/v1")
API_TOKEN = os.getenv("API_TOKEN", "insecure-api-token")

REDIS_URL = os.getenv("REDIS_URL", "redis://192.168.1.100:6379/0")
REDIS_RELAYS_CHANNEL = os.getenv("REDIS_RELAYS_CHANNEL", "relays:control")
REDIS_SENSORS_CHANNEL = os.getenv("REDIS_SENSORS_CHANNEL", "sensors:telemetry")
REDIS_RELAY_STATE_KEY_PREFIX = os.getenv("REDIS_RELAY_STATE_KEY_PREFIX", "relays:state:")

"""
28000007176e41 - rad
280000071766e4 - wf-1-in, 28000007173569 - wf-1-out
28000007162e15 - wf-2-in, 28000007177269 - wf-1-out
"""
TEMP_SENSORS = {"28000007176e41", "28000007162e15", "28000007173569", "280000071766e4", "28000007177269"}

VALVE_SENSOR_ID = "28000007173569"

VALVE_MAP = {
    16: "VALVE-OPEN",
    18: "VALVE-CLOSED",
}

PUMP_MAP = {
    11: "PUMP-WF-2",
    12: "PUMP-WF-1",
    13: "PUMP-NC",
    15: "PUMP-RD",
}

SERVO_MAP = {
    29: "SERVO-SR",
    31: "SERVO-GR",
    33: "SERVO-NC",
    35: "SERVO-HL",
    37: "SERVO-BR",
    38: "SERVO-WR",
}

SERVO_TEMP_HYSTERESIS = Decimal("0.5")

# TODO: Read from a database
VALVE_TARGET_TEMP = Decimal("27.0")
VALVE_TEMP_HYSTERESIS = Decimal("0.5")
VALVE_ACT_TIMEOUT = 60

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
    "loggers": {
        "": {"handlers": ["console", "file", "http"], "level": "DEBUG", "propagate": True},
    },
}
