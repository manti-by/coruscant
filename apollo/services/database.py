from __future__ import annotations

import json
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from decimal import Decimal
    from sqlite3 import connection as Connection  # noqa


def get_sensors_data(
    connection: Connection, limit: int = 500, offset: int = 0, sensor_id: str | None = None
) -> list[dict]:
    cursor = connection.cursor()
    params = (limit, offset)
    sql = "SELECT * FROM data ORDER BY created_at DESC LIMIT ? OFFSET ?"
    if sensor_id is not None:
        params = (sensor_id, limit, offset)
        sql = "SELECT * FROM data WHERE sensor_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?"
    cursor.execute(sql, params)
    return [{**item} for item in cursor.fetchall()]


def get_not_synced_sensors_data(connection: Connection, limit: int = 500, offset: int = 0) -> list[dict]:
    cursor = connection.cursor()
    sql = "SELECT * FROM data WHERE synced_at IS NULL ORDER BY created_at DESC LIMIT ? OFFSET ?"
    cursor.execute(sql, (limit, offset))
    return cursor.fetchall()


def get_latest_sensors_data(connection: Connection, sensor_ids: list[str]) -> list[dict]:
    cursor = connection.cursor()
    result = []
    for sensor_id in sensor_ids:
        cursor.execute("SELECT * FROM data WHERE sensor_id = ? ORDER BY created_at DESC", (sensor_id,))
        if item := cursor.fetchone():
            result.append(item)
    return result


def save_sensor_data(connection: Connection, sensor_id: str, temp: Decimal, context: dict | None = None):
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO data (sensor_id, temp, context) VALUES (?, ?, ?)",
        (sensor_id, str(temp), json.dumps(context) if context else "{}"),
    )
    connection.commit()
