from unittest import mock

import pytest
from redis.exceptions import RedisError


class MockRedisError(RedisError):
    pass


@pytest.fixture(scope="session")
def mock_redis():
    import coruscant.services.redis_bus as redis_module

    mock_redis_instance = mock.MagicMock()
    mock_redis_class = mock.MagicMock()
    mock_redis_class.from_url.return_value = mock_redis_instance

    original_redis = redis_module.Redis
    original_redis_error = redis_module.RedisError

    redis_module.Redis = mock_redis_class
    redis_module.RedisError = MockRedisError  # ty: ignore

    yield mock_redis_instance

    redis_module.Redis = original_redis
    redis_module.RedisError = original_redis_error

