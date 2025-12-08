from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

import psycopg2
from psycopg2.extras import DictCursor

from coruscant.settings import DATABASE_PATH, DATABASE_URL


if TYPE_CHECKING:
    from decimal import Decimal


def get_sensor(sensor_id: str) -> dict:
    with psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor) as connection:
        cursor = connection.cursor()
        sql = "SELECT * FROM sensors_sensor WHERE sensor_id = ? ORDER BY created_at DESC LIMIT 1"
        cursor.execute(sql, (sensor_id,))
        return cursor.fetchone()


def get_sensor_data(sensor_id: str) -> dict:
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()
        sql = "SELECT * FROM data WHERE sensor_id = ? ORDER BY created_at DESC LIMIT 1"
        cursor.execute(sql, (sensor_id,))
        return cursor.fetchone()


def get_data_for_sync(limit: int = 500, offset: int = 0) -> list[dict]:
    with sqlite3.connect(DATABASE_PATH) as connection:
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
