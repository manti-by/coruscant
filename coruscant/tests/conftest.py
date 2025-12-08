import sqlite3

import pytest

from ..settings import BASE_DIR, DATABASE_PATH


@pytest.fixture(scope="session", autouse=True)
def db_connection():
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        with open(BASE_DIR / "utils" / "database.sql") as f:
            create_table_query = f.read()
        connection.cursor().execute(create_table_query)
    except sqlite3.Error:
        pass

    yield connection


@pytest.fixture(scope="function", autouse=True)
def clear_tables(db_connection):
    """This fixture will be executed after every test, clearing the given table."""
    yield
    db_connection.cursor().execute("DELETE FROM data;")
    db_connection.commit()
