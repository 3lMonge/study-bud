import tempfile
import os
import pymupdf


def save_uploaded_pdf(uploaded_file):
    """
    Saves an uploaded PDF temporarily and returns the file path.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.read())
        return temp_file.name


def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF page by page.

    Returns:
        [
            {"page": 1, "text": "..."},
            {"page": 2, "text": "..."}
        ]
    """
    doc = pymupdf.open(pdf_path)
    pages = []

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text()

        if text.strip():
            pages.append({
                "page": page_number,
                "text": text
            })

    doc.close()
    return pages


def delete_temp_file(file_path):
    """
    Deletes the temporary PDF file after processing.
    """
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
