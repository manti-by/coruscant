from decimal import Decimal
from unittest import mock

from coruscant.services.kafka import update_sensor_data
from coruscant.services.relay import update_relay_state


class TestRelayStatus:
    @mock.patch("coruscant.services.kafka.send_message")
    @mock.patch("coruscant.services.relay.logger")
    def test_update_relay_state(self, _mock_logger, mock_send_message):
        mock_send_message.return_value = True

        result = update_relay_state(relay_id="test_relay", state="ON")

        assert result is True
        assert mock_send_message.call_count == 1

    @mock.patch("coruscant.services.kafka.send_message")
    @mock.patch("coruscant.services.relay.logger")
    def test_update_sensor_data(self, _mock_logger, mock_send_message):
        mock_send_message.return_value = True

        result = update_sensor_data(sensor_id="test_sensor", temp=Decimal("10"))

        assert result is True
        assert mock_send_message.call_count == 1
