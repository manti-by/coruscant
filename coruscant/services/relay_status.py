import logging.config

from coruscant.services.kafka import send_message
from coruscant.settings import LOGGING


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def get_relay_state(relay_id: str) -> str | None:
    logger.info(f"Getting relay state for {relay_id} is no longer supported via API")
    return None


def update_relay_state(relay_id: str, state: str) -> bool:
    message = {
        "relay_id": relay_id,
        "state": state,
        "timestamp": logger.handlers[0].formatter.formatTime(logger.makeRecord("", 0, "", 0, "", (), None))
        if logger.handlers
        else None,
    }

    return send_message(topic="odin", message=message, key=relay_id)
