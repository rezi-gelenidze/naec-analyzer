import os
import pandas as pd

from src import config
from src.enrollments import extractors, segmentation
from src.db import api


def main():
    print("Available PDF files:")
    pdfs = sorted(os.listdir(config.ENROLLMENT_DATA_DIR))

    [print(f"- {pdf_filename}") for pdf_filename in pdfs]

    if not pdfs:
        print("No PDF files found. Exiting.")
        return

    data = []
    for pdf_filename in pdfs:
        print(f"Processing {pdf_filename}...")
        # Read content and divide as enrollment chunks
        string_content = segmentation.pdf_to_string(pdf_filename)
        chunks = segmentation.segment_pdf_content(string_content)

        # extract year from the filename
        year = int(pdf_filename.split(".")[0])

        for chunk in chunks:
            university_id, university_name = extractors.extract_university_name_and_id(chunk)
            faculty_id, faculty_name = extractors.extract_faculty_name_and_id(chunk)

            subjects = extractors.extract_taken_subjects(chunk)
            enrollments = extractors.extract_enrollment_records(chunk)

            # Group data of enrollments for each faculty of a university of a year
            data.append({
                "year": year,
                "university_id": university_id,
                "university_name": university_name,
                "faculty_id": faculty_id,
                "faculty_name": faculty_name,
                "subjects": subjects,
                "enrollments": enrollments
            })

    if not data:
        print("No data extracted from PDFs. Exiting.")
        return

    # Save extracted data to a CSV file for backup
    df = pd.DataFrame(data)
    csv_path = os.path.join(config.DATA_DIR, "enrollment_data_backup.csv")
    df.to_csv(csv_path, index=False)

    # Finally, save the extracted data to the database
    api.batch_insert_enrollment_records(data)

if __name__ == "__main__":
    main()
