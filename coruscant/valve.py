import logging.config
import time
from decimal import Decimal

import RPi.GPIO as GPIO
from pi1wire import FailedToChangeResolutionException, InvalidCRCException, NotFoundSensorException, Pi1Wire, Resolution

from coruscant.exceptions import TempReadErrorException
from coruscant.services.gpio import set_gpio_state, setup_gpio
from coruscant.settings import (
    LOGGING,
    VALVE_ACT_TIMEOUT,
    VALVE_MAP,
    VALVE_SENSOR_ID,
    VALVE_TEMP_HYSTERESIS,
)


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

# TODO: Read from a database
TARGET_TEMP = Decimal("27.0")


def read_temperature(sensor_id: str) -> Decimal:
    try:
        wire = Pi1Wire()
        sensor = wire.find(sensor_id)

        sensor.change_resolution(resolution=Resolution.X0_25)
        return Decimal(round(sensor.get_temperature(), 2))

    except (
        NotFoundSensorException,
        FailedToChangeResolutionException,
        InvalidCRCException,
        OSError,
    ) as e:
        raise TempReadErrorException from e


def update_valve_state(valve_pin: int) -> bool:
    try:
        logger.info(f"Setting valve #{valve_pin} to HIGH")
        set_gpio_state(gpio_pin=valve_pin, target_state=GPIO.HIGH)

        time.sleep(VALVE_ACT_TIMEOUT)

        logger.info(f"Successfully set valve #{valve_pin} to LOW")
        set_gpio_state(gpio_pin=valve_pin, target_state=GPIO.LOW)

        return True

    except RuntimeError as e:
        logger.exception(f"GPIO error: {e}")

    except Exception as e:
        logger.exception(e)

    return False


if __name__ == "__main__":
    setup_gpio()

    try:
        temp = read_temperature(sensor_id=VALVE_SENSOR_ID)
        logger.info(f"Temperature: {temp:.2f}°C")
    except TempReadErrorException as e:
        logger.error(f"Temperature sensor #{VALVE_SENSOR_ID} read error")
        exit(e.exit_code)

    valve_id_map = {v: k for k, v in VALVE_MAP.items()}
    if temp < TARGET_TEMP - VALVE_TEMP_HYSTERESIS:
        update_valve_state(valve_pin=valve_id_map["VALVE-OPEN"])

    elif temp > TARGET_TEMP + VALVE_TEMP_HYSTERESIS:
        update_valve_state(valve_pin=valve_id_map["VALVE-CLOSED"])
