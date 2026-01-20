import sys
from unittest import mock

from fastapi.testclient import TestClient


mock_gpio = mock.MagicMock()
sys.modules["RPi"] = mock.MagicMock()
sys.modules["RPi.GPIO"] = mock_gpio

from coruscant.server import app


client = TestClient(app)


class TestRelayEndpoint:
    @mock.patch("coruscant.server.set_gpio_state")
    def test_set_relay__success_on(self, mock_set):
        mock_set.return_value = True

        response = client.post("/relay/", json={"relay_id": "PUMP-WF-2", "state": "ON"})

        assert response.status_code == 200
        assert response.json() == {"success": True}
        assert mock_set.called

    @mock.patch("coruscant.server.set_gpio_state")
    def test_set_relay__success_off(self, mock_set):
        mock_set.return_value = True

        response = client.post("/relay/", json={"relay_id": "PUMP-RD", "state": "OFF"})

        assert response.status_code == 200
        assert response.json() == {"success": True}
        assert mock_set.called

    @mock.patch("coruscant.server.set_gpio_state")
    def test_set_relay__lowercase_state(self, mock_set):
        mock_set.return_value = True

        response = client.post("/relay/", json={"relay_id": "PUMP-WF-2", "state": "on"})

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_set_relay__relay_not_found(self):
        response = client.post("/relay/", json={"relay_id": "UNKNOWN-PUMP", "state": "ON"})

        assert response.status_code == 404

    @mock.patch("coruscant.server.set_gpio_state")
    def test_set_relay__gpio_failed(self, mock_set):
        mock_set.return_value = False

        response = client.post("/relay/", json={"relay_id": "PUMP-WF-2", "state": "ON"})

        assert response.status_code == 400

    @mock.patch("coruscant.server.set_gpio_state")
    def test_set_relay__state_normalized_to_lowercase(self, mock_set):
        mock_set.return_value = True

        response = client.post("/relay/", json={"relay_id": "PUMP-WF-2", "state": "On"})

        assert response.status_code == 200
        assert response.json()["success"] is True
