import fitz  # PyMuPDF

def parse_pdf(file_bytes: bytes) -> str:
    text = ""
    try:
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
    except Exception as e:
        print(f"Error parsing PDF: {e}")
    return text
