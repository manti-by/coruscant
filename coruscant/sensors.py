import logging.config
from decimal import Decimal

from pi1wire import FailedToChangeResolutionException, NotFoundSensorException, Pi1Wire, Resolution

from coruscant.services.database import save_sensor_data
from coruscant.settings import LOGGING, TEMP_SENSORS


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    wire = Pi1Wire()

    for sensor_id in TEMP_SENSORS:
        try:
            wire_sensor = wire.find(sensor_id)
            wire_sensor.change_resolution(resolution=Resolution.X0_25)
            temp = Decimal(round(wire_sensor.get_temperature(), 2))

            save_sensor_data(sensor_id=sensor_id, temp=temp)
            logger.debug(f"Temp for {sensor_id}: {temp:.2f} *C")

        except NotFoundSensorException:
            logger.warning(f"Sensor {sensor_id} not found")

        except FailedToChangeResolutionException:
            logger.error(f"Can't change resolution for sensor {sensor_id}")

        except OSError:
            logger.error(f"Can't read sensor {sensor_id} data")

        except Exception as e:
            logger.critical(e)
