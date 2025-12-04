import logging.config
import sqlite3
from decimal import Decimal

from pi1wire import NotFoundSensorException, Pi1Wire, Resolution

from apollo.services.database import save_sensor_data
from apollo.settings import DATABASE_PATH, LOGGING, MODE, SENSORS


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    wire = Pi1Wire()
    connection = sqlite3.connect(DATABASE_PATH)

    for sensor_id, sensor in SENSORS.items():
        try:
            wire_sensor = wire.find(sensor.sensor_id)
        except NotFoundSensorException:
            logger.info(f"Sensor {sensor_id} not found")
            continue

        wire_sensor.change_resolution(resolution=Resolution.X0_25)
        temp = round(Decimal(wire_sensor.get_temperature()), 2)

        save_sensor_data(connection=connection, sensor_id=sensor.sensor_id, temp=temp, context={"mode": MODE})
        logger.info(f"Temp for {sensor.label}: {temp:.2f} *C")
