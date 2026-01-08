import logging.config

import RPi.GPIO as GPIO

from coruscant.services.gpio import set_gpio_state, setup_gpio
from coruscant.services.relay import check_relay_state
from coruscant.settings import LOGGING, PUMP_MAP


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("Checking pumps state")
    setup_gpio()

    for pump_pin, pump_id in PUMP_MAP.items():
        # If a result is False fallback to ON state
        if not check_relay_state(relay_id=pump_id, relay_pin=pump_pin):
            set_gpio_state(gpio_pin=pump_pin, target_state=GPIO.HIGH)
