import pdfplumber
import json
import re

def escape_html(text):
    if not text:
        return text
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

def get_answer_index(ans_text, options):
    if not ans_text:
        return 0
    
    ans_text = str(ans_text).strip()
    
    letter_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    if ans_text.upper() in letter_map:
        return letter_map[ans_text.upper()]
    
    if ans_text in ['1', '2', '3', '4']:
        return int(ans_text) - 1
    
    ans_clean = ans_text.strip().lower().replace('\n', ' ').replace('  ', ' ')
    for i, opt in enumerate(options):
        if opt:
            opt_clean = str(opt).strip().lower().replace('\n', ' ').replace('  ', ' ')
            if ans_clean == opt_clean or ans_clean in opt_clean or opt_clean in ans_clean:
                return i
    
    for i, opt in enumerate(options):
        if opt:
            opt_clean = str(opt).strip().lower()
            if len(ans_clean) > 5 and len(opt_clean) > 5:
                if ans_clean[:10] == opt_clean[:10]:
                    return i
    
    return 0

def extract_mcqs_dm(pdf_path, test_config):
    """
    Extract MCQs from DM PDF.
    DM has swapped columns: [0]=Unit, [1]=SrNo, rest same.
    """
    unit_to_test = {}
    all_assigned = set()
    for test, units in test_config.items():
        if units != 'rest':
            for u in units:
                unit_to_test[u] = test
                all_assigned.add(u)
    
    data = {'T1': [], 'T2': [], 'T3': [], 'T4': []}
    
    total_q = 0
    skipped = 0
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or len(row) < 10:
                        continue
                    
                    # DM format: [0]=Unit, [1]=SrNo, [2]=Question, [3]=Answer, [4]=Marks, [5]=PrevYear, [6-9]=Options
                    unit_raw = row[0]  # Unit is at index 0 for DM
                    sr_no = row[1]     # Sr.No at index 1
                    question = row[2]
                    ans_text = row[3]
                    marks = row[4]
                    opt1 = row[6]
                    opt2 = row[7]
                    opt3 = row[8]
                    opt4 = row[9]
                    
                    # Skip header rows
                    if not unit_raw or 'Unit' in str(unit_raw) or 'Sr' in str(unit_raw):
                        continue
                    if 'L. J.' in str(unit_raw) or 'L.J.' in str(unit_raw) or 'Note' in str(unit_raw):
                        continue
                    if 'Practice' in str(unit_raw) or 'SEM' in str(unit_raw):
                        continue
                    
                    # Skip non-MCQ rows
                    if str(marks).strip() != '1':
                        skipped += 1
                        continue
                    
                    if not question or not str(question).strip():
                        continue
                    
                    # Get unit number
                    unit = str(unit_raw).strip()
                    unit = re.sub(r'[^\d]', '', unit)
                    if not unit:
                        continue
                    
                    # Build options
                    raw_options = [opt1, opt2, opt3, opt4]
                    options = []
                    for opt in raw_options:
                        if opt:
                            cleaned = escape_html(str(opt).strip().replace('\n', ' '))
                            options.append(cleaned)
                        else:
                            options.append("")
                    
                    if not any(o.strip() for o in options):
                        skipped += 1
                        continue
                    
                    ans_idx = get_answer_index(ans_text, raw_options)
                    q_text = escape_html(str(question).strip().replace('\n', ' '))
                    
                    # Remove leading Sr.No from question text if present
                    q_text = re.sub(r'^\d+\s*', '', q_text).strip()
                    
                    if unit in unit_to_test:
                        test_key = unit_to_test[unit]
                    else:
                        test_key = 'T4'
                    
                    q_obj = {
                        "q": q_text,
                        "options": options,
                        "ans": ans_idx,
                        "unit": unit
                    }
                    
                    data[test_key].append(q_obj)
                    total_q += 1
    
    print(f"\n{'='*60}")
    print(f"DM Extraction Results:")
    print(f"Total MCQs: {total_q}")
    print(f"Skipped: {skipped}")
    for key in ['T1', 'T2', 'T3', 'T4']:
        units_in = set(q['unit'] for q in data[key])
        print(f"  {key}: {len(data[key])} questions (units: {sorted(units_in)})")
    
    return data


# DM config
dm_config = {
    'T1': ['1', '2', '3'],
    'T2': ['4', '5', '6'],
    'T3': ['7', '8'],
    'T4': 'rest'
}

data = extract_mcqs_dm('PB_DM_SEM-IV_2026.pdf', dm_config)

with open('questions/dm.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
print("Saved to questions/dm.json")

# Show sample questions
for key in ['T1', 'T2', 'T3', 'T4']:
    if data[key]:
        q = data[key][0]
        print(f"\n  Sample {key}: Unit {q['unit']} - {q['q'][:80]}...")
        print(f"    Options: {[o[:30] for o in q['options']]}")
        print(f"    Answer: {q['ans']}")
