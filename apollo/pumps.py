import logging
import logging.config
from datetime import datetime
from zoneinfo import ZoneInfo

from apollo.services.gpio import close_gpio, set_gpio_state, setup_gpio
from apollo.settings import (
    LOGGING,
    RD_PUMP_PIN,
    WF_PUMP_PIN,
)


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

# TODO: Read from a database
PUMPS_SCHEDULE = {d: {h: 8 <= h <= 22 for h in range(24)} for d in range(6)}


if __name__ == "__main__":
    setup_gpio()

    now = datetime.now(ZoneInfo("Europe/Minsk"))
    day, hour = int(now.strftime("%w")), int(now.strftime("%H"))
    is_pump_on = PUMPS_SCHEDULE[day][hour]

    if is_changed := set_gpio_state(gpio_pin=WF_PUMP_PIN, target_state=is_pump_on):
        logger.info(f"Water floor pump is {'ON' if is_pump_on else 'OFF'}")

    if is_changed := set_gpio_state(gpio_pin=RD_PUMP_PIN, target_state=is_pump_on):
        logger.info(f"Radiators pump is {'ON' if is_pump_on else 'OFF'}")

    close_gpio()
