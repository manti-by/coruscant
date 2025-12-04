from __future__ import annotations

import logging
import logging.config
import sqlite3
from typing import TYPE_CHECKING

from apollo.services.database import get_latest_sensors_data
from apollo.services.gpio import close_gpio, set_gpio_state, setup_gpio
from apollo.settings import DATABASE_PATH, LOGGING, SERVO_MAP, SERVO_TEMP_HYSTERESIS


if TYPE_CHECKING:
    from sqlite3 import connection as Connection  # noqa

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def get_sensor_id_state(connection: Connection, sensor_id: str) -> bool:
    if not (sensor_data := get_latest_sensors_data(connection=connection, sensor_ids=[sensor_id])):
        logger.error(f"Cannot retrieve data for sensor {sensor_id}")
        exit(2)

    current_temp = sensor_data["temp"]
    target_temp = sensor_data["target_temp"]

    target_temp_min = target_temp - SERVO_TEMP_HYSTERESIS
    target_temp_max = target_temp + SERVO_TEMP_HYSTERESIS

    return target_temp_min < current_temp < target_temp_max


if __name__ == "__main__":
    connection = sqlite3.connect(DATABASE_PATH)

    setup_gpio()

    for servo_pin, sensor_id in SERVO_MAP:
        is_servo_closed = get_sensor_id_state(connection=connection, sensor_id=sensor_id)
        if is_changed := set_gpio_state(gpio_pin=servo_pin, target_state=is_servo_closed):
            logger.info(f"Servo for {sensor_id} state is {'OFF' if is_servo_closed else 'ON'}")

    close_gpio()
