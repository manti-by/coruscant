import logging.config
import time
from itertools import chain

import RPi.GPIO as GPIO

from coruscant.services.gpio import close_gpio, set_gpio_state, setup_gpio
from coruscant.settings import LOGGING, PUMP_MAP, SERVO_MAP


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def check_relays(duration: float = 1) -> None:
    """Turn each pump and servo relay on, then off, one at a time."""
    setup_gpio()

    try:
        for relay_pin, relay_id in chain(PUMP_MAP.items(), SERVO_MAP.items()):
            logger.info(f"Testing relay #{relay_id}")
            try:
                set_gpio_state(gpio_pin=relay_pin, target_state=GPIO.HIGH)
                time.sleep(duration)
            finally:
                set_gpio_state(gpio_pin=relay_pin, target_state=GPIO.LOW)
    finally:
        close_gpio()


if __name__ == "__main__":
    check_relays()
