import sqlite3
from unittest import mock

import pytest
from redis.exceptions import RedisError

from ..settings import BASE_DIR, DATABASE_PATH


class MockKafkaError(Exception):
    pass


class MockRedisError(RedisError):
    pass


@pytest.fixture(scope="session", autouse=True)
def mock_kafka_producer():
    import coruscant.services.kafka as kafka_module

    mock_producer_instance = mock.MagicMock()

    original_kafka_producer = kafka_module.KafkaProducer
    original_kafka_error = kafka_module.KafkaError

    kafka_module.KafkaProducer = lambda *a, **k: mock_producer_instance
    kafka_module.KafkaError = MockKafkaError

    yield mock_producer_instance

    kafka_module.KafkaProducer = original_kafka_producer
    kafka_module.KafkaError = original_kafka_error


@pytest.fixture(scope="session")
def mock_redis():
    import coruscant.services.redis_bus as redis_module

    mock_redis_instance = mock.MagicMock()
    mock_redis_class = mock.MagicMock()
    mock_redis_class.from_url.return_value = mock_redis_instance

    original_redis = redis_module.Redis
    original_redis_error = redis_module.RedisError

    redis_module.Redis = mock_redis_class
    redis_module.RedisError = MockRedisError

    yield mock_redis_instance

    redis_module.Redis = original_redis
    redis_module.RedisError = original_redis_error


@pytest.fixture(scope="session", autouse=True)
def db_connection():
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        with open(BASE_DIR / "utils" / "database.sql") as f:
            create_table_query = f.read()
        connection.cursor().execute(create_table_query)
    except sqlite3.Error:
        pass

    yield connection


@pytest.fixture(scope="function", autouse=True)
def clear_tables(db_connection):
    """This fixture will be executed after every test, clearing the given table."""
    yield
    db_connection.cursor().execute("DELETE FROM data;")
    db_connection.commit()
