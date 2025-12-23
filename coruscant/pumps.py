import logging.config
from datetime import datetime
from zoneinfo import ZoneInfo

import RPi.GPIO as GPIO
from psycopg2 import Error

from coruscant.services.api import update_relay_state
from coruscant.services.database import get_relay
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


def check_pump_relay(relay_id: str, relay_pin: int):
    relay = get_relay(relay_id=relay_id)
    target_state = GPIO.HIGH if relay["context"]["schedule"][day][hour] else GPIO.LOW  # noqa

    if set_gpio_state(gpio_pin=relay_pin, target_state=target_state):
        state = "ON" if target_state else "OFF"
        update_relay_state(relay_id=relay_id, state=state)
        logger.info(f"Relay #{relay_id} state set to {state}")


if __name__ == "__main__":
    logger.info("Checking pumps state")

    try:
        setup_gpio()

        check_pump_relay(relay_id=WF_PUMP_ID, relay_pin=WF_PUMP_PIN)
        check_pump_relay(relay_id=RD_PUMP_ID, relay_pin=RD_PUMP_PIN)

    except Error as e:
        logger.error(f"Database error: {e}")

    except RuntimeError as e:
        logger.error(f"GPIO error: {e}")

    except Exception as e:
        logger.critical(e)
