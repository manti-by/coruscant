import logging.config
from datetime import datetime
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


if __name__ == "__main__":
    setup_gpio()

    now = datetime.now(ZoneInfo("Europe/Minsk"))
    day, hour = now.strftime("%w"), now.strftime("%H")

    # Relays have inverted logic for its states
    # if pump is ON you need to set LOW GPIO state
    relay = get_relay(relay_id="PUMP-WF-2")
    is_rd_pump_on = relay["context"]["schedule"][day][hour]
    target_state = not is_rd_pump_on

    if is_changed := set_gpio_state(gpio_pin=WF_PUMP_PIN, target_state=target_state):
        logger.info(f"Water floor pump is {'ON' if is_rd_pump_on else 'OFF'}")

    relay = get_relay(relay_id="PUMP-RD")
    is_wf_pump_on = relay["context"]["schedule"][day][hour]
    target_state = not is_rd_pump_on

    if is_changed := set_gpio_state(gpio_pin=RD_PUMP_PIN, target_state=target_state):
        logger.info(f"Radiators pump is {'ON' if is_wf_pump_on else 'OFF'}")

    close_gpio()
