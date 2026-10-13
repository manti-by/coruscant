from unittest import mock

from requests.exceptions import RequestException

from coruscant.models import Relay
from coruscant.services.api import get_relay
from coruscant.settings import API_TOKEN, API_URL


class TestAPI:
    @mock.patch("coruscant.services.api.requests")
    @mock.patch("coruscant.services.api.logger")
    def test_get_relay__success(self, mock_logger, mock_requests):
        mock_response = mock.Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"target_state": "ON", "mode": "BASIC"}
        mock_requests.get.return_value = mock_response

        relay = get_relay(relay_id="relay_id")

        assert relay == Relay(relay_id="relay_id", state="ON", mode="BASIC")
        mock_requests.get.assert_called_once_with(
            f"{API_URL}/relays/relay_id/", headers={"Authorization": f"Token {API_TOKEN}"}, timeout=10
        )
        assert mock_logger.exception.call_count == 0

    @mock.patch("coruscant.services.api.requests")
    @mock.patch("coruscant.services.api.logger")
    def test_get_relay__without_mode(self, mock_logger, mock_requests):
        mock_response = mock.Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"target_state": "OFF"}
        mock_requests.get.return_value = mock_response

        relay = get_relay(relay_id="relay_id")

        assert relay == Relay(relay_id="relay_id", state="OFF")
        assert mock_logger.exception.call_count == 0

    @mock.patch("coruscant.services.api.requests")
    @mock.patch("coruscant.services.api.logger")
    def test_get_relay__failed(self, mock_logger, mock_requests):
        mock_response = mock.Mock()
        mock_response.ok = False
        mock_response.text = "error body"
        mock_requests.get.return_value = mock_response

        relay = get_relay(relay_id="relay_id")

        assert relay is None
        mock_requests.get.assert_called_once_with(
            f"{API_URL}/relays/relay_id/", headers={"Authorization": f"Token {API_TOKEN}"}, timeout=10
        )
        assert mock_logger.exception.call_count == 1

    @mock.patch("coruscant.services.api.requests")
    @mock.patch("coruscant.services.api.logger")
    def test_get_relay__exception(self, mock_logger, mock_requests):
        mock_requests.get.side_effect = RequestException("boom")

        relay = get_relay(relay_id="relay_id")

        assert relay is None
        mock_requests.get.assert_called_once_with(
            f"{API_URL}/relays/relay_id/", headers={"Authorization": f"Token {API_TOKEN}"}, timeout=10
        )
        assert mock_logger.exception.call_count == 1

    @mock.patch("coruscant.services.api.requests")
    @mock.patch("coruscant.services.api.logger")
    def test_get_relay__with_context_success(self, mock_logger, mock_requests):
        mock_response = mock.Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "target_state": "ON",
            "mode": "MIDSEASON",
            "context": {"schedule": {"0": {"11": "on"}}},
        }
        mock_requests.get.return_value = mock_response

        relay = get_relay(relay_id="relay_id")

        assert relay == Relay(relay_id="relay_id", state="ON", mode="MIDSEASON")
        assert mock_logger.exception.call_count == 0

    @mock.patch("coruscant.services.api.requests")
    @mock.patch("coruscant.services.api.logger")
    def test_get_relay__empty_response(self, mock_logger, mock_requests):
        mock_response = mock.Mock()
        mock_response.ok = True
        mock_response.json.return_value = {}
        mock_requests.get.return_value = mock_response

        relay = get_relay(relay_id="relay_id")

        assert relay is None
        assert mock_logger.exception.call_count == 1
        mock_requests.get.assert_called_once_with(
            f"{API_URL}/relays/relay_id/", headers={"Authorization": f"Token {API_TOKEN}"}, timeout=10
        )
