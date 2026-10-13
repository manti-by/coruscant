import logging.config

import RPi.GPIO as GPIO

from coruscant.services.api import get_relay
from coruscant.services.gpio import set_gpio_state
from coruscant.services.redis_bus import update_relay
from coruscant.settings import LOGGING


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def check_relay_state(relay_id: str, relay_pin: int) -> bool:
    try:
        relay = get_relay(relay_id=relay_id)
        if not relay or not relay.state:
            logger.info(f"Get relay #{relay_id} state failed")
            return False

        target_state = GPIO.LOW if relay.state == "ON" else GPIO.HIGH
        if set_gpio_state(gpio_pin=relay_pin, target_state=target_state):
            update_relay(relay=relay)
            logger.info(f"Relay #{relay_id} state set to {relay.state}, mode {relay.mode}")
        return True

    except RuntimeError as e:
        logger.exception(f"GPIO error: {e}")

    except Exception as e:
        logger.exception(e)

    return False
