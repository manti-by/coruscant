import sys
from unittest import mock


mock_gpio = mock.MagicMock()
sys.modules["RPi"] = mock.MagicMock()
sys.modules["RPi.GPIO"] = mock_gpio

from coruscant.relay_check import check_relays
from coruscant.settings import PUMP_MAP, SERVO_MAP


@mock.patch("coruscant.relay_check.logger")
@mock.patch("coruscant.relay_check.close_gpio")
@mock.patch("coruscant.relay_check.time.sleep")
@mock.patch("coruscant.relay_check.set_gpio_state")
@mock.patch("coruscant.relay_check.setup_gpio")
def test_check_relays__turns_each_relay_on_then_off(mock_setup, mock_set, mock_sleep, mock_close, mock_logger):
    check_relays()

    relays = [*PUMP_MAP.items(), *SERVO_MAP.items()]
    assert mock_set.call_args_list == [
        call
        for relay_pin, _ in relays
        for call in (
            mock.call(gpio_pin=relay_pin, target_state=mock_gpio.HIGH),
            mock.call(gpio_pin=relay_pin, target_state=mock_gpio.LOW),
        )
    ]
    mock_sleep.assert_has_calls([mock.call(1)] * len(relays))
    mock_setup.assert_called_once_with()
    mock_close.assert_called_once_with()
    mock_logger.info.assert_has_calls([mock.call(f"Testing relay #{relay_id}") for _, relay_id in relays])
