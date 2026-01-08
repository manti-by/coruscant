import logging.config
from datetime import datetime
from zoneinfo import ZoneInfo

import RPi.GPIO as GPIO
from psycopg2 import Error as Psycopg2Error

from coruscant.services.api import get_relay_state, update_relay_state
from coruscant.services.gpio import set_gpio_state, setup_gpio
from coruscant.settings import (
    LOGGING,
    RD_PUMP_ID,
    RD_PUMP_PIN,
    WF_PUMP_ID,
    WF_PUMP_PIN,
)


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

now = datetime.now(ZoneInfo("Europe/Minsk"))
day, hour = now.strftime("%w"), now.strftime("%H")


def check_pump_relay(relay_id: str, relay_pin: int) -> bool:
    try:
        if not (state := get_relay_state(relay_id=relay_id)):
            return False

        target_state = GPIO.HIGH if state == "ON" else GPIO.LOW  # noqa
        if set_gpio_state(gpio_pin=relay_pin, target_state=target_state):
            update_relay_state(relay_id=relay_id, state=state)
            logger.info(f"Relay #{relay_id} state set to {state}")
        return True

    except Psycopg2Error as e:
        logger.error(f"Database error: {e}")

    except RuntimeError as e:
        logger.error(f"GPIO error: {e}")

    except Exception as e:
        logger.critical(e)
    return False


if __name__ == "__main__":
    logger.info("Checking pumps state")
    setup_gpio()

    for pump_id, pump_pin in ((WF_PUMP_ID, WF_PUMP_PIN), (RD_PUMP_ID, RD_PUMP_PIN)):
        # If a result is False fallback to ON state
        if not check_pump_relay(relay_id=pump_id, relay_pin=pump_pin):
            set_gpio_state(gpio_pin=pump_pin, target_state=GPIO.HIGH)
