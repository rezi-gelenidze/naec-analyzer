import sqlite3
import os

from src import config


def setup():
    """
    Execute the SQL commands from a seed SQL file to create tables and insert data.
    """
    # Connect to SQLite database (creates the file if it doesn't exist)
    connection = sqlite3.connect(config.DATABASE_PATH)
    cursor = connection.cursor()

    try:
        schema_seed_path = os.path.join(config.SEED_DIR, "schema.sql")

        # Read the SQL file
        with open(schema_seed_path, 'r', encoding='utf-8') as file:
            sql_script = file.read()

        # Execute the SQL script
        cursor.executescript(sql_script)

        # Commit the changes
        connection.commit()
        print(f"SQL script executed successfully from {schema_seed_path}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the connection
        connection.close()


if __name__ == "__main__":
    setup()

