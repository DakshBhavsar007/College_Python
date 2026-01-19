
import pdfplumber
import json
import re

pdf_path = r"c:\Users\parul\Desktop\html\PythonMCQs\PB_DE_SEM-III_2025.pdf"
output_json_path = r"c:\Users\parul\Desktop\html\PythonMCQs\extracted_de.json"

def escape_html(text):
    if not text:
        return text
    # Basic escaping, might want to be more robust or selective
    # For now, matching the python one
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

def get_answer_index(ans_char):
    if not ans_char: return 0
    ans_char = str(ans_char).strip().upper()
    mapping = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    return mapping.get(ans_char, 0) # Default to A if invalid, or handle error

# Grouping Units into Modules
# T1: 1, 2, 3
# T2: 4, 5
# T3: 6, 7
# T4: 8, 9, 10
UNIT_TO_MODULE = {
    '1': 'T1', '2': 'T1', '3': 'T1',
    '4': 'T2', '5': 'T2',
    '6': 'T3', '7': 'T3',
    '8': 'T4', '9': 'T4', '10': 'T4'
}

data = {
    'T1': [],
    'T2': [],
    'T3': [],
    'T4': []
}

print("Starting extraction for DE...")
try:
    with pdfplumber.open(pdf_path) as pdf:
        total_q = 0
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    # Basic validation
                    # Analysis showed rows have len 9. 
                    # 0: Sr No, 1: Unit, 2: Question, 3: Ans, 4: ?, 5: OptA, 6: OptB, 7: OptC, 8: OptD
                    if not row or len(row) < 9:
                        continue
                    
                    sr_no = row[0]
                    unit = str(row[1]).strip() if row[1] else ""
                    
                    # Check if header row
                    if not sr_no or "Sr" in str(sr_no) or "No" in str(sr_no) or "Unit" in str(unit):
                        continue
                        
                    question = row[2]
                    ans_char = row[3]
                    
                    # Clean up question
                    if question:
                        question = escape_html(question.strip().replace('\n', ' '))
                    else:
                        continue # Skip empty questions logic
                    
                    options = []
                    # Options are at index 5, 6, 7, 8
                    for idx in range(5, 9):
                        opt_text = row[idx]
                        if opt_text:
                            options.append(escape_html(str(opt_text).strip().replace('\n', ' ')))
                        else:
                            options.append("")
                            
                    ans_idx = get_answer_index(ans_char)
                    
                    module = UNIT_TO_MODULE.get(unit)
                    
                    if module:
                        # Ensure we have options (some rows might be malformed)
                        if any(opt.strip() for opt in options):
                            q_obj = {
                                "q": question,
                                "options": options,
                                "ans": ans_idx,
                                "unit": unit
                            }
                            data[module].append(q_obj)
                            total_q += 1

    print(f"Extraction complete. Total questions: {total_q}")
    for k, v in data.items():
        print(f"{k}: {len(v)} questions")

    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print(f"Saved to {output_json_path}")

except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"An error occurred: {e}")
