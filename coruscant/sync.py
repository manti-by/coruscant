import logging.config
from datetime import UTC, datetime

import requests

from coruscant.services.database import get_data_for_sync, update_sensor_data
from coruscant.settings import LOGGING, SYNC_API_URL


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    while True:
        if not (result := get_data_for_sync()):
            exit(0)

        for item in result:
            # Add TZ info as the main server can use non-UTC time zone
            created_at = datetime.strptime(item["created_at"], "%Y-%m-%d %H:%M:%S")
            created_at = created_at.replace(tzinfo=UTC).isoformat()

            requests.post(
                SYNC_API_URL,
                json={
                    "temp": item["temp"],
                    "sensor_id": item["sensor_id"],
                    "created_at": created_at,
                },
                timeout=10,
            )
            update_sensor_data(sensor_id=item["sensor_id"], synced_at=datetime.now())

        logger.info(f"Synced {len(result)} sensor records")
