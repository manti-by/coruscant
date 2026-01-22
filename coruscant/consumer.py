import json
import logging.config

import RPi.GPIO as GPIO
from kafka import KafkaConsumer

from coruscant.services.gpio import set_gpio_state, setup_gpio
from coruscant.settings import KAFKA_SERVERS, LOGGING, PUMP_MAP, SERVO_MAP, VALVE_MAP


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

RELAY_MAP = {
    **{relay_id: pin_id for pin_id, relay_id in VALVE_MAP.items()},
    **{relay_id: pin_id for pin_id, relay_id in PUMP_MAP.items()},
    **{relay_id: pin_id for pin_id, relay_id in SERVO_MAP.items()},
}


def consume():
    setup_gpio()

    consumer = KafkaConsumer(
        "coruscant", bootstrap_servers=KAFKA_SERVERS, group_id="coruscant", enable_auto_commit=True
    )

    for message in consumer:
        try:
            data = json.loads(message.value)
            relay_id = data["relay_id"]
            target_state = bool(data["target_state"])

            if relay_id not in RELAY_MAP:
                logger.error(f"Unknown relay_id: {relay_id}")
                continue

            pin_id = RELAY_MAP[relay_id]
            state = GPIO.HIGH if target_state else GPIO.LOW

            if set_gpio_state(gpio_pin=pin_id, target_state=state):
                logger.info(f"Relay '{relay_id}' state set to {target_state}")
            else:
                logger.debug(f"Relay '{relay_id}' already in target state")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON: {e}")

        except KeyError as e:
            logger.error(f"Missing required field: {e}")

        except Exception as e:
            logger.critical(e)


if __name__ == "__main__":
    consume()
