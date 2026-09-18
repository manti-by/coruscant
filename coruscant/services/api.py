import logging.config

import requests
from requests.exceptions import RequestException

from coruscant.settings import API_TOKEN, API_URL, LOGGING


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def get_relay_state(relay_id: str) -> str | None:
    try:
        response = requests.get(
            f"{API_URL}/relays/{relay_id}/",
            headers={"Authorization": f"Token {API_TOKEN}"},
            timeout=10,
        )

        if response.ok:
            target_state = response.json().get("target_state")
            logger.info(f"get_relay_state: relay_id={relay_id}, target_state={target_state}")
            return target_state
        logger.exception(f"{relay_id}: {response.text}")

    except RequestException as e:
        logger.exception(f"{relay_id}: {e}")
    return None
