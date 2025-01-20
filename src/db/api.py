import sqlite3
from src import config, constants


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
    """
    Insert multiple records into the `enrollment_records` table in a batch.

    received data format:
    {
        "year": int,                     # The year of the enrollment group
        "university_id": str,            # A 3-character string representing the university ID
        "university_name": str,          # The name of the university
        "faculty_id": str,               # A 8-10-character string representing the faculty ID
        "faculty_name": str,             # The name of the faculty
        "subjects": list[str],           # A list of strings representing the subjects
        "enrollments": [                 # A list of enrollment records
            {
                "student_id": str,       # A 9-character string representing the student ID
                "rank": int,             # The rank of the student
                "contest_score": float,  # The contest score of the student
                "subject_scores": list[float]  # A list of float values representing subject scores with the same order as the subjects
            }
        ]
    }
    """
    # Connect to SQLite database
    connection = sqlite3.connect(config.DATABASE_PATH)
    cursor = connection.cursor()

    # Insert the records in a batch
    for record in records:
        year = record["year"]
        university_id = record["university_id"]
        university_name = record["university_name"]
        faculty_id = record["faculty_id"]
        faculty_name = record["faculty_name"]
        subjects = record["subjects"]
        enrollments = record["enrollments"]

        # Insert university if it does not exist
        cursor.execute("""
            INSERT OR IGNORE INTO university (id, name) 
                VALUES (?, ?);""",(university_id, university_name)
        )

        # Insert faculty if it does not exist
        cursor.execute("""
            INSERT OR IGNORE INTO faculty (id, name, university_id) 
                VALUES (?, ?, ?);""",(faculty_id, faculty_name, university_id)
                       )

        # Map the subjects to database representation with mapping
        # find value of matching key.split()[0]
        mapping_subjects = constants.SUBJECTS_KA_TO_EN_MAPPING.keys()
        for i in range(len(subjects)):
            subject_name = subjects[i]

            for key in mapping_subjects:
                if key.split()[0] == subject_name:
                    subjects[i] = constants.SUBJECTS_KA_TO_EN_MAPPING[key]
                    break

        # Iterate and insert enrollments of a group
        for enrollment in enrollments:
            student_id = enrollment["student_id"]
            rank = enrollment["rank"]
            contest_score = enrollment["contest_score"]
            subject_scores = enrollment["subject_scores"]

            # Insert enrollment record
            cursor.execute("""
                INSERT INTO enrollment (student_id, faculty_id, contest_score, rank, year) 
                    VALUES (?, ?, ?, ?, ?);""",(student_id, faculty_id, contest_score, rank, year)
            )

            # Insert subject scores
            for subject, score in zip(subjects, subject_scores):
                cursor.execute("""
                    INSERT INTO result (enrollment_id, subject_name, scaled_score) 
                        VALUES (?, ?, ?);""",(student_id, subject, score)
                )


    # Commit and close the connection
    connection.commit()
    connection.close()
    print(f"{len(records)} records inserted successfully")
