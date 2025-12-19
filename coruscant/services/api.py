import requests

from coruscant.settings import API_URL


def update_relay_state(relay_id: str, state: str) -> bool:
    response = requests.post(
        f"{API_URL}/relays/{relay_id}/",
        json={"context": {"state": state}},
        timeout=10,
    )
    return response.ok
