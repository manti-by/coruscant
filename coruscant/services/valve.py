import logging.config
import time

import RPi.GPIO as GPIO

from coruscant.services.gpio import set_gpio_state
from coruscant.settings import (
    LOGGING,
    VALVE_ACT_TIMEOUT,
)


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def update_valve_state(valve_pin: int) -> bool:
    try:
        logger.info(f"Setting valve #{valve_pin} to HIGH")
        set_gpio_state(gpio_pin=valve_pin, target_state=GPIO.HIGH)

        time.sleep(VALVE_ACT_TIMEOUT)

        set_gpio_state(gpio_pin=valve_pin, target_state=GPIO.LOW)
        logger.info(f"Successfully set valve #{valve_pin} to LOW")

        return True

    except RuntimeError as e:
        logger.exception(f"GPIO error: {e}")

    except Exception as e:
        logger.exception(e)

    return False
