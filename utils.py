import re
import docx2txt
import PyPDF2
import os
import spacy
from pdf2image import convert_from_path
import pytesseract
# from spire.doc import *
# from spire.doc.common import *

nlp = spacy.load("en_core_web_sm")


# # Regex to extract years
# def extract_years(text):
#     match = re.search(r'(\d{4})-(\d{4})', text)
#     if match:
#         start_year = int(match.group(1))
#         end_year = int(match.group(2))
#         return end_year - start_year
#     else:
#         return None

# # Function to extract time periods like 'for X years'
# def extract_vague_periods(text):
#     match = re.search(r'for (\d+) years', text)
#     if match:
#         return int(match.group(1))
#     return None

# !pip install docx2txt PyPDF2
def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text


def ocr_pdfs(file_path):
    pages = convert_from_path(file_path, 300)
    # If you want to extract text from all pages:
    full_text = ""
    for page in pages:
        full_text += pytesseract.image_to_string(page)

    full_text.replace('\n', ' ')
    return full_text
    # return " ".join([token.text.lower() for token in nlp(full_text) if not token.is_space and not token.is_punct])

def extract_text_from_docx(file_path):
    return docx2txt.process(file_path)

# def extract_text_from_doc(file_path):
#     # Create an object of the Document class
#     document = Document()
#     # Load a Word DOC file
#     document.LoadFromFile("/content/4288m1hpp1.doc")

#     # Save the DOC file to DOCX format
#     document.SaveToFile("ToDocx.docx", FileFormat.Docx2016)
#     # Close the Document object
#     document.Close()
#     text = extract_text_from_docx("ToDocx.docx")
#     os.remove("ToDocx.docx")
#     return text


def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def parse_resume(file_path):
    if file_path.endswith('.pdf'):
        # return extract_text_from_pdf(file_path)
        return ocr_pdfs(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    # elif file_path.endswith('.doc'):
    #     return extract_text_from_doc(file_path)
    elif file_path.endswith('.txt'):
        return extract_text_from_txt(file_path)
    else:
        return ""