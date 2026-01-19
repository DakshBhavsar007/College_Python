
import pdfplumber
import json
import re

pdf_path = r"c:\Users\parul\Desktop\html\PythonMCQs\PB_Python-I_SEM III_2025.pdf"
output_json_path = r"c:\Users\parul\Desktop\html\PythonMCQs\extracted_python.json"

def escape_html(text):
    if not text:
        return text
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

def get_answer_index(ans_char):
    ans_char = str(ans_char).strip().upper()
    mapping = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    return mapping.get(ans_char, -1)

# Grouping Units into Modules
# T1: 1, 2, 3
# T2: 4, 5
# T3: 6, 7, 8
# T4: 9, 10
UNIT_TO_MODULE = {
    '1': 'T1', '2': 'T1', '3': 'T1',
    '4': 'T2', '5': 'T2',
    '6': 'T3', '7': 'T3', '8': 'T3',
    '9': 'T4', '10': 'T4'
}

data = {
    'T1': [],
    'T2': [],
    'T3': [],
    'T4': []
}

print("Starting extraction...")
try:
    with pdfplumber.open(pdf_path) as pdf:
        total_q = 0
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    # Basic validation: check if row has enough columns
                    # We expect around 11 columns based on analysis
                    if not row or len(row) < 11:
                        continue
                    
                    # Columns based on analysis:
                    # 0: Sr No, 1: Unit, 2: Question, 3: Ans, ... 7: OptA, 8: OptB, 9: OptC, 10: OptD
                    
                    sr_no = row[0]
                    unit = str(row[1]).strip() if row[1] else ""
                    question = row[2]
                    ans_char = row[3]
                    
                    # Check if header row (Sr. No. usually in header)
                    if not sr_no or "Sr" in str(sr_no) or "No" in str(sr_no):
                        continue
                        
                    # Clean up content
                    if question:
                        question = escape_html(question.strip().replace('\n', ' '))
                    
                    options = []
                    # Options are at index 7, 8, 9, 10
                    for idx in range(7, 11):
                        opt_text = row[idx]
                        if opt_text:
                            options.append(escape_html(str(opt_text).strip().replace('\n', ' ')))
                        else:
                            options.append("") # Placeholder for empty option
                            
                    ans_idx = get_answer_index(ans_char)
                    
                    if ans_idx == -1:
                        # try to find answer in options if not A/B/C/D? No, usually it's a char.
                        # Sometimes answer might be empty or formatted weirdly.
                        # We'll skip or mark as 0 (default)
                        ans_idx = 0 
                    
                    module = UNIT_TO_MODULE.get(unit)
                    
                    if module and question:
                        # Check if at least one option is non-empty
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
    print(f"An error occurred: {e}")
