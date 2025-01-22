/*
In the database we got scaled points for each student on each year's subject exam.

if X is student's taken raw point, scaled point is calculated so:

SP = 15 * ((X - E) / SD) + 150 (which varies between [100, 200])
it helps to compare results from different subjects for competition and grants.

to create a function which calculates
SP -> X (scaled point back to raw) and
X -> SP (raw point to scaled) we need to calculate E and SD for each subject on each year.

E is Mean of X values, and SD is Standard Deviation of X values.

if we ignore their meanings and treat them as two unknowns, we can solve them with two equations,
as it's 2 linear equations, with 2 unknowns, we can solve them.

SP1 = 15 * ((X1 - E) / SD) + 150
SP2 = 15 * ((X2 - E) / SD) + 150

but to take 2 samples of (SP1, X1) and (SP2, X2), we exploit the fact that
every year there was someone who maxed the exam and who took a minimum barrier.

so we query each subjects' each year exam results and find Scaled Point of
MAX and MIN result.

For example for mathematics, exam is MAX 51 points and MIN 11. So min and max scaled points will mean:
(SP_MIN, 11)
(SP_MAX, 51)

so we got 2 samples and can solve the equations.

SP_MIN = 15 * ((11 - E) / SD) + 150
SP_MAX = 15 * ((51 - E) / SD) + 150

we can solve them and get E and SD for each subject on each year.

SD = (X1 - X2) / (SP1 - SP2)
E = X1 - SP1 * SD

after having this two variables solved, we can freely convert between X and SP.

This is the SQL code to calculate E and SD for each subject on each year,
of math, english and foreign language subjects.
*/
-- Calculate E and SD dynamically based on the `exam` table
-- TODO it only works for GEORGIAN, FOREIGN, MATHEMATICS triple of exams for aplha
WITH
SubjectScoreStats AS (
    SELECT
        r.subject_name,
        e.year,
        MIN(scaled_score) AS min_score,
        MAX(scaled_score) AS max_score
    FROM result r
    JOIN enrollment e ON e.student_id = r.enrollment_id
    WHERE r.subject_name IN (SELECT name FROM subject)
    GROUP BY e.year, r.subject_name
),
CalculateSPAndThresholds AS (
    SELECT
        stats.subject_name,
        stats.year,
        ((stats.min_score - 150) * 1.0) / 15 AS sp1,
        ((stats.max_score - 150) * 1.0) / 15 AS sp2,
        ex.min_score AS x1,
        ex.max_score AS x2
    FROM SubjectScoreStats stats
    JOIN exam ex
        ON stats.subject_name = ex.subject_name
        AND stats.year = ex.year
),
CalculateEAndSD AS (
SELECT subject_name,
   year,
   (x1 - x2) / (sp1 - sp2)              AS standard_deviation,
   x1 - sp1 * ((x1 - x2) / (sp1 - sp2)) AS e_value
FROM CalculateSPAndThresholds
)
UPDATE exam
SET
    mean = subquery.e_value,
    standard_deviation = subquery.standard_deviation
FROM CalculateEAndSD subquery
WHERE
    exam.subject_name = subquery.subject_name
  AND exam.year = subquery.year;