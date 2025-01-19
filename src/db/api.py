import sqlite3
from src import config


def batch_insert_grant_records(records):
    """
    Insert multiple records into the `grant_records` table in a batch.

    :param records: List of tuples containing (student_id, grant_score, percentage, subject)
    """
    # Connect to SQLite database
    connection = sqlite3.connect(config.DATABASE_PATH)
    cursor = connection.cursor()

    # Insert the records in a batch
    cursor.executemany("""
    INSERT INTO grant (student_id, grant_score, grant_amount, subject_name, year)
    VALUES (?, ?, ?, ?, ?);
    """, records)

    # Commit and close the connection
    connection.commit()
    connection.close()
    print(f"{len(records)} records inserted successfully")


def batch_insert_enrollment_records(records):
    """ TODO """
    pass