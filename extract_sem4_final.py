import pdfplumber
import json
import re

def escape_html(text):
    if not text:
        return text
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

def get_answer_index(ans_text, options):
    """
    Determine the correct answer index.
    ans_text could be: A/B/C/D, a/b/c/d, or the actual answer text.
    """
    if not ans_text:
        return 0
    
    ans_text = str(ans_text).strip()
    
    # Check if it's a letter A/B/C/D
    letter_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3,
                  'a': 0, 'b': 1, 'c': 2, 'd': 3}
    if ans_text.upper() in letter_map:
        return letter_map[ans_text.upper()]
    
    # Check if it's 1/2/3/4
    if ans_text in ['1', '2', '3', '4']:
        return int(ans_text) - 1
    
    # Otherwise, try to match the answer text with one of the options
    ans_clean = ans_text.strip().lower().replace('\n', ' ').replace('  ', ' ')
    for i, opt in enumerate(options):
        if opt:
            opt_clean = str(opt).strip().lower().replace('\n', ' ').replace('  ', ' ')
            if ans_clean == opt_clean or ans_clean in opt_clean or opt_clean in ans_clean:
                return i
    
    # Fuzzy match: if a significant portion matches
    for i, opt in enumerate(options):
        if opt:
            opt_clean = str(opt).strip().lower()
            # Check if first 10 chars match
            if len(ans_clean) > 5 and len(opt_clean) > 5:
                if ans_clean[:10] == opt_clean[:10]:
                    return i
    
    return 0  # Default to first option

def extract_mcqs(pdf_path, subject_name, test_config):
    """
    Extract MCQs from a practice book PDF.
    Only extracts 1-mark questions (MCQs with 4 options).
    Returns dict with T1, T2, T3, T4 keys.
    """
    
    # Build unit-to-test mapping from config
    unit_to_test = {}
    all_assigned = set()
    for test, units in test_config.items():
        if units != 'rest':
            for u in units:
                unit_to_test[u] = test
                all_assigned.add(u)
    
    data = {'T1': [], 'T2': [], 'T3': [], 'T4': []}
    
    print(f"\n{'='*60}")
    print(f"Extracting: {subject_name} from {pdf_path}")
    
    total_q = 0
    skipped = 0
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or len(row) < 10:
                        continue
                    
                    sr_no = row[0]
                    unit_raw = row[1]
                    question = row[2]
                    ans_text = row[3]
                    marks = row[4]
                    # row[5] = previous year
                    opt1 = row[6]
                    opt2 = row[7]
                    opt3 = row[8]
                    opt4 = row[9]
                    
                    # Skip header rows
                    if not sr_no or 'Sr' in str(sr_no) or 'No' in str(sr_no):
                        continue
                    
                    # Skip non-MCQ rows (marks != 1)
                    if str(marks).strip() != '1':
                        skipped += 1
                        continue
                    
                    # Skip if no question
                    if not question or not str(question).strip():
                        continue
                    
                    # Get unit number
                    unit = str(unit_raw).strip() if unit_raw else ""
                    # Remove any non-digit chars
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
                    
                    # Skip if no valid options
                    if not any(o.strip() for o in options):
                        skipped += 1
                        continue
                    
                    # Get answer index
                    ans_idx = get_answer_index(ans_text, raw_options)
                    
                    # Clean question text
                    q_text = escape_html(str(question).strip().replace('\n', ' '))
                    
                    # Determine which test this belongs to
                    if unit in unit_to_test:
                        test_key = unit_to_test[unit]
                    else:
                        test_key = 'T4'  # Rest goes to T4
                    
                    q_obj = {
                        "q": q_text,
                        "options": options,
                        "ans": ans_idx,
                        "unit": unit
                    }
                    
                    data[test_key].append(q_obj)
                    total_q += 1
    
    print(f"Total MCQs extracted: {total_q}")
    print(f"Skipped (non-MCQ/invalid): {skipped}")
    for key in ['T1', 'T2', 'T3', 'T4']:
        units_in = set(q['unit'] for q in data[key])
        print(f"  {key}: {len(data[key])} questions (units: {sorted(units_in)})")
    
    return data


# Define configurations for each subject
configs = {
    'dm': {
        'file': 'PB_DM_SEM-IV_2026.pdf',
        'tests': {
            'T1': ['1', '2', '3'],
            'T2': ['4', '5', '6'],
            'T3': ['7', '8'],
            'T4': 'rest'
        }
    },
    'coa': {
        'file': 'PB_COA_SEM-IV_2026.pdf',
        'tests': {
            'T1': ['1', '2', '3'],
            'T2': ['4', '5'],
            'T3': ['6', '7', '8'],
            'T4': 'rest'
        }
    },
    'python2': {
        'file': 'PB_Python-2_Sem-IV_2026.pdf',
        'tests': {
            'T1': ['1', '2', '3'],
            'T2': ['4', '5', '6'],
            'T3': ['7', '8'],
            'T4': 'rest'
        }
    },
    'fsd2': {
        'file': 'PB_FSD 2_SEM-IV_2026.pdf',
        'tests': {
            'T1': ['1', '2', '3'],
            'T2': ['4', '5', '6'],
            'T3': ['7', '8'],
            'T4': 'rest'
        }
    },
    'toc': {
        'file': 'PB_TOC_SEM-IV_2026.pdf',
        'tests': {
            'T1': ['1', '2', '3', '4'],
            'T2': ['5', '6'],
            'T3': ['7', '8'],
            'T4': 'rest'
        }
    }
}

# Extract all subjects
for subject, config in configs.items():
    data = extract_mcqs(config['file'], subject.upper(), config['tests'])
    
    output_path = f'questions/{subject}.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Saved to {output_path}")

print("\n\nAll subjects extracted successfully!")
