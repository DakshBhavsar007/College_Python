
import pdfplumber
import json
import re

files = [
    {"path": r"c:\Users\parul\Desktop\html\PythonMCQs\ETC_PB_NEW SYLLABUS_UNIT 01 to 05_PART 01.pdf", "name": "etc"},
    {"path": r"c:\Users\parul\Desktop\html\PythonMCQs\QB_CI_SEM-III.pdf", "name": "ci"}
]

output_data = {}

def clean_text(text):
    if not text: return ""
    return str(text).strip().replace('\n', ' ')

for item in files:
    path = item["path"]
    name = item["name"]
    print(f"Extraction sample from {name}...")
    
    questions = []
    
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages[:5]: # First 5 pages
            tables = page.extract_tables()
            for table in tables:
                if not table: continue
                
                # Find header
                header_idx = -1
                for idx, row in enumerate(table):
                    row_str = " ".join([str(x).lower() for x in row if x])
                    if "question" in row_str or "sr" in row_str:
                        header_idx = idx
                        break
                
                if header_idx == -1: continue
                
                print(f"  Found header at row {header_idx} in a table on page {page.page_number}")
                # Analyze header to map columns
                header = table[header_idx]
                col_map = {"q": -1, "ans": -1, "unit": -1, "opts": []}
                
                for c_idx, col_text in enumerate(header):
                    if not col_text: continue
                    txt = str(col_text).lower()
                    if "question" in txt: col_map["q"] = c_idx
                    elif "ans" in txt: col_map["ans"] = c_idx
                    elif "unit" in txt: col_map["unit"] = c_idx
                    elif "opt" in txt: col_map["opts"].append(c_idx)
                
                print(f"  Column Map: {col_map}")
                
                # Extract first 3 rows of data
                for row_idx in range(header_idx + 1, min(header_idx + 4, len(table))):
                    row = table[row_idx]
                    if len(row) <= max(col_map["q"], col_map["ans"], 3): continue # Basic safety
                    
                    q_text = row[col_map["q"]] if col_map["q"] != -1 else "UNK"
                    ans_text = row[col_map["ans"]] if col_map["ans"] != -1 else "UNK"
                    unit_text = row[col_map["unit"]] if col_map["unit"] != -1 else "UNK"
                    opts = [row[i] for i in col_map["opts"]] if col_map["opts"] else []
                    
                    # If opts are not detected by header, assume they follow specific indices often used
                    if not opts and col_map["q"] != -1:
                        # Fallback strategy: if Q is at 2, Ans usually at 3, Opts at 4,5,6,7 or similar?
                        # Current extract_mcqs.py used: Q=2, Ans=3, Opts=7,8,9,10.
                        pass

                    questions.append({
                        "q": clean_text(q_text),
                        "ans": clean_text(ans_text),
                        "unit": clean_text(unit_text),
                        "options": [clean_text(o) for o in opts],
                        "raw_row": [clean_text(x) for x in row] # For debug
                    })
    
    output_data[name] = questions

with open("extraction_debug.json", "w") as f:
    json.dump(output_data, f, indent=4)
print("Saved extraction_debug.json")
