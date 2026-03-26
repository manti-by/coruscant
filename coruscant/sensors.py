import logging.config

from coruscant.exceptions import TempReadErrorException
from coruscant.services.database import save_sensor_data
from coruscant.services.kafka import update_sensor_data
from coruscant.services.sensors import read_temperature
from coruscant.settings import LOGGING, TEMP_SENSORS


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    for sensor_id in TEMP_SENSORS:
        try:
            temp = read_temperature(sensor_id=sensor_id)
            save_sensor_data(sensor_id=sensor_id, temp=temp)
            update_sensor_data(sensor_id=sensor_id, temp=temp)
            logger.debug(f"Temp for {sensor_id}: {temp:.2f} *C")
        except TempReadErrorException:
            pass
