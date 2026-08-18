import json
import sys
from unittest import mock


mock_gpio = mock.MagicMock()
mock_gpio.HIGH = 1
mock_gpio.LOW = 0
sys.modules["RPi"] = mock.MagicMock()
sys.modules["RPi.GPIO"] = mock_gpio

from coruscant.consumer import RELAY_MAP, consume


def create_mock_pubsub(message_bytes):
    mock_pubsub = mock.MagicMock()
    mock_pubsub.listen.return_value = iter([{"type": "message", "data": message_bytes}])
    return mock_pubsub


def mock_redis_pubsub(message_bytes):
    mock_pubsub = create_mock_pubsub(message_bytes)
    return mock.patch(
        "coruscant.consumer.Redis.from_url",
        return_value=mock.MagicMock(pubsub=mock.MagicMock(return_value=mock_pubsub)),
    )


def envelope(relay_id, target_state):
    return json.dumps({"type": "RELAY_STATE_UPDATE", "data": {"relay_id": relay_id, "target_state": target_state}})


class TestConsumer:
    @mock.patch("coruscant.consumer.set_gpio_state")
    @mock.patch("coruscant.consumer.logger")
    def test_consume__valid_message_valve_open(self, mock_logger, mock_set_gpio):
        mock_set_gpio.return_value = True

        with mock_redis_pubsub(envelope("VALVE-OPEN", "ON").encode()):
            consume()

        mock_set_gpio.assert_called_once()
        _, kwargs = mock_set_gpio.call_args
        assert kwargs["gpio_pin"] == 15
        mock_logger.info.assert_called_with("Relay #VALVE-OPEN state set to ON")

    @mock.patch("coruscant.consumer.set_gpio_state")
    @mock.patch("coruscant.consumer.logger")
    def test_consume__valid_message_pump_off(self, mock_logger, mock_set_gpio):
        mock_set_gpio.return_value = True

        with mock_redis_pubsub(envelope("PUMP-WF-2", "OFF").encode()):
            consume()

        mock_set_gpio.assert_called_once()
        _, kwargs = mock_set_gpio.call_args
        assert kwargs["gpio_pin"] == 12
        mock_logger.info.assert_called_with("Relay #PUMP-WF-2 state set to OFF")

    @mock.patch("coruscant.consumer.set_gpio_state")
    @mock.patch("coruscant.consumer.logger")
    def test_consume__already_in_target_state(self, mock_logger, mock_set_gpio):
        mock_set_gpio.return_value = False

        with mock_redis_pubsub(envelope("VALVE-CLOSED", "ON").encode()):
            consume()

        mock_set_gpio.assert_called_once()
        _, kwargs = mock_set_gpio.call_args
        assert kwargs["gpio_pin"] == 16
        mock_logger.debug.assert_called_with("Relay #VALVE-CLOSED already in a target state")

    @mock.patch("coruscant.consumer.logger")
    def test_consume__invalid_json(self, mock_logger):
        with mock_redis_pubsub(b"not valid json"):
            consume()

        mock_logger.exception.assert_called_once()
        call_args = mock_logger.exception.call_args[0][0]
        assert "Failed to decode JSON" in call_args

    @mock.patch("coruscant.consumer.logger")
    def test_consume__missing_relay_id(self, mock_logger):
        message = json.dumps({"type": "RELAY_STATE_UPDATE", "data": {"target_state": "ON"}})

        with mock_redis_pubsub(message.encode()):
            consume()

        mock_logger.exception.assert_called_once()
        call_args = mock_logger.exception.call_args[0][0]
        assert "Missing required field" in call_args

    @mock.patch("coruscant.consumer.logger")
    def test_consume__missing_target_state(self, mock_logger):
        message = json.dumps({"type": "RELAY_STATE_UPDATE", "data": {"relay_id": "VALVE-OPEN"}})

        with mock_redis_pubsub(message.encode()):
            consume()

        mock_logger.exception.assert_called_once()
        call_args = mock_logger.exception.call_args[0][0]
        assert "Missing required field" in call_args

    @mock.patch("coruscant.consumer.logger")
    def test_consume__unknown_relay_id(self, mock_logger):
        with mock_redis_pubsub(envelope("unknown_relay", "ON").encode()):
            consume()

        mock_logger.exception.assert_called_once_with("Unknown relay_id: unknown_relay")


class TestRelayMap:
    def test_relay_map_contains_valves(self):
        assert "VALVE-OPEN" in RELAY_MAP
        assert "VALVE-CLOSED" in RELAY_MAP

    def test_relay_map_contains_pumps(self):
        assert "PUMP-WF-2" in RELAY_MAP
        assert "PUMP-RD" in RELAY_MAP

    def test_relay_map_contains_servos(self):
        assert "SERVO-WR" in RELAY_MAP
        assert "SERVO-GR" in RELAY_MAP
