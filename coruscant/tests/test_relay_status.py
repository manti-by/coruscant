from decimal import Decimal
from unittest import mock

from coruscant.models import Relay
from coruscant.services.redis_bus import update_relay, update_sensor_data


class TestRelayStatus:
    @mock.patch("coruscant.services.redis_bus.publish_message")
    @mock.patch("coruscant.services.redis_bus.set_relay_state")
    def test_update_relay(self, mock_set_relay_state, mock_publish_message):
        mock_set_relay_state.return_value = True
        mock_publish_message.return_value = True

        result = update_relay(relay=Relay(relay_id="test_relay", state="ON"))

        assert result is True
        mock_publish_message.assert_called_once()

    @mock.patch("coruscant.services.redis_bus.publish_message")
    def test_update_sensor_data(self, mock_publish_message):
        mock_publish_message.return_value = True

        result = update_sensor_data(sensor_id="test_sensor", temp=Decimal("10"))

        assert result is True
        mock_publish_message.assert_called_once()
