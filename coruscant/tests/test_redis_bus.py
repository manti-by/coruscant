import json
from decimal import Decimal
from unittest import mock

import pytest
from redis.exceptions import RedisError

from coruscant.services.redis_bus import (
    RELAY_STATE_TTL,
    MessageType,
    publish_message,
    set_relay_state,
    update_relay_state,
    update_sensor_data,
)
from coruscant.settings import REDIS_RELAY_STATE_KEY_PREFIX, REDIS_RELAYS_CHANNEL, REDIS_SENSORS_CHANNEL


class TestRedisBus:
    @mock.patch("coruscant.services.redis_bus.get_redis")
    @mock.patch("coruscant.services.redis_bus.logger")
    def test_publish_message__success(self, mock_logger, mock_get_redis):
        mock_redis_client = mock.Mock()
        mock_redis_client.publish.return_value = 1
        mock_get_redis.return_value = mock_redis_client

        result = publish_message(channel=REDIS_SENSORS_CHANNEL, payload={"relay_id": "test", "state": "ON"})

        assert result is True
        mock_redis_client.publish.assert_called_once_with(
            REDIS_SENSORS_CHANNEL, json.dumps({"relay_id": "test", "state": "ON"})
        )
        assert mock_logger.error.call_count == 0

    @mock.patch("coruscant.services.redis_bus.get_redis")
    @mock.patch("coruscant.services.redis_bus.logger")
    def test_publish_message__redis_error(self, mock_logger, mock_get_redis):
        mock_redis_client = mock.Mock()
        mock_redis_client.publish.side_effect = RedisError("Connection failed")
        mock_get_redis.return_value = mock_redis_client

        result = publish_message(channel=REDIS_SENSORS_CHANNEL, payload={"relay_id": "test", "state": "ON"})

        assert result is False
        mock_redis_client.publish.assert_called_once()
        assert mock_logger.error.call_count == 1
        assert "Redis error: Connection failed" in mock_logger.error.call_args[0][0]

    @mock.patch("coruscant.services.redis_bus.get_redis")
    @mock.patch("coruscant.services.redis_bus.logger")
    def test_publish_message__redis_error_resets_client(self, mock_logger, mock_get_redis):
        import coruscant.services.redis_bus as redis_module

        mock_redis_client = mock.Mock()
        mock_redis_client.publish.side_effect = RedisError("Connection failed")
        mock_get_redis.return_value = mock_redis_client

        original_client = redis_module.redis_client
        redis_module.redis_client = mock_redis_client
        try:
            result = publish_message(channel=REDIS_SENSORS_CHANNEL, payload={"relay_id": "test", "state": "ON"})
            assert result is False
            assert redis_module.redis_client is None
        finally:
            redis_module.redis_client = original_client

    @mock.patch("coruscant.services.redis_bus.get_redis")
    @mock.patch("coruscant.services.redis_bus.logger")
    def test_publish_message__connection_error(self, mock_logger, mock_get_redis):
        mock_redis_client = mock.Mock()
        mock_redis_client.publish.side_effect = ConnectionError("refused")
        mock_get_redis.return_value = mock_redis_client

        result = publish_message(channel=REDIS_SENSORS_CHANNEL, payload={"relay_id": "test", "state": "ON"})

        assert result is False
        mock_redis_client.publish.assert_called_once()
        assert mock_logger.error.call_count == 1
        assert "Redis error: refused" in mock_logger.error.call_args[0][0]

    @mock.patch("coruscant.services.redis_bus.get_redis")
    @mock.patch("coruscant.services.redis_bus.logger")
    def test_publish_message__serialization_error(self, mock_logger, mock_get_redis):
        mock_redis_client = mock.Mock()
        mock_get_redis.return_value = mock_redis_client

        result = publish_message(channel=REDIS_SENSORS_CHANNEL, payload={"relay_id": object()})

        assert result is False
        mock_redis_client.publish.assert_not_called()
        assert mock_logger.error.call_count == 1
        assert "Failed to serialize payload" in mock_logger.error.call_args[0][0]

    @mock.patch("coruscant.services.redis_bus.set_relay_state")
    @mock.patch("coruscant.services.redis_bus.publish_message")
    def test_update_relay_state__publishes_and_sets(self, mock_publish_message, mock_set_relay_state):
        calls = []
        mock_publish_message.side_effect = lambda *a, **k: calls.append("publish") or True
        mock_set_relay_state.side_effect = lambda *a, **k: calls.append("set") or True

        result = update_relay_state(relay_id="VALVE-OPEN", state="ON")

        assert result is True
        assert calls == ["set", "publish"]
        mock_publish_message.assert_called_once()
        channel, envelope = mock_publish_message.call_args[0]
        assert channel == REDIS_RELAYS_CHANNEL
        assert envelope["type"] == MessageType.RELAY_STATE_UPDATE.value
        assert envelope["data"] == {"relay_id": "VALVE-OPEN", "state": "ON"}
        mock_set_relay_state.assert_called_once_with("VALVE-OPEN", envelope)

    @mock.patch("coruscant.services.redis_bus.get_redis")
    @mock.patch("coruscant.services.redis_bus.logger")
    def test_update_relay_state__last_value_set_happens(self, mock_logger, mock_get_redis):
        mock_redis_client = mock.Mock()
        mock_redis_client.publish.return_value = 1
        mock_redis_client.set.return_value = True
        mock_get_redis.return_value = mock_redis_client

        result = update_relay_state(relay_id="VALVE-OPEN", state="ON")

        assert result is True
        mock_redis_client.set.assert_called_once()
        key, value, kwargs = (
            mock_redis_client.set.call_args[0][0],
            mock_redis_client.set.call_args[0][1],
            mock_redis_client.set.call_args[1],
        )
        assert key == f"{REDIS_RELAY_STATE_KEY_PREFIX}VALVE-OPEN"
        assert json.loads(value)["data"] == {"relay_id": "VALVE-OPEN", "state": "ON"}
        assert kwargs == {"ex": RELAY_STATE_TTL}

    @mock.patch("coruscant.services.redis_bus.set_relay_state")
    @mock.patch("coruscant.services.redis_bus.publish_message")
    def test_update_relay_state__returns_false_when_publish_fails(self, mock_publish_message, mock_set_relay_state):
        mock_publish_message.return_value = False
        mock_set_relay_state.return_value = True

        result = update_relay_state(relay_id="VALVE-OPEN", state="ON")

        assert result is False

    @mock.patch("coruscant.services.redis_bus.set_relay_state")
    @mock.patch("coruscant.services.redis_bus.publish_message")
    def test_update_relay_state__does_not_publish_when_set_fails(self, mock_publish_message, mock_set_relay_state):
        mock_set_relay_state.return_value = False

        result = update_relay_state(relay_id="VALVE-OPEN", state="ON")

        assert result is False
        mock_set_relay_state.assert_called_once()
        mock_publish_message.assert_not_called()

    @mock.patch("coruscant.services.redis_bus.publish_message")
    def test_update_sensor_data(self, mock_publish_message):
        mock_publish_message.return_value = True

        result = update_sensor_data(sensor_id="28000007176e41", temp=Decimal("21.5"))

        assert result is True
        mock_publish_message.assert_called_once()
        channel, envelope = mock_publish_message.call_args[0]
        assert channel == REDIS_SENSORS_CHANNEL
        assert envelope["type"] == MessageType.SENSOR_DATA_UPDATE.value
        assert envelope["data"] == {
            "sensor_id": "28000007176e41",
            "temp": "21.5",
            "value": "21.5",
            "unit": "C",
            "humidity": None,
        }

    @mock.patch("coruscant.services.redis_bus.publish_message")
    def test_update_sensor_data__with_humidity(self, mock_publish_message):
        mock_publish_message.return_value = True

        result = update_sensor_data(sensor_id="28000007176e41", temp=Decimal("21.5"), humidity=42)

        assert result is True
        mock_publish_message.assert_called_once()
        channel, envelope = mock_publish_message.call_args[0]
        assert channel == REDIS_SENSORS_CHANNEL
        assert envelope["data"]["humidity"] == 42


class TestGetRedis:
    @mock.patch("coruscant.services.redis_bus.logger")
    def test_get_redis__passes_socket_timeouts(self, mock_logger):
        import coruscant.services.redis_bus as redis_module

        mock_redis_class = mock.Mock()
        mock_redis_instance = mock.Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_class.from_url.return_value = mock_redis_instance

        original_redis = redis_module.Redis
        original_client = redis_module.redis_client
        redis_module.Redis = mock_redis_class
        redis_module.redis_client = None

        try:
            result = redis_module.get_redis()
            assert result is mock_redis_instance
            _, kwargs = mock_redis_class.from_url.call_args
            assert kwargs["socket_connect_timeout"] == redis_module.REDIS_CONNECT_TIMEOUT
            assert kwargs["socket_timeout"] == redis_module.REDIS_SOCKET_TIMEOUT
        finally:
            redis_module.Redis = original_redis
            redis_module.redis_client = original_client

    @mock.patch("coruscant.services.redis_bus.logger")
    def test_get_redis__connection_error_resets_client(self, mock_logger):
        import coruscant.services.redis_bus as redis_module

        mock_redis_class = mock.Mock()
        mock_redis_instance = mock.Mock()
        mock_redis_instance.ping.side_effect = RedisError("Connection failed")
        mock_redis_class.from_url.return_value = mock_redis_instance

        original_redis = redis_module.Redis
        original_client = redis_module.redis_client
        redis_module.Redis = mock_redis_class
        redis_module.redis_client = None

        try:
            with pytest.raises(RedisError):
                redis_module.get_redis()
            assert redis_module.redis_client is None
            assert mock_logger.error.call_count == 1
        finally:
            redis_module.Redis = original_redis
            redis_module.redis_client = original_client


class TestRedactUrl:
    def test_redact_url__with_credentials(self):
        from coruscant.services.redis_bus import _redact_url

        assert _redact_url("redis://user:secret@localhost:6380/0") == "redis://localhost:6380"

    def test_redact_url__unix_socket(self):
        from coruscant.services.redis_bus import _redact_url

        assert _redact_url("unix:///var/run/redis.sock") == "unix:///var/run/redis.sock"


class TestSetRelayState:
    @mock.patch("coruscant.services.redis_bus.get_redis")
    @mock.patch("coruscant.services.redis_bus.logger")
    def test_set_relay_state__sets_key_with_ttl(self, mock_logger, mock_get_redis):
        mock_redis_client = mock.Mock()
        mock_redis_client.set.return_value = True
        mock_get_redis.return_value = mock_redis_client

        result = set_relay_state(relay_id="VALVE-OPEN", payload={"k": "v"})

        assert result is True
        mock_redis_client.set.assert_called_once_with(
            f"{REDIS_RELAY_STATE_KEY_PREFIX}VALVE-OPEN", json.dumps({"k": "v"}), ex=RELAY_STATE_TTL
        )

    @mock.patch("coruscant.services.redis_bus.get_redis")
    @mock.patch("coruscant.services.redis_bus.logger")
    def test_set_relay_state__redis_error(self, mock_logger, mock_get_redis):
        mock_redis_client = mock.Mock()
        mock_redis_client.set.side_effect = RedisError("Connection failed")
        mock_get_redis.return_value = mock_redis_client

        result = set_relay_state(relay_id="VALVE-OPEN", payload={"k": "v"})

        assert result is False
        mock_redis_client.set.assert_called_once()
        assert mock_logger.error.call_count == 1

    @mock.patch("coruscant.services.redis_bus.get_redis")
    @mock.patch("coruscant.services.redis_bus.logger")
    def test_set_relay_state__redis_error_resets_client(self, mock_logger, mock_get_redis):
        import coruscant.services.redis_bus as redis_module

        mock_redis_client = mock.Mock()
        mock_redis_client.set.side_effect = RedisError("Connection failed")
        mock_get_redis.return_value = mock_redis_client

        original_client = redis_module.redis_client
        redis_module.redis_client = mock_redis_client
        try:
            result = set_relay_state(relay_id="VALVE-OPEN", payload={"k": "v"})
            assert result is False
            assert redis_module.redis_client is None
        finally:
            redis_module.redis_client = original_client

    @mock.patch("coruscant.services.redis_bus.get_redis")
    @mock.patch("coruscant.services.redis_bus.logger")
    def test_set_relay_state__serialization_error(self, mock_logger, mock_get_redis):
        mock_redis_client = mock.Mock()
        mock_get_redis.return_value = mock_redis_client

        result = set_relay_state(relay_id="VALVE-OPEN", payload={"k": object()})

        assert result is False
        mock_redis_client.set.assert_not_called()
        assert mock_logger.error.call_count == 1
        assert "Failed to serialize payload" in mock_logger.error.call_args[0][0]
