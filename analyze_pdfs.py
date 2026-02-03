
import pdfplumber

etc_pdf = r"c:\Users\parul\Desktop\html\PythonMCQs\ETC_PB_NEW SYLLABUS_UNIT 01 to 05_PART 01.pdf"
ci_pdf = r"c:\Users\parul\Desktop\html\PythonMCQs\QB_CI_SEM-III.pdf"

def is_question_header(row):
    if not row: return False
    # Check for keywords in the row strings
    row_str = " ".join([str(x).lower() for x in row if x])
    return "question" in row_str or "sr" in row_str or "no." in row_str

def analyze(path, name):
    print(f"--- Analyzing {name} ---")
    try:
        with pdfplumber.open(path) as pdf:
            found_header = False
            for i, page in enumerate(pdf.pages[:5]): # Check first 5 pages
                print(f"Page {i+1}")
                tables = page.extract_tables()
                for t_idx, table in enumerate(tables):
                    if not table: continue
                    # Check first few rows for header
                    for r_idx, row in enumerate(table[:5]):
                        if is_question_header(row):
                            print(f"  Found Potential Header in Table {t_idx} Row {r_idx}: {row}")
                            # Print next row as sample data
                            if len(table) > r_idx + 1:
                                print(f"  Sample Data: {table[r_idx+1]}")
                            found_header = True
                            
                if found_header: 
                     break 
            
            if not found_header:
                print("  No question header found in first 5 pages.")

    except Exception as e:
        print(f"Error: {e}")

analyze(etc_pdf, "ETC PDF")
print("\n" + "="*30 + "\n")
analyze(ci_pdf, "CI PDF")
