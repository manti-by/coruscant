from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import TYPE_CHECKING

from coruscant.settings import DATABASE_PATH


if TYPE_CHECKING:
    from decimal import Decimal


def get_sensor_data(sensor_id: str) -> dict:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        sql = "SELECT * FROM data WHERE sensor_id = ? ORDER BY created_at DESC LIMIT 1"
        cursor.execute(sql, (sensor_id,))
        return cursor.fetchone()


def get_data_for_sync(limit: int = 500, offset: int = 0) -> list[dict]:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        sql = "SELECT * FROM data WHERE synced_at IS NULL ORDER BY created_at DESC LIMIT ? OFFSET ?"
        cursor.execute(sql, (limit, offset))
        return cursor.fetchall()


def save_sensor_data(sensor_id: str, temp: Decimal):
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO data (sensor_id, temp) VALUES (?, ?)",
            (sensor_id, str(temp)),
        )
        connection.commit()


def update_sensor_data(sensor_id: str, synced_at: datetime):
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE data SET synced_at = ? WHERE sensor_id = ?",
            (synced_at, sensor_id),
        )
        connection.commit()
