import logging.config

import requests

from coruscant.settings import API_URL, LOGGING


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def update_relay_state(relay_id: str, state: str) -> bool:
    response = requests.patch(
        f"{API_URL}/relays/{relay_id}/",
        json={"context": {"state": state}},
        timeout=10,
    )
    if not response.ok:
        logger.error(response.text)
    return response.ok
