from unittest import mock

from coruscant.services.api import update_relay_state


class TestAPI:
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
