import re


def extract_university_name_and_id(text):
    """
    Extract university ID and name from the given text chunk.
    """
    university_match = re.search(r"^(\d{3})\s+(.+?)\n", text, flags=re.MULTILINE)

    if university_match:
        university_id = university_match.group(1)
        university_name = university_match.group(2).strip()

        return university_id, university_name

    print(text)
    raise ValueError("university ID/name not found in the given text chunk.")

def extract_faculty_name_and_id(text):
    """
    Extract faculty ID and name from the given text chunk.
    Matches everything between the faculty ID and 'წლიური გადასახადი'.
    """
    # Regex to match faculty ID and capture all text until 'წლიური გადასახადი'
    faculty_match = re.search(
        r"^(\d{8,11})\s+(.+?)\s+წლიური გადასახადი",
        text,
        flags=re.DOTALL | re.MULTILINE
    )

    if faculty_match:
        faculty_id = faculty_match.group(1)
        faculty_name = faculty_match.group(2).strip()
        return faculty_id, faculty_name.strip()

    print(text)
    raise ValueError("Faculty ID/name not found in the given text chunk.")

def extract_taken_subjects(text):
    """
    Extract subjects taken by students for a given faculty enrollment.
    """
    # Match the header line that lists the subjects
    subjects_match = re.search(r"საგამოცდოს\s+(.+?)\s+საკონკურსო", text)
    if subjects_match:
        subjects = subjects_match.group(1).strip().split()
        return subjects
    return []


def extract_enrollment_records(text):
    """
    Extract enrollment records from the given text chunk.
    """
    records = []
    # Pattern to match enrollment lines
    # RANK STUDENT_ID SUBJECT_SCORES+ CONTEST_SCORE GRANT_SCORE(Ignored)
    enrollment_pattern = re.compile(r"^(\d+)\s+(\d{9})\s+((?:\d{3}\.\d\s+){3,4})(\d+\.\d)(?:\s+(?:50|70|100))?",
                                    flags=re.MULTILINE)

    for match in enrollment_pattern.finditer(text):
        rank = int(match.group(1))
        student_id = int(match.group(2))
        subjects_scores = match.group(3).strip()
        contest_score = float(match.group(4))

        # Parse individual subject scores
        subject_scores = [float(score) for score in subjects_scores.split()]

        records.append({
            "rank": rank,
            "student_id": student_id,
            "subject_scores": subject_scores,
            "contest_score": contest_score
        })

    return records
