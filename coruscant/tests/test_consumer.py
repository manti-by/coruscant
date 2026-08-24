import json
import sys
from contextlib import contextmanager
from unittest import mock

import pytest
from redis.exceptions import RedisError


mock_gpio = mock.MagicMock()
mock_gpio.HIGH = 1
mock_gpio.LOW = 0
mock_rpi = mock.MagicMock()
mock_rpi.GPIO = mock_gpio
sys.modules["RPi"] = mock_rpi
sys.modules["RPi.GPIO"] = mock_gpio

from coruscant.consumer import RELAY_MAP, consume


def create_mock_pubsub(message_bytes):
    mock_pubsub = mock.MagicMock()

    def listen():
        yield {"type": "message", "data": message_bytes}
        raise RedisError("Connection lost")

    mock_pubsub.listen.side_effect = listen
    return mock_pubsub


@contextmanager
def mock_redis_pubsub(message_bytes, sleep_side_effect=KeyboardInterrupt):
    mock_pubsub = create_mock_pubsub(message_bytes)
    with (
        mock.patch(
            "coruscant.consumer.Redis.from_url",
            return_value=mock.MagicMock(pubsub=mock.MagicMock(return_value=mock_pubsub)),
        ),
        mock.patch("coruscant.consumer.time.sleep", side_effect=sleep_side_effect),
    ):
        yield


def envelope(relay_id, state):
    return json.dumps({"type": "RELAY_STATE_UPDATE", "data": {"relay_id": relay_id, "state": state}})


class TestConsumer:
    @mock.patch("coruscant.consumer.set_gpio_state")
    @mock.patch("coruscant.consumer.logger")
    def test_consume__valid_message_valve_open(self, mock_logger, mock_set_gpio):
        mock_set_gpio.return_value = True

        with mock_redis_pubsub(envelope("VALVE-OPEN", "ON").encode()), pytest.raises(KeyboardInterrupt):
            consume()

        mock_set_gpio.assert_called_once()
        _, kwargs = mock_set_gpio.call_args
        assert kwargs["gpio_pin"] == 15
        assert kwargs["target_state"] == 1
        mock_logger.info.assert_called_with("Relay #VALVE-OPEN state set to ON")

    @mock.patch("coruscant.consumer.set_gpio_state")
    @mock.patch("coruscant.consumer.logger")
    def test_consume__valid_message_pump_off(self, mock_logger, mock_set_gpio):
        mock_set_gpio.return_value = True

        with mock_redis_pubsub(envelope("PUMP-WF-2", "OFF").encode()), pytest.raises(KeyboardInterrupt):
            consume()

        mock_set_gpio.assert_called_once()
        _, kwargs = mock_set_gpio.call_args
        assert kwargs["gpio_pin"] == 12
        assert kwargs["target_state"] == 0
        mock_logger.info.assert_called_with("Relay #PUMP-WF-2 state set to OFF")

    @mock.patch("coruscant.consumer.set_gpio_state")
    @mock.patch("coruscant.consumer.logger")
    def test_consume__already_in_target_state(self, mock_logger, mock_set_gpio):
        mock_set_gpio.return_value = False

        with mock_redis_pubsub(envelope("VALVE-CLOSED", "ON").encode()), pytest.raises(KeyboardInterrupt):
            consume()

        mock_set_gpio.assert_called_once()
        _, kwargs = mock_set_gpio.call_args
        assert kwargs["gpio_pin"] == 16
        mock_logger.debug.assert_called_with("Relay #VALVE-CLOSED already in a target state")

    @mock.patch("coruscant.consumer.set_gpio_state")
    @mock.patch("coruscant.consumer.logger")
    def test_consume__invalid_state(self, mock_logger, mock_set_gpio):
        with mock_redis_pubsub(envelope("VALVE-OPEN", "MAYBE").encode()), pytest.raises(KeyboardInterrupt):
            consume()

        mock_set_gpio.assert_not_called()
        mock_logger.error.assert_any_call("Invalid relay state: MAYBE")

    @mock.patch("coruscant.consumer.logger")
    def test_consume__invalid_json(self, mock_logger):
        with mock_redis_pubsub(b"not valid json"), pytest.raises(KeyboardInterrupt):
            consume()

        mock_logger.exception.assert_called_once()
        call_args = mock_logger.exception.call_args[0][0]
        assert "Failed to decode JSON" in call_args

    @mock.patch("coruscant.consumer.logger")
    def test_consume__missing_relay_id(self, mock_logger):
        message = json.dumps({"type": "RELAY_STATE_UPDATE", "data": {"state": "ON"}})

        with mock_redis_pubsub(message.encode()), pytest.raises(KeyboardInterrupt):
            consume()

        mock_logger.exception.assert_called_once()
        call_args = mock_logger.exception.call_args[0][0]
        assert "Missing required field" in call_args

    @mock.patch("coruscant.consumer.logger")
    def test_consume__missing_state(self, mock_logger):
        message = json.dumps({"type": "RELAY_STATE_UPDATE", "data": {"relay_id": "VALVE-OPEN"}})

        with mock_redis_pubsub(message.encode()), pytest.raises(KeyboardInterrupt):
            consume()

        mock_logger.exception.assert_called_once()
        call_args = mock_logger.exception.call_args[0][0]
        assert "Missing required field" in call_args

    @mock.patch("coruscant.consumer.set_gpio_state")
    @mock.patch("coruscant.consumer.logger")
    def test_consume__rejects_flat_payload(self, mock_logger, mock_set_gpio):
        message = json.dumps({"type": "RELAY_STATE_UPDATE", "relay_id": "VALVE-OPEN", "state": "ON"})

        with mock_redis_pubsub(message.encode()), pytest.raises(KeyboardInterrupt):
            consume()

        mock_set_gpio.assert_not_called()
        mock_logger.exception.assert_called_once()
        call_args = mock_logger.exception.call_args[0][0]
        assert "Missing required field" in call_args

    @mock.patch("coruscant.consumer.logger")
    def test_consume__unknown_relay_id(self, mock_logger):
        with mock_redis_pubsub(envelope("unknown_relay", "ON").encode()), pytest.raises(KeyboardInterrupt):
            consume()

        mock_logger.exception.assert_called_once_with("Unknown relay_id: unknown_relay")

    @mock.patch("coruscant.consumer.logger")
    def test_consume__redis_error_reconnects_with_backoff(self, mock_logger):
        sleep_side_effect = [None, KeyboardInterrupt]

        with (
            mock_redis_pubsub(envelope("VALVE-OPEN", "ON").encode(), sleep_side_effect=sleep_side_effect),
            pytest.raises(KeyboardInterrupt),
        ):
            consume()

        mock_logger.error.assert_called_with("Redis error: Connection lost")


class TestNonMessageEvents:
    @mock.patch("coruscant.consumer.process_message")
    @mock.patch("coruscant.consumer.logger")
    def test_consume__skips_non_message_events(self, mock_logger, mock_process_message):
        messages = [{"type": "subscribe"}, {"type": "message", "data": b"{}"}]
        mock_pubsub = mock.MagicMock()

        def listen():
            yield from messages
            raise RedisError("Connection lost")

        mock_pubsub.listen.side_effect = listen

        with (
            mock.patch(
                "coruscant.consumer.Redis.from_url",
                return_value=mock.MagicMock(pubsub=mock.MagicMock(return_value=mock_pubsub)),
            ),
            mock.patch("coruscant.consumer.time.sleep", side_effect=[KeyboardInterrupt]),
            pytest.raises(KeyboardInterrupt),
        ):
            consume()

        mock_process_message.assert_called_once_with(messages[1])


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
