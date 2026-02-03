import logging.config

import requests
from requests.exceptions import RequestException

from coruscant.settings import API_URL, LOGGING


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def get_relay_state(relay_id: str) -> str | None:
    try:
        response = requests.get(
            f"{API_URL}/relays/{relay_id}/",
            timeout=10,
        )

        if response.ok:
            return response.json().get("target_state")
        logger.error(response.text)

    except RequestException as e:
        logger.error(e)
    return None
