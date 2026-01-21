from unittest import mock

from requests.exceptions import RequestException

from coruscant.services.api import get_relay_state, update_relay_state
from coruscant.settings import API_URL


class TestAPI:
    @mock.patch("coruscant.services.api.requests")
    @mock.patch("coruscant.services.api.logger")
    def test_get_relay_state__success(self, mock_logger, mock_requests):
        mock_response = mock.Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"target_state": {"status": "on"}}
        mock_requests.get.return_value = mock_response

        state = get_relay_state(relay_id="relay_id")

        assert state == {"status": "on"}
        mock_requests.get.assert_called_once_with(f"{API_URL}/relays/relay_id/", timeout=10)
        assert mock_logger.error.call_count == 0

    @mock.patch("coruscant.services.api.requests")
    @mock.patch("coruscant.services.api.logger")
    def test_get_relay_state__failed(self, mock_logger, mock_requests):
        mock_response = mock.Mock()
        mock_response.ok = False
        mock_response.text = "error body"
        mock_requests.get.return_value = mock_response

        state = get_relay_state(relay_id="relay_id")

        assert state is None
        mock_requests.get.assert_called_once_with(f"{API_URL}/relays/relay_id/", timeout=10)
        assert mock_logger.error.call_count == 1

    @mock.patch("coruscant.services.api.requests")
    @mock.patch("coruscant.services.api.logger")
    def test_get_relay_state__exception(self, mock_logger, mock_requests):
        mock_requests.get.side_effect = RequestException("boom")

        state = get_relay_state(relay_id="relay_id")

        assert state is None
        mock_requests.get.assert_called_once_with(f"{API_URL}/relays/relay_id/", timeout=10)
        assert mock_logger.error.call_count == 1

    @mock.patch("coruscant.services.api.requests")
    @mock.patch("coruscant.services.api.logger")
    def test_update_relay_state__success(self, mock_logger, mock_requests):
        mock_requests.patch.return_value.ok = True
        mock_requests.patch.return_value.status_code = 200

        update_relay_state(relay_id="relay_id", state="state")
        assert mock_requests.patch.call_count == 1
        assert mock_logger.error.call_count == 0

    @mock.patch("coruscant.services.api.requests")
    @mock.patch("coruscant.services.api.logger")
    def test_update_relay_state__failed(self, mock_logger, mock_requests):
        mock_requests.patch.return_value.ok = False
        mock_requests.patch.return_value.status_code = 400

        update_relay_state(relay_id="relay_id", state="state")
        assert mock_requests.patch.call_count == 1
        assert mock_logger.error.call_count == 1

    @mock.patch("coruscant.services.api.requests")
    @mock.patch("coruscant.services.api.logger")
    def test_get_relay_state__with_context_success(self, mock_logger, mock_requests):
        mock_response = mock.Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "target_state": {"status": "on"},
            "context": {"schedule": {"0": {"11": "on"}}},
        }
        mock_requests.get.return_value = mock_response

        result = get_relay_state(relay_id="relay_id")

        assert result == {"status": "on"}
        assert mock_logger.error.call_count == 0

    @mock.patch("coruscant.services.api.requests")
    @mock.patch("coruscant.services.api.logger")
    def test_get_relay_state__empty_response(self, mock_logger, mock_requests):
        mock_response = mock.Mock()
        mock_response.ok = True
        mock_response.json.return_value = {}
        mock_requests.get.return_value = mock_response

        state = get_relay_state(relay_id="relay_id")

        assert state is None
        mock_requests.get.assert_called_once_with(f"{API_URL}/relays/relay_id/", timeout=10)
