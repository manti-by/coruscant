import json
import logging.config
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum

from kafka import KafkaProducer
from kafka.errors import KafkaError

from coruscant.settings import KAFKA_SERVERS, KAFKA_TOPIC, LOGGING


class PartitionKey(Enum):
    SENSORS = "sensors"
    RELAYS = "relays"


class MessageType(Enum):
    RELAY_STATE_UPDATE = "RELAY_STATE_UPDATE"
    SENSOR_DATA_UPDATE = "SENSOR_DATA_UPDATE"


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

kafka_producer: KafkaProducer | None = None


def get_producer() -> KafkaProducer:
    global kafka_producer

    if kafka_producer is None:
        try:
            kafka_producer = KafkaProducer(
                bootstrap_servers=KAFKA_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
            )
        except KafkaError as e:
            logger.error(f"Failed to connect to Kafka brokers {KAFKA_SERVERS}: {e}")
            raise
    return kafka_producer


def send_message(topic: str, message: dict, key: str | None = None) -> bool:
    try:
        producer = get_producer()
        future = producer.send(topic, value=message, key=key)
        record_metadata = future.get(timeout=10)

        logger.info(
            f"Message sent to topic {record_metadata.topic} "
            f"partition {record_metadata.partition} offset {record_metadata.offset}"
        )
        return True

    except KafkaError as e:
        logger.error(f"Kafka error: {e}")

    except Exception as e:
        logger.critical(e)

    return False


def update_relay_state(relay_id: str, state: str) -> bool:
    message = {
        "type": MessageType.RELAY_STATE_UPDATE.value,
        "data": {"relay_id": relay_id, "state": state},
        "timestamp": datetime.now(UTC).isoformat(),
    }
    return send_message(topic=KAFKA_TOPIC, key=PartitionKey.RELAYS.value, message=message)


def update_sensor_data(sensor_id: str, temp: Decimal, humidity: int | None = None) -> bool:
    message = {
        "type": MessageType.SENSOR_DATA_UPDATE.value,
        "data": {"sensor_id": sensor_id, "temp": str(temp), "humidity": humidity},
        "timestamp": datetime.now(UTC).isoformat(),
    }
    return send_message(topic=KAFKA_TOPIC, key=PartitionKey.SENSORS.value, message=message)
