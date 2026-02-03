import json
import logging.config
from datetime import UTC, datetime

from kafka import KafkaProducer
from kafka.errors import KafkaError

from coruscant.settings import KAFKA_SERVERS, LOGGING


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda k: k.encode("utf-8") if k else None,
)


def send_message(topic: str, message: dict, key: str | None = None) -> bool:
    try:
        future = producer.send(topic, value=message, key=key)
        record_metadata = future.get(timeout=10)
        producer.close()

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
        "relay_id": relay_id,
        "state": state,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    return send_message(topic="odin", key=relay_id, message=message)
