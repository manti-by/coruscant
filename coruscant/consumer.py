import json
import logging.config
import time

import RPi.GPIO as GPIO
from redis import Redis
from redis.exceptions import RedisError

from coruscant.services.gpio import set_gpio_state, setup_gpio
from coruscant.services.redis_bus import update_relay_state
from coruscant.settings import LOGGING, PUMP_MAP, REDIS_RELAYS_CHANNEL, REDIS_URL, SERVO_MAP, VALVE_MAP


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

RELAY_MAP = {
    **{relay_id: pin_id for pin_id, relay_id in VALVE_MAP.items()},
    **{relay_id: pin_id for pin_id, relay_id in PUMP_MAP.items()},
    **{relay_id: pin_id for pin_id, relay_id in SERVO_MAP.items()},
}

VALID_STATES = ("ON", "OFF")
RETRY_DELAY = 1
MAX_RETRY_DELAY = 30


def process_message(message):
    if message.get("type") != "message":
        return

    try:
        data = json.loads(message["data"])
        relay_id = data["data"]["relay_id"]
        state = data["data"]["state"]

        if state not in VALID_STATES:
            logger.error(f"Invalid relay state: {state}")
            return

        if relay_id not in RELAY_MAP:
            logger.exception(f"Unknown relay_id: {relay_id}")
            return

        pin_id = RELAY_MAP[relay_id]
        target_state = GPIO.HIGH if state == "ON" else GPIO.LOW

        if set_gpio_state(gpio_pin=pin_id, target_state=target_state):
            update_relay_state(relay_id=relay_id, state=state)
            logger.info(f"Relay #{relay_id} state set to {state}")
        else:
            logger.debug(f"Relay #{relay_id} already in a target state")

    except json.JSONDecodeError as e:
        logger.exception(f"Failed to decode JSON: {e}")

    except KeyError as e:
        logger.exception(f"Missing required field: {e}")

    except Exception as e:
        logger.exception(e)


def consume():
    setup_gpio()

    retry_delay = RETRY_DELAY
    while True:
        try:
            redis_client = Redis.from_url(REDIS_URL)
            pubsub = redis_client.pubsub()
            pubsub.subscribe(REDIS_RELAYS_CHANNEL)

            retry_delay = RETRY_DELAY
            for message in pubsub.listen():
                if message.get("type") != "message":
                    continue
                process_message(message)

        except RedisError as e:
            logger.error(f"Redis error: {e}")

        logger.warning(f"Reconnecting in {retry_delay}s")
        time.sleep(retry_delay)
        retry_delay = min(retry_delay * 2, MAX_RETRY_DELAY)


if __name__ == "__main__":
    consume()
