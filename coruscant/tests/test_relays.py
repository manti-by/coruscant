import sys
from unittest import mock


mock_gpio = mock.MagicMock()
sys.modules["RPi"] = mock.MagicMock()
sys.modules["RPi.GPIO"] = mock_gpio

from coruscant.models import Relay
from coruscant.services.relay import check_relay_state


class TestCheckPumpRelay:
    @mock.patch("coruscant.services.relay.get_relay")
    @mock.patch("coruscant.services.relay.set_gpio_state")
    @mock.patch("coruscant.services.relay.update_relay")
    @mock.patch("coruscant.services.relay.logger")
    def test_check_pump_relay__success_on(self, mock_logger, mock_update, mock_set, mock_get):
        relay = Relay(relay_id="pump_1", state="ON", mode="FALLBACK")
        mock_get.return_value = relay
        mock_set.return_value = True

        result = check_relay_state(relay_id="pump_1", relay_pin=11)

        assert result is True
        mock_get.assert_called_once_with(relay_id="pump_1")
        mock_set.assert_called_once()
        mock_update.assert_called_once_with(relay=relay)
        mock_logger.exception.assert_not_called()

    @mock.patch("coruscant.services.relay.get_relay")
    @mock.patch("coruscant.services.relay.set_gpio_state")
    @mock.patch("coruscant.services.relay.update_relay")
    @mock.patch("coruscant.services.relay.logger")
    def test_check_pump_relay__success_off(self, mock_logger, mock_update, mock_set, mock_get):
        relay = Relay(relay_id="pump_2", state="OFF")
        mock_get.return_value = relay
        mock_set.return_value = True

        result = check_relay_state(relay_id="pump_2", relay_pin=12)

        assert result is True
        mock_get.assert_called_once_with(relay_id="pump_2")
        mock_set.assert_called_once()
        mock_update.assert_called_once_with(relay=relay)
        mock_logger.exception.assert_not_called()

    @mock.patch("coruscant.services.relay.get_relay")
    @mock.patch("coruscant.services.relay.logger")
    def test_check_pump_relay__no_state(self, mock_logger, mock_get):
        mock_get.return_value = None

        result = check_relay_state(relay_id="pump_1", relay_pin=11)

        assert result is False
        mock_get.assert_called_once_with(relay_id="pump_1")
        mock_logger.exception.assert_not_called()

    @mock.patch("coruscant.services.relay.get_relay")
    @mock.patch("coruscant.services.relay.set_gpio_state")
    @mock.patch("coruscant.services.relay.update_relay")
    @mock.patch("coruscant.services.relay.logger")
    def test_check_pump_relay__gpio_set_failed(self, mock_logger, mock_update, mock_set, mock_get):
        mock_get.return_value = Relay(relay_id="pump_1", state="ON", mode="BASIC")
        mock_set.return_value = False

        result = check_relay_state(relay_id="pump_1", relay_pin=11)

        assert result is True
        mock_get.assert_called_once_with(relay_id="pump_1")
        mock_set.assert_called_once()
        mock_update.assert_not_called()
        mock_logger.exception.assert_not_called()

    @mock.patch("coruscant.services.relay.get_relay")
    @mock.patch("coruscant.services.relay.logger")
    def test_check_pump_relay__gpio_error(self, mock_logger, mock_get):
        mock_get.side_effect = RuntimeError("gpio error")

        result = check_relay_state(relay_id="pump_1", relay_pin=11)

        assert result is False
        mock_logger.exception.assert_called_once()

    @mock.patch("coruscant.services.relay.get_relay")
    @mock.patch("coruscant.services.relay.logger")
    def test_check_pump_relay__generic_error(self, mock_logger, mock_get):
        mock_get.side_effect = Exception("unexpected error")

        result = check_relay_state(relay_id="pump_1", relay_pin=11)

        assert result is False
        mock_logger.exception.assert_called_once()
