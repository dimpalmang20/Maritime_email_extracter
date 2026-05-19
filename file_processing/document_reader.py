import pdfplumber
from docx import Document


def read_pdf(file_path):

    text = ""

    with pdfplumber.open(file_path) as pdf:

        for page in pdf.pages:

            text += page.extract_text() + "\n"

    return text


def read_docx(file_path):

    doc = Document(file_path)

    text = ""

    for para in doc.paragraphs:

        text += para.text + "\n"

    return text