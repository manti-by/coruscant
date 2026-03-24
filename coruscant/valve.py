import logging.config

from coruscant.exceptions import TempReadErrorException
from coruscant.services.gpio import setup_gpio
from coruscant.services.kafka import update_relay_state, update_sensor_data
from coruscant.services.sensors import read_temperature
from coruscant.services.valve import update_valve_state
from coruscant.settings import (
    LOGGING,
    VALVE_MAP,
    VALVE_SENSOR_ID,
    VALVE_TARGET_TEMP,
    VALVE_TEMP_HYSTERESIS,
)


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def update_valve(relay_id: str, valve_pin: int):
    update_relay_state(relay_id=relay_id, state="ON")
    if update_valve_state(valve_pin=valve_pin):
        update_relay_state(relay_id=relay_id, state="OFF")


if __name__ == "__main__":
    setup_gpio()

    try:
        temp = read_temperature(sensor_id=VALVE_SENSOR_ID)
        update_sensor_data(sensor_id=VALVE_SENSOR_ID, temp=temp)
        logger.debug(f"Temp for {VALVE_SENSOR_ID}: {temp:.2f} *C")
    except TempReadErrorException as e:
        exit(e.exit_code)

    valve_id_map = {v: k for k, v in VALVE_MAP.items()}
    if temp < VALVE_TARGET_TEMP - VALVE_TEMP_HYSTERESIS:
        update_valve(relay_id="VALVE-OPEN", valve_pin=valve_id_map["VALVE-OPEN"])

    elif temp > VALVE_TARGET_TEMP + VALVE_TEMP_HYSTERESIS:
        update_valve(relay_id="VALVE-CLOSED", valve_pin=valve_id_map["VALVE-CLOSED"])
