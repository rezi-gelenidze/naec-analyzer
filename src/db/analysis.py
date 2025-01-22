import sqlite3
from src import config


def check_historical_data(faculty_id, student_points, weights):
    """
    Calculate contest and grant score
    to check each year enrollment and grant amount
    using precalculated SD and E values and parameters.

    :param faculty_id: Faculty ID for contest ranking.
    :param student_points: Dictionary with student points for each subject.
    :param weights: Dictionary with coefficients for subjects (multipliers).
    :return: Result rows from the calculation.
    """
    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()
    query = """
WITH CalculateSubjectScaledScores AS (
    SELECT
        x_values.subject_name,
        x_values.x_value,
        exam.year,
        15.0 * ((x_values.x_value - exam.mean) / exam.standard_deviation) + 150 AS scaled_score
    FROM (
        SELECT 'MATHEMATICS' AS subject_name, ? AS x_value
        UNION ALL
        SELECT 'FOREIGN LANGUAGE', ?
        UNION ALL
        SELECT 'GEORGIAN LANGUAGE', ?
    ) AS x_values
    JOIN exam ON x_values.subject_name = exam.subject_name
), ComputeGrantAndContestScores AS (
    SELECT
        year,
        SUM(
            (scaled_score * 1.5 * CASE WHEN subject_name = 'MATHEMATICS' THEN 1 ELSE 0 END) +
            (scaled_score * CASE WHEN subject_name = 'FOREIGN LANGUAGE' THEN 1 ELSE 0 END) +
            (scaled_score * CASE WHEN subject_name = 'GEORGIAN LANGUAGE' THEN 1 ELSE 0 END)
        ) * 10 AS grant_score,
        SUM(
            (scaled_score * ? * CASE WHEN subject_name = 'MATHEMATICS' THEN 1 ELSE 0 END) +
            (scaled_score * ? * CASE WHEN subject_name = 'FOREIGN LANGUAGE' THEN 1 ELSE 0 END) +
            (scaled_score * ? * CASE WHEN subject_name = 'GEORGIAN LANGUAGE' THEN 1 ELSE 0 END)
        ) AS contest_score
    FROM CalculateSubjectScaledScores
    GROUP BY year
), FinalRankAndGrant AS (
    SELECT
        scores.year,
        scores.grant_score,
        scores.contest_score,
        (SELECT grant_amount
         FROM grant
         WHERE grant_score < scores.grant_score
           AND subject_name = 'MATHEMATICS'
           AND year = scores.year
         ORDER BY grant_score DESC
         LIMIT 1) AS grant_amount,
        (SELECT rank
         FROM enrollment
         WHERE contest_score < scores.contest_score
           AND faculty_id = ?
           AND year = scores.year
         ORDER BY contest_score DESC
         LIMIT 1) AS rank,
         -- Total enrolled students in that faculty on that year
        (SELECT COUNT(*)
            FROM enrollment
            WHERE year = scores.year
            AND faculty_id = ?
            ) AS total_enrolled
    FROM ComputeGrantAndContestScores scores
)
SELECT *
FROM FinalRankAndGrant;
"""

    params = [
        student_points['MATHEMATICS'],
        student_points['FOREIGN LANGUAGE'],
        student_points['GEORGIAN LANGUAGE'],
        weights['MATHEMATICS'],
        weights['FOREIGN LANGUAGE'],
        weights['GEORGIAN LANGUAGE'],
        faculty_id,
        faculty_id
    ]

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    return results


def get_grant_thresholds():
    """
    Fetch minimum grant scores for 50%, 70%, and 100% grants as reference.

    :return: List of rows with year, min_grant_50, min_grant_70, and min_grant_100.
    """
    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()
    query = """
    WITH GrantThresholds AS (
        SELECT
            year,
            MIN(grant_score) FILTER (WHERE grant_amount = 50) AS min_grant_50,
            MIN(grant_score) FILTER (WHERE grant_amount = 70) AS min_grant_70,
            MIN(grant_score) FILTER (WHERE grant_amount = 100) AS min_grant_100
        FROM grant
        WHERE subject_name = 'MATHEMATICS'
        GROUP BY year
    )
    SELECT *
    FROM GrantThresholds
    ORDER BY year;
    """
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


def get_enrollment_thresholds(faculty_id):
    """
    Fetch enrollment thresholds (minimum contest scores for each rank) for a given faculty.

    :param faculty_id: Faculty ID for which to fetch thresholds.
    :return: List of rows with year, rank, and minimum contest scores.
    """
    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()
    query = """
    WITH EnrollmentThresholds AS (
        SELECT
            year,
            rank,
            MIN(contest_score) AS min_contest_score
        FROM enrollment
        WHERE faculty_id = ?
        GROUP BY year
    )
    SELECT *
    FROM EnrollmentThresholds
    """
    cursor.execute(query, (faculty_id,))
    results = cursor.fetchall()
    conn.close()
    return results


if __name__ == "__main__":
    faculty_id = 19701034

    student_points = {"MATHEMATICS": 46, "FOREIGN LANGUAGE": 69, "GEORGIAN LANGUAGE": 56}
    weights = {"MATHEMATICS": 6, "FOREIGN LANGUAGE": 3, "GEORGIAN LANGUAGE": 3}

    # Print params
    print("Faculty ID:", faculty_id)
    print("Student Points:", student_points)
    print("Subject Weights:", weights)

    # Test check_historical_data
    print("Historical Data:")
    result = check_historical_data(faculty_id, student_points, weights)
    for row in result:
        print(row)

    # Test get_grant_thresholds
    print("\nGrant Thresholds:")
    grant_thresholds = get_grant_thresholds()
    for row in grant_thresholds:
        print(row)

    # Test get_enrollment_thresholds
    print("\nEnrollment Thresholds:")
    enrollment_thresholds = get_enrollment_thresholds(faculty_id)
    for row in enrollment_thresholds:
        print(row)
