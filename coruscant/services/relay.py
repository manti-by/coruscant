import logging.config

import RPi.GPIO as GPIO

from coruscant.services.gpio import set_gpio_state
from coruscant.services.relay_status import get_relay_state, update_relay_state
from coruscant.settings import LOGGING


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def check_relay_state(relay_id: str, relay_pin: int) -> bool:
    try:
        if not (state := get_relay_state(relay_id=relay_id)):
            return False

        target_state = GPIO.HIGH if state == "ON" else GPIO.LOW  # noqa
        if set_gpio_state(gpio_pin=relay_pin, target_state=target_state):
            update_relay_state(relay_id=relay_id, state=state)
            logger.info(f"Relay #{relay_id} state set to {state}")
        return True

    except RuntimeError as e:
        logger.error(f"GPIO error: {e}")

    except Exception as e:
        logger.critical(e)

    return False
