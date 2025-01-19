import os
import re

import pdfplumber
import pandas as pd

from src import constants, config
from src.db import api


def main():
    # List available PDF files
    print("Available PDF files:")
    pdfs = sorted(os.listdir(config.GRANTS_DATA_DIR))

    # Display the list of PDF files
    for i, pdf in enumerate(pdfs, start=1):
        print(f"{i}. {pdf}")

    # Prepare data for database insertion
    data = []
    for pdf in pdfs:
        result = process_pdf_to_tuple_list(pdf)
        data.extend(result)

    # save as csv file for backup if DB insertion fails
    print("Saving data to a CSV file for backup...")
    df = pd.DataFrame(data, columns=["student_id", "grant_score", "grant_amount", "subject_name", "year"])
    df.to_csv(config.DATA_DIR + "/grants_data.csv", index=False)

    # Insert data into the database
    print("Inserting into the database...")
    api.batch_insert_grant_records(data)


def extract_subject_and_percentage(text):
    """
    Extract subject name and percentage (e.g., 100%) from a page.
    """
    # Perform OCR to extract text

    # Extract percentage (e.g., "100%")
    percentage_match = re.search(r"(\d+%)", text)
    percentage = percentage_match.group(1)

    # Extract subject name (e.g., "ბიოლოგია")
    subject_match = re.search(
        rf"({'|'.join(constants.SUBJECTS_KA_TO_EN_MAPPING.keys())})",
        text,
    )
    subject = constants.SUBJECTS_KA_TO_EN_MAPPING[subject_match.group(1)]

    return subject, percentage


def extract_table_of_records(text):
    """
    Extract a table of student IDs and grant scores from a page.
    """
    # Regex to match student ID and grant score (e.g., "401500482 6082.0")
    records = []
    for line in text.split("\n"):
        match = re.match(r"(\d+)\s+(\d+\.\d+)", line)
        if match:
            student_id = match.group(1)
            grant_score = float(match.group(2))
            records.append({"student_id": student_id, "grant_score": grant_score})

    return records


def process_pdf_to_tuple_list(pdf_filename):
    """
    Process a PDF file, extract data from each page, and return a list of tuples for database insertion.
    """
    # Convert PDF to images
    print(f"Converting file {pdf_filename} to textual content...")

    pdf_path = os.path.join(config.GRANTS_DATA_DIR, pdf_filename)

    with pdfplumber.open(pdf_path) as pdf:
        page_contents = [page.extract_text() for page in pdf.pages]

    # Initialize a list to store the extracted data
    records = []
    year = int(pdf_filename.split(".")[0])  # Extract year from the filename

    # Process each page
    for page_number, page_content in enumerate(page_contents):
        # Extract subject and percentage
        subject_name, grant_amount = extract_subject_and_percentage(page_content)

        # Extract student records
        student_records = extract_table_of_records(page_content)

        # Add records as tuples (student_id, grant_score, subject, percentage, year)
        for record in student_records:
            records.append((
                record["student_id"],  # student_id
                record["grant_score"],  # grant_score
                int(grant_amount[:-1]),  # percentage (converted to integer)
                subject_name,  # subject name of acquired grant
                year  # year
            ))

    return records


if __name__ == "__main__":
    main()
