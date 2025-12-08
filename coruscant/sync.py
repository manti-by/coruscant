import logging.config

import requests

from coruscant.services.database import get_data_for_sync
from coruscant.settings import LOGGING, SYNC_API_URL


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    while True:
        if not (result := get_data_for_sync()):
            logger.info("No new sensors data received, exiting")
            exit(0)

        for item in result:
            requests.post(
                SYNC_API_URL,
                data={
                    "sensor_id": item["sensor_id"],
                    "temp": item["temp"],
                },
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
        logger.info(f"Synced {len(result)} sensor records")
