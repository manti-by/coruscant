import logging.config
from datetime import datetime
import RPi.GPIO as GPIO
from zoneinfo import ZoneInfo

from coruscant.services.database import get_relay
from coruscant.services.gpio import close_gpio, set_gpio_state, setup_gpio
from coruscant.settings import (
    LOGGING,
    RD_PUMP_PIN,
    WF_PUMP_PIN,
)


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

now = datetime.now(ZoneInfo("Europe/Minsk"))
day, hour = now.strftime("%w"), now.strftime("%H")


def get_target_state(relay_id: str) -> GPIO.LOW | GPIO.HIGH:
    """
        Relays have inverted logic for its states
        if pump is ON you need to set LOW GPIO state
    """
    relay = get_relay(relay_id=relay_id)
    return  GPIO.LOW if relay["context"]["schedule"][day][hour] else GPIO.HIGH


if __name__ == "__main__":
    setup_gpio()

    if is_changed := set_gpio_state(gpio_pin=WF_PUMP_PIN, target_state=get_target_state("PUMP-WF-2")):
        logger.info(f"Water floor pump is {'ON' if is_wf_pump_on else 'OFF'}")

    if is_changed := set_gpio_state(gpio_pin=RD_PUMP_PIN, target_state=get_target_state("PUMP-RD")):
        logger.info(f"Radiators pump is {'ON' if is_rd_pump_on else 'OFF'}")

    close_gpio()
