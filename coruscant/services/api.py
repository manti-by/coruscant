import logging.config

import requests
from requests.exceptions import RequestException

from coruscant.models import Relay
from coruscant.settings import API_TOKEN, API_URL, LOGGING


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def get_relay(relay_id: str) -> Relay | None:
    """Fetch the computed target state and mode of a relay from the ODIN API."""
    try:
        response = requests.get(
            f"{API_URL}/relays/{relay_id}/",
            headers={"Authorization": f"Token {API_TOKEN}"},
            timeout=10,
        )

        if response.ok:
            data = response.json()

            if not (target_state := data.get("target_state")):
                logger.exception(f"{relay_id}: no target_state in response")
                return None
            mode = data.get("mode")

            logger.info(f"get_relay: relay_id={relay_id}, target_state={target_state}, mode={mode}")
            return Relay(relay_id=relay_id, state=target_state, mode=mode)

        logger.exception(f"{relay_id}: {response.text}")

    except RequestException as e:
        logger.exception(f"{relay_id}: {e}")
    return None
