from decimal import Decimal

from coruscant.services.database import (
    get_data_for_sync,
    get_sensor_data,
    save_sensor_data,
)


class TestDatabase:
    def test_create_and_get_sensor(self, clear_tables):
        assert not get_sensor_data(sensor_id="test")
        save_sensor_data(sensor_id="test", temp=Decimal("20.5"))
        assert get_sensor_data(sensor_id="test")

    def test_not_synced_sensors(self, clear_tables):
        assert len(get_data_for_sync()) == 0
        save_sensor_data(sensor_id="test-1", temp=Decimal("20.5"))
        save_sensor_data(sensor_id="test-2", temp=Decimal("20.5"))
        assert len(get_data_for_sync()) == 2
