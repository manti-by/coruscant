import os
from decimal import Decimal
from pathlib import Path

from apollo.services.models import Sensor


BASE_DIR = Path(__file__).resolve().parent.parent

MODE = os.getenv("MODE", "warm")

DATABASE_PATH = os.getenv("DB_PATH", "/var/lib/apollo/db.sqlite")

SENSORS = {
    "T1": Sensor(sensor_id="28000007176e41", label_shine="CONNECT", label_warm="RADI-RS", context={"mode": MODE}),
    "T2": Sensor(sensor_id="28000007162e15", label_shine="REACTOR", label_warm="WF-1-IN", context={"mode": MODE}),
    "T3": Sensor(sensor_id="28000007173569", label_shine="FRZR-LO", label_warm="WF-1-OU", context={"mode": MODE}),
    "T4": Sensor(sensor_id="280000071766e4", label_shine="FRZR-HI", label_warm="WF-2-IN", context={"mode": MODE}),
    "T5": Sensor(sensor_id="28000007177269", label_shine="STORAGE", label_warm="WF-2-OU", context={"mode": MODE}),
}

VALVE_SENSOR_ID = "28000007173569"

RELAY_HEAT_PIN = 11
RELAY_COOL_PIN = 12

WF_PUMP_PIN = 15
RD_PUMP_PIN = 16

SERVO_MAP = {
    35: "CENTAX-01",
    36: "CENTAX-02",
    37: "CENTAX-03",
    38: "CENTAX-04",
    40: "CENTAX-05",
}

SERVO_TEMP_HYSTERESIS = Decimal("1.0")

VALVE_ACT_TIMEOUT = 60
VALVE_TEMP_HYSTERESIS = Decimal("1.0")

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
            "filename": os.getenv("LOG_PATH", "/var/log/apollo/events.log"),
            "formatter": "standard",
        },
    },
    "loggers": {"": {"handlers": ["console", "file"], "level": "INFO", "propagate": True}},
}
