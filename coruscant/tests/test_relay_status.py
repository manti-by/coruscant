from decimal import Decimal
from unittest import mock

from coruscant.services.redis_bus import update_sensor_data
from coruscant.services.relay import update_relay_state


class TestRelayStatus:
    @mock.patch("coruscant.services.redis_bus.publish_message")
    @mock.patch("coruscant.services.redis_bus.set_relay_state")
    @mock.patch("coruscant.services.relay.logger")
    def test_update_relay_state(self, _mock_logger, mock_set_relay_state, mock_publish_message):
        mock_set_relay_state.return_value = True
        mock_publish_message.return_value = True

        result = update_relay_state(relay_id="test_relay", state="ON")

        assert result is True
        mock_publish_message.assert_called_once()

    @mock.patch("coruscant.services.redis_bus.publish_message")
    @mock.patch("coruscant.services.relay.logger")
    def test_update_sensor_data(self, _mock_logger, mock_publish_message):
        mock_publish_message.return_value = True

        result = update_sensor_data(sensor_id="test_sensor", temp=Decimal("10"))

        assert result is True
        mock_publish_message.assert_called_once()
