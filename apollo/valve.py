import logging
import logging.config
import time
from decimal import Decimal

from pi1wire import NotFoundSensorException, Pi1Wire, Resolution

from apollo.services.gpio import close_gpio, set_gpio_state, setup_gpio
from apollo.settings import (
    LOGGING,
    RELAY_COOL_PIN,
    RELAY_HEAT_PIN,
    VALVE_ACT_TIMEOUT,
    VALVE_SENSOR_ID,
    VALVE_TEMP_HYSTERESIS,
)


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

MODE_HEAT, MODE_COOL = "heat", "cool"

# TODO: Read from a database
TARGET_TEMP = Decimal("27.0")


def read_temperature() -> Decimal:
    try:
        wire = Pi1Wire()
        sensor = wire.find(VALVE_SENSOR_ID)
    except NotFoundSensorException:
        logger.error(f"Temperature sensor {VALVE_SENSOR_ID} not found")
        exit(1)

    sensor.change_resolution(resolution=Resolution.X0_25)
    return round(Decimal(str(sensor.get_temperature())))


def set_valve_mode(mode: str) -> None:
    if mode == MODE_HEAT:
        set_gpio_state(gpio_pin=RELAY_HEAT_PIN, target_state=True)
    else:
        set_gpio_state(gpio_pin=RELAY_COOL_PIN, target_state=True)

    logger.info(f"Setting valve mode to {mode}")
    time.sleep(VALVE_ACT_TIMEOUT)
    logger.info(f"Successfully set valve mode to {mode}")

    set_gpio_state(gpio_pin=RELAY_HEAT_PIN, target_state=False)
    set_gpio_state(gpio_pin=RELAY_HEAT_PIN, target_state=False)


if __name__ == "__main__":
    setup_gpio()

    temp = read_temperature()
    logger.info(f"Temperature: {temp:.2f}°C")

    if temp < TARGET_TEMP - VALVE_TEMP_HYSTERESIS:
        set_valve_mode(mode=MODE_HEAT)

    elif temp > TARGET_TEMP + VALVE_TEMP_HYSTERESIS:
        set_valve_mode(mode=MODE_COOL)

    close_gpio()
