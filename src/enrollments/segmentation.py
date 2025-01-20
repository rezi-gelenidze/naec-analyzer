import os
import re
import pdfplumber

from src import config


def pdf_to_string(pdf_filename):
    """
    Extract text from a PDF file.
    """
    pdf_path = os.path.join(config.ENROLLMENT_DATA_DIR, pdf_filename)
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        print(f"Extracting text...")
        result = ""

        for i, page in enumerate(pdf.pages):
            print(f"Processing page {i + 1}...")
            string_content = page.extract_text()

            # Remove first two lines (title) of the first page
            if i == 0:
                string_content = "\n".join(string_content.split("\n")[2:])

            result += string_content

            # Break after processing 10 pages TEMPORARY TODO

        #save as txt
        with open('pdf_content.txt', 'w') as f:
            f.write(result)

        return result


def segment_pdf_content(text):
    """
    Segment PDF text content into chunks for each faculty enrollment.
    """
    # Split text into chunks for each faculty enrollment
    chunks = []

    # Clean text from lines where there are only numbers separated by spaces (page number noise)
    text = re.sub(r"^\d+(?:\s+\d+)*\s*\n", "", text, flags=re.MULTILINE)

    # Pattern to find the start of each enrollment group (3 digits followed by a university name)
    start_pattern = r"^\d{3}\s+[ა-ჰ]+.*\n"
    # Find all matches for the start of enrollment groups
    matches = list(re.finditer(start_pattern, text, flags=re.MULTILINE))

    # Iterate over matches to extract chunks
    for i, match in enumerate(matches):
        start = match.start()

        # Determine the end of the current chunk
        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(text)

        # Extract and clean the chunk
        chunk = text[start:end].strip()
        chunks.append(chunk)

    return chunks