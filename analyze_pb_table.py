
import pdfplumber
import json

pdf_path = r"c:\Users\parul\Desktop\html\PythonMCQs\PB_Python-I_SEM III_2025.pdf"

try:
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        print(f"--- Founds {len(tables)} tables on Page 1 ---")
        for table in tables:
            # Print rows 4-6 (data rows usually start after header)
            print(json.dumps(table[3:6], indent=2))
except Exception as e:
    print(f"Error: {e}")
