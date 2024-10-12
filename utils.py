import docx2txt
import PyPDF2
from pdf2image import convert_from_bytes
import pytesseract
from io import BytesIO

def extract_text_from_pdf(file_content):
    text = ""
    reader = PyPDF2.PdfReader(file_content)
    for page in reader.pages:
        text += page.extract_text()
    return text

def ocr_pdfs(file_content):
    pages = convert_from_bytes(file_content.read(), 300)
    full_text = ""
    for page in pages:
        full_text += pytesseract.image_to_string(page)

    full_text = full_text.replace('\n', ' ')
    return full_text


def extract_text_from_docx(file_content):
    return docx2txt.process(BytesIO(file_content.read()))


def extract_text_from_txt(file_content):
    return file_content.read().decode('utf-8')


def parse_resume(file_content, file_name):
    """
    This function processes the in-memory file object and determines which
    function to call based on the file type (extension).
    """
    if file_name.endswith('.pdf'):
        # return extract_text_from_pdf(file_content)
        return ocr_pdfs(file_content)
    elif file_name.endswith('.docx'):
        return extract_text_from_docx(file_content)
    elif file_name.endswith('.txt'):
        return extract_text_from_txt(file_content)
    else:
        return ""