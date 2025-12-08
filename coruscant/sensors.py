import logging.config
from decimal import Decimal

from pi1wire import NotFoundSensorException, Pi1Wire, Resolution

from coruscant.services.database import save_sensor_data
from coruscant.settings import LOGGING, TEMP_SENSORS


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    wire = Pi1Wire()
    for sensor_id in TEMP_SENSORS:
        try:
            wire_sensor = wire.find(sensor_id)
        except NotFoundSensorException:
            logger.warning(f"Sensor {sensor_id} not found")
            continue

        wire_sensor.change_resolution(resolution=Resolution.X0_25)
        temp = Decimal(round(wire_sensor.get_temperature(), 2))

        save_sensor_data(sensor_id=sensor_id, temp=temp)
        logger.info(f"Temp for {sensor_id}: {temp:.2f} *C")
