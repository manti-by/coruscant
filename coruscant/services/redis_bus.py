import json
import logging
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from urllib.parse import urlsplit

from redis import Redis
from redis.exceptions import RedisError

from coruscant.settings import (
    REDIS_RELAY_STATE_KEY_PREFIX,
    REDIS_RELAYS_CHANNEL,
    REDIS_SENSORS_CHANNEL,
    REDIS_URL,
)


class PartitionKey(Enum):
    SENSORS = "sensors"
    RELAYS = "relays"


class MessageType(Enum):
    RELAY_STATE_UPDATE = "RELAY_STATE_UPDATE"
    SENSOR_DATA_UPDATE = "SENSOR_DATA_UPDATE"


RELAY_STATE_TTL = 24 * 60 * 60
REDIS_CONNECT_TIMEOUT = 5
REDIS_SOCKET_TIMEOUT = 5


def _redact_url(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.hostname:
        return f"{parsed.scheme}://{parsed.hostname}:{parsed.port or 6379}"
    return f"{parsed.scheme}://{parsed.path or parsed.netloc}"


logger = logging.getLogger(__name__)

redis_client: Redis | None = None


def get_redis() -> Redis:
    global redis_client

    if redis_client is None:
        try:
            redis_client = Redis.from_url(
                REDIS_URL,
                socket_connect_timeout=REDIS_CONNECT_TIMEOUT,
                socket_timeout=REDIS_SOCKET_TIMEOUT,
            )
            redis_client.ping()
        except (RedisError, ConnectionError) as e:
            redis_client = None
            logger.error(f"Failed to connect to Redis {_redact_url(REDIS_URL)}: {e}")
            raise
    return redis_client


def _handle_redis_error(error: Exception) -> bool:
    global redis_client
    redis_client = None
    logger.error(f"Redis error: {error}")
    return False


def publish_message(channel: str, payload: dict) -> bool:
    try:
        message = json.dumps(payload)
    except (TypeError, ValueError) as e:
        logger.error(f"Failed to serialize payload: {e}")
        return False

    try:
        client = get_redis()
        client.publish(channel, message)
        logger.info(f"Published message to channel {channel}")
        return True

    except (RedisError, ConnectionError) as e:
        return _handle_redis_error(e)


def set_relay_state(relay_id: str, payload: dict) -> bool:
    try:
        message = json.dumps(payload)
    except (TypeError, ValueError) as e:
        logger.error(f"Failed to serialize payload: {e}")
        return False

    try:
        client = get_redis()
        key = f"{REDIS_RELAY_STATE_KEY_PREFIX}{relay_id}"
        client.set(key, message, ex=RELAY_STATE_TTL)
        logger.info(f"Persisted relay state for {relay_id}")
        return True

    except (RedisError, ConnectionError) as e:
        return _handle_redis_error(e)


def update_relay_state(relay_id: str, state: str) -> bool:
    envelope = {
        "type": MessageType.RELAY_STATE_UPDATE.value,
        "data": {"relay_id": relay_id, "state": state},
        "timestamp": datetime.now(UTC).isoformat(),
    }
    # Persist first so consumers never observe an event for unpersisted state.
    if not set_relay_state(relay_id, envelope):
        return False
    return publish_message(REDIS_RELAYS_CHANNEL, envelope)


def update_sensor_data(sensor_id: str, temp: Decimal, humidity: int | None = None) -> bool:
    envelope = {
        "type": MessageType.SENSOR_DATA_UPDATE.value,
        "data": {
            "sensor_id": sensor_id,
            "temp": str(temp),
            "value": str(temp),
            "unit": "C",
            "humidity": humidity,
        },
        "timestamp": datetime.now(UTC).isoformat(),
    }
    return publish_message(REDIS_SENSORS_CHANNEL, envelope)
