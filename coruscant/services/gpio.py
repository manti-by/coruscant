import logging.config

import RPi.GPIO as GPIO

from coruscant.settings import LOGGING


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def setup_gpio() -> None:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)


def set_gpio_state(gpio_pin: int, target_state: GPIO.LOW | GPIO.HIGH) -> bool:
    GPIO.setup(gpio_pin, GPIO.OUT)
    logger.debug(f"GPIO #{gpio_pin} target state = {target_state}")

    current_state = GPIO.input(gpio_pin)
    logger.debug(f"GPIO #{gpio_pin} current state = {current_state}")

    if current_state != target_state:
        logger.debug(f"Set GPIO #{gpio_pin} state to {target_state}")
        GPIO.output(gpio_pin, target_state)
        return True
    return False


def close_gpio() -> None:
    GPIO.cleanup()
