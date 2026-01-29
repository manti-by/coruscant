import json
import logging.config

from kafka import KafkaProducer
from kafka.errors import KafkaError

from coruscant.settings import KAFKA_SERVERS, LOGGING


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

producer = None


def get_producer() -> KafkaProducer:
    global producer
    if producer is None:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
        )
    return producer


def send_message(topic: str, message: dict, key: str | None = None) -> bool:
    try:
        prod = get_producer()
        future = prod.send(topic, value=message, key=key)
        record_metadata = future.get(timeout=10)

        logger.info(
            f"Message sent to topic {record_metadata.topic} "
            f"partition {record_metadata.partition} offset {record_metadata.offset}"
        )
        return True

    except KafkaError as e:
        logger.error(f"Kafka error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error sending message: {e}")
    return False


def close_producer():
    global producer
    if producer is not None:
        producer.close()
        producer = None
