from unittest import mock

from coruscant.services.relay_status import get_relay_state, update_relay_state


class TestRelayStatus:
    @mock.patch("coruscant.services.relay_status.send_message")
    @mock.patch("coruscant.services.relay_status.logger")
    def test_get_relay_state__returns_none(self, mock_logger, mock_send_message):
        state = get_relay_state(relay_id="test_relay")

        assert state is None
        mock_send_message.assert_not_called()
        assert mock_logger.info.call_count == 1
        assert "Getting relay state for test_relay is no longer supported via API" in mock_logger.info.call_args[0][0]

    @mock.patch("coruscant.services.relay_status.send_message")
    @mock.patch("coruscant.services.relay_status.logger")
    def test_update_relay_state__success(self, mock_logger, mock_send_message):
        mock_send_message.return_value = True

        result = update_relay_state(relay_id="test_relay", state="ON")

        assert result is True
        mock_send_message.assert_called_once_with(
            topic="odin", message={"relay_id": "test_relay", "state": "ON", "timestamp": mock.ANY}, key="test_relay"
        )

    @mock.patch("coruscant.services.relay_status.send_message")
    @mock.patch("coruscant.services.relay_status.logger")
    def test_update_relay_state__failed(self, mock_logger, mock_send_message):
        mock_send_message.return_value = False

        result = update_relay_state(relay_id="test_relay", state="OFF")

        assert result is False
        mock_send_message.assert_called_once_with(
            topic="odin", message={"relay_id": "test_relay", "state": "OFF", "timestamp": mock.ANY}, key="test_relay"
        )
