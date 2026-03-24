import logging.config
from decimal import Decimal

from pi1wire import FailedToChangeResolutionException, NotFoundSensorException, Pi1Wire, Resolution

from coruscant.exceptions import TempReadErrorException
from coruscant.settings import LOGGING


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def read_temperature(sensor_id: str) -> Decimal:
    try:
        wire = Pi1Wire()
        sensor = wire.find(sensor_id)

        sensor.change_resolution(resolution=Resolution.X0_25)
        return Decimal(round(sensor.get_temperature(), 2))

    except NotFoundSensorException as e:
        logger.warning(f"Sensor {sensor_id} not found")
        raise TempReadErrorException from e

    except FailedToChangeResolutionException as e:
        logger.exception(f"Can't change resolution for sensor {sensor_id}")
        raise TempReadErrorException from e

    except OSError as e:
        logger.exception(f"Can't read sensor {sensor_id} data")
        raise TempReadErrorException from e

    except Exception as e:
        logger.exception(e)
        raise TempReadErrorException from e
