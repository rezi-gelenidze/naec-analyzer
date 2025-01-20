-- Subjects table, which contains the list of subjects that provide grants.
CREATE TABLE IF NOT EXISTS subject
(
    name VARCHAR(255) PRIMARY KEY -- The name of the subject.
);

-- Populate the subjects table with the list of subjects.
INSERT INTO subject (name)
VALUES ('MATHEMATICS'),
       ('PHYSICS'),
       ('CHEMISTRY'),
       ('BIOLOGY'),
       ('HISTORY'),
       ('GEOGRAPHY'),
       ('LITERATURE'),
       ('ART'),
       ('CIVICS'),
       ('GENERAL APTITUDE'),
       -- Mandatory non-grant subjects.
       ('GEORGIAN LANGUAGE'),
       ('FOREIGN LANGUAGE');

-- Tables for university and faculty information.
CREATE TABLE IF NOT EXISTS university
(
    id   CHAR(3) PRIMARY KEY,  -- The ID of the university is a 3-character string.
    name VARCHAR(511) NOT NULL -- The name of the university.
);

CREATE TABLE IF NOT EXISTS faculty
(
    id            CHAR(8) PRIMARY KEY,                             -- The ID of the faculty is an 8-character string.
    name          VARCHAR(511) NOT NULL,                           -- The name of the faculty.
    university_id CHAR(3)      NOT NULL,                           -- FK to the university table.
    FOREIGN KEY (university_id) REFERENCES university (id)
);

-- Record for student enrollment in a specific faculty on a specific year with written subject scores.
CREATE TABLE IF NOT EXISTS enrollment
(
    student_id    CHAR(9) PRIMARY KEY, -- Each student can only enroll once. Same person on different years will have different student IDs.
    faculty_id    CHAR(8) NOT NULL,   -- FK to the faculty table.
    contest_score FLOAT   NOT NULL,
    rank          INTEGER NOT NULL,
    year          INTEGER NOT NULL,
    FOREIGN KEY (faculty_id) REFERENCES faculty (id)
);

-- Record for enrollment results for specific subjects.
CREATE TABLE IF NOT EXISTS result
(
    enrollment_id CHAR(9) NOT NULL,  -- FK to enrollment table.
    subject_name  VARCHAR(255) NOT NULL, -- FK to subject table.
    scaled_score  FLOAT   NOT NULL,
    PRIMARY KEY (enrollment_id, subject_name),
    FOREIGN KEY (enrollment_id) REFERENCES enrollment (student_id),
    FOREIGN KEY (subject_name) REFERENCES subject (name)
);

-- Record for acquired grants.
CREATE TABLE IF NOT EXISTS grant
(
    student_id   CHAR(9) PRIMARY KEY, -- FK to enrollment table.
    grant_score  FLOAT       NOT NULL, -- Cumulative score of the student.
    grant_amount INTEGER     NOT NULL, -- 50%, 75%, or 100%.
    subject_name VARCHAR(255) NOT NULL, -- FK to subject table.
    year         INTEGER      NOT NULL,
    FOREIGN KEY (student_id) REFERENCES enrollment (student_id),
    FOREIGN KEY (subject_name) REFERENCES subject (name)
);
