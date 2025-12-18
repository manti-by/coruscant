from __future__ import annotations

import logging.config
import sqlite3
from typing import TYPE_CHECKING

from coruscant.exceptions import PostgresConnectionErrorException, SQLiteConnectionErrorException
from coruscant.services.database import get_sensor, get_sensor_data
from coruscant.services.gpio import set_gpio_state, setup_gpio
from coruscant.settings import DATABASE_PATH, LOGGING, SERVO_MAP, SERVO_TEMP_HYSTERESIS


if TYPE_CHECKING:
    from sqlite3 import sqlite_connection as Connection  # noqa

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def get_sensor_id_state(sensor_id: str) -> bool:
    if not (sensor_data := get_sensor_data(sensor_id=sensor_id)):
        raise SQLiteConnectionErrorException
    current_temp = sensor_data["temp"]

    if not (sensor := get_sensor(sensor_id=sensor_id)):
        raise PostgresConnectionErrorException
    target_temp = sensor["context"]["target_temp"]

    target_temp_min = target_temp - SERVO_TEMP_HYSTERESIS
    target_temp_max = target_temp + SERVO_TEMP_HYSTERESIS

    return target_temp_min < current_temp < target_temp_max


if __name__ == "__main__":
    sqlite_connection = sqlite3.connect(DATABASE_PATH)

    setup_gpio()

    for servo_pin, sensor_id in SERVO_MAP:
        try:
            is_servo_closed = get_sensor_id_state(sensor_id=sensor_id)
            if is_changed := set_gpio_state(gpio_pin=servo_pin, target_state=is_servo_closed):
                logger.info(f"Servo for {sensor_id} state is {'OFF' if is_servo_closed else 'ON'}")

        except SQLiteConnectionErrorException as e:
            logger.error(f"Cannot retrieve data for sensor {sensor_id}")
            exit(e.exit_code)

        except PostgresConnectionErrorException as e:
            logger.error(f"Cannot retrieve sensor {sensor_id}")
            exit(e.exit_code)
