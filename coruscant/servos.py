import logging.config

import RPi.GPIO as GPIO

from coruscant.services.gpio import set_gpio_state, setup_gpio
from coruscant.services.relay import check_relay_state
from coruscant.settings import LOGGING, SERVO_MAP


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("Checking servos state")
    setup_gpio()

    for servo_pin, relay_id in SERVO_MAP.items():
        # If a result is False fallback to ON state
        if not check_relay_state(relay_id=relay_id, relay_pin=servo_pin):
            set_gpio_state(gpio_pin=servo_pin, target_state=GPIO.HIGH)
