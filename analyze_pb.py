
import pdfplumber

pdf_path = r"c:\Users\parul\Desktop\html\PythonMCQs\PB_Python-I_SEM III_2025.pdf"

with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages[:5]):
        print(f"--- Page {i+1} ---")
        print(page.extract_text())
        print("\n")
