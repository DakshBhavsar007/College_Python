
import pdfplumber

pdf_path = r"c:\Users\parul\Desktop\html\PythonMCQs\PB_DE_SEM-III_2025.pdf"

print(f"Analyzing {pdf_path}...")
try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        
        # Analyze first few pages to check table structure
        for i in range(min(5, len(pdf.pages))):
            print(f"\n--- PAGE {i+1} ---")
            tables = pdf.pages[i].extract_tables()
            if not tables:
                print("No tables found.")
            for table in tables:
                if table:
                    # Print first 2 rows of each table
                    for row in table[:2]: 
                        print(row)
                        print(f"Row len: {len(row)}")
        
        # Analyze last few pages to find max unit
        print("\n--- CHECKING LAST PAGES ---")
        for i in range(max(0, len(pdf.pages)-3), len(pdf.pages)):
            print(f"\n--- PAGE {i+1} ---")
            tables = pdf.pages[i].extract_tables()
            for table in tables:
                if table:
                    for row in table[:5]:
                        if len(row) > 1:
                            print(f"Unit in row: {row[1]}")
                        
except Exception as e:
    print(f"Error: {e}")
