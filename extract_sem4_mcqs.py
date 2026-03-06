import PyPDF2
import re
import json
import html
import os

def extract_text_from_pdf(pdf_path):
    """Extract all text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text

def clean_text(text):
    """Clean and normalize text."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def escape_html(text):
    """Escape HTML special characters."""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#39;')
    return text

def parse_mcqs_from_text(text, subject_name):
    """Parse MCQs from extracted PDF text - handles multiple formats."""
    questions = []
    
    # Try to find questions using various patterns
    # Pattern 1: Numbered questions like "1." or "1)" or "Q1." or "Q.1"
    # We'll split by question numbers
    
    # First, let's try to identify the unit/chapter markers
    # Common patterns: "Unit 1", "Chapter 1", "UNIT-1", "Unit - 1", "UNIT 1"
    
    lines = text.split('\n')
    full_text = text
    
    # Try to find MCQs with numbered patterns
    # Pattern: number followed by question text, then options a/b/c/d or A/B/C/D or 1/2/3/4
    
    # Split text into potential question blocks
    # Look for patterns like "1.", "2.", "Q1.", "Q.1", "1)", etc.
    question_pattern = re.compile(
        r'(?:^|\n)\s*(?:Q\.?\s*)?(\d+)\s*[.)]\s*(.*?)(?=(?:\n\s*(?:Q\.?\s*)?\d+\s*[.)]|\Z))',
        re.DOTALL
    )
    
    # Also try unit detection
    unit_pattern = re.compile(
        r'(?:Unit|UNIT|Chapter|CHAPTER|unit)\s*[-:]?\s*(\d+)',
        re.IGNORECASE
    )
    
    # Find all unit markers and their positions
    unit_markers = []
    for match in unit_pattern.finditer(full_text):
        unit_markers.append((match.start(), match.group(1)))
    
    def get_unit_for_position(pos):
        """Determine which unit a position belongs to."""
        current_unit = "1"
        for marker_pos, unit_num in unit_markers:
            if marker_pos <= pos:
                current_unit = unit_num
            else:
                break
        return current_unit
    
    # Try multiple extraction strategies
    
    # Strategy 1: Look for question-option-answer pattern
    # Questions like: "1. question text\na) option1\nb) option2\nc) option3\nd) option4\nAnswer: a"
    
    # First detect the answer format
    answer_patterns = [
        r'(?:Answer|Ans|ANSWER|ANS|Correct\s*Answer|correct\s*answer)\s*[:.-]?\s*(?:\(?\s*)?([abcdABCD1234])',
        r'(?:Answer|Ans|ANSWER|ANS)\s*[:.-]?\s*(?:\(?\s*)?([abcdABCD1234])\s*\)',
    ]
    
    # Let's try a more robust approach
    # Split the entire text by question numbers
    
    # Clean up the text first
    clean = full_text
    
    # Try to extract using a very flexible pattern
    # Look for blocks that have: question number, question text, 4 options, and possibly an answer
    
    # Pattern for options: a), b), c), d) or A), B), C), D) or (a), (b), (c), (d)
    option_patterns = [
        # a) b) c) d) format
        r'(?:\(?[aA]\)?[.)]\s*)(.*?)(?:\(?[bB]\)?[.)]\s*)(.*?)(?:\(?[cC]\)?[.)]\s*)(.*?)(?:\(?[dD]\)?[.)]\s*)(.*?)(?=(?:\n\s*(?:Q\.?\s*)?\d+[.)]|Answer|Ans|ANSWER|ANS|$))',
        # (a) (b) (c) (d) format with various separators
        r'\(a\)\s*(.*?)\s*\(b\)\s*(.*?)\s*\(c\)\s*(.*?)\s*\(d\)\s*(.*?)(?=(?:\d+[.)]|Answer|Ans|$))',
        # A. B. C. D. format
        r'(?:A[.)]\s*)(.*?)(?:B[.)]\s*)(.*?)(?:C[.)]\s*)(.*?)(?:D[.)]\s*)(.*?)(?=(?:\d+[.)]|Answer|Ans|$))',
    ]
    
    print(f"\n{'='*60}")
    print(f"Processing: {subject_name}")
    print(f"Text length: {len(full_text)} characters")
    print(f"Found {len(unit_markers)} unit markers")
    if unit_markers:
        for pos, unit in unit_markers:
            context = full_text[max(0,pos-20):pos+50].replace('\n', ' ')
            print(f"  Unit {unit} at position {pos}: ...{context}...")
    
    # Let's try a simpler approach: split by question numbers and parse each block
    # First, find all question starts
    q_starts = list(re.finditer(r'(?:^|\n)\s*(?:Q\.?\s*)?(\d+)\s*[.)]\s*', full_text))
    
    print(f"Found {len(q_starts)} potential question starts")
    
    if len(q_starts) < 5:
        # Try alternate pattern
        q_starts = list(re.finditer(r'(?:^|\n)\s*(\d+)\s*[.)]\s*', full_text))
        print(f"Alternate pattern found {len(q_starts)} question starts")
    
    for i, q_match in enumerate(q_starts):
        q_num = int(q_match.group(1))
        q_start = q_match.end()
        q_end = q_starts[i+1].start() if i+1 < len(q_starts) else len(full_text)
        
        block = full_text[q_start:q_end].strip()
        
        if len(block) < 20:  # Too short to be a valid question
            continue
            
        # Determine unit
        unit = get_unit_for_position(q_match.start())
        
        # Try to find options in this block
        options = []
        question_text = ""
        answer_idx = -1
        
        # Try different option formats
        # Format 1: a) b) c) d) or (a) (b) (c) (d)
        opt_match = re.search(
            r'(.*?)(?:\(?[aA]\)?\s*[.)]\s*|\(a\)\s*)(.*?)(?:\(?[bB]\)?\s*[.)]\s*|\(b\)\s*)(.*?)(?:\(?[cC]\)?\s*[.)]\s*|\(c\)\s*)(.*?)(?:\(?[dD]\)?\s*[.)]\s*|\(d\)\s*)(.*)',
            block, re.DOTALL
        )
        
        if not opt_match:
            # Format 2: A. B. C. D. or A) B) C) D)
            opt_match = re.search(
                r'(.*?)\s*[Aa][.)]\s*(.*?)\s*[Bb][.)]\s*(.*?)\s*[Cc][.)]\s*(.*?)\s*[Dd][.)]\s*(.*)',
                block, re.DOTALL
            )
        
        if opt_match:
            question_text = opt_match.group(1).strip()
            opt_a = opt_match.group(2).strip()
            opt_b = opt_match.group(3).strip()
            opt_c = opt_match.group(4).strip()
            opt_d = opt_match.group(5).strip()
            
            # Clean up options - remove answer text from last option
            for ans_pat in answer_patterns:
                for opt_text in [opt_d, opt_c, opt_b, opt_a]:
                    ans_match = re.search(ans_pat, opt_text)
                    if ans_match:
                        answer_letter = ans_match.group(1).lower()
                        if answer_letter in 'abcd':
                            answer_idx = 'abcd'.index(answer_letter)
                        elif answer_letter in '1234':
                            answer_idx = int(answer_letter) - 1
                        break
                if answer_idx >= 0:
                    break
            
            # Also check for answer after options block
            if answer_idx < 0:
                ans_in_block = re.search(
                    r'(?:Answer|Ans|ANSWER|ANS|Correct\s*Answer)\s*[:.-]?\s*(?:\(?\s*)?([abcdABCD1234])',
                    block
                )
                if ans_in_block:
                    al = ans_in_block.group(1).lower()
                    if al in 'abcd':
                        answer_idx = 'abcd'.index(al)
                    elif al in '1234':
                        answer_idx = int(al) - 1
            
            # Clean up option texts - remove answer markers
            for ans_pat in answer_patterns:
                opt_d = re.sub(ans_pat + r'.*$', '', opt_d, flags=re.DOTALL).strip()
            
            # Remove trailing answer patterns from options
            for pat in [r'\s*(?:Answer|Ans|ANSWER|ANS).*$', r'\s*Correct\s*Answer.*$']:
                opt_a = re.sub(pat, '', opt_a, flags=re.DOTALL).strip()
                opt_b = re.sub(pat, '', opt_b, flags=re.DOTALL).strip()
                opt_c = re.sub(pat, '', opt_c, flags=re.DOTALL).strip()
                opt_d = re.sub(pat, '', opt_d, flags=re.DOTALL).strip()
            
            options = [opt_a, opt_b, opt_c, opt_d]
            
            # Clean up options - remove newlines
            options = [re.sub(r'\s+', ' ', o).strip() for o in options]
            question_text = re.sub(r'\s+', ' ', question_text).strip()
            
            # Skip if question text is too short or options are empty
            if len(question_text) < 5:
                continue
            if any(len(o) == 0 for o in options):
                continue
            
            # If no answer found, default to 0 (we'll mark it)
            if answer_idx < 0:
                answer_idx = 0  # Default
            
            # Escape HTML
            question_text = escape_html(question_text)
            options = [escape_html(o) for o in options]
            
            questions.append({
                "q": question_text,
                "options": options,
                "ans": answer_idx,
                "unit": unit
            })
    
    print(f"Extracted {len(questions)} questions for {subject_name}")
    
    # Show unit distribution
    unit_counts = {}
    for q in questions:
        u = q['unit']
        unit_counts[u] = unit_counts.get(u, 0) + 1
    print(f"Unit distribution: {unit_counts}")
    
    return questions


def organize_into_tests(questions, subject_name, test_config):
    """
    Organize questions into T1, T2, T3, T4 based on unit assignments.
    test_config is a dict like: {'T1': ['1','2','3'], 'T2': ['4','5','6'], 'T3': ['7','8'], 'T4': 'rest'}
    """
    result = {}
    assigned_units = set()
    
    for test_name, units in test_config.items():
        if units == 'rest':
            continue
        assigned_units.update(units)
        test_questions = [q for q in questions if q['unit'] in units]
        result[test_name] = test_questions
    
    # T4 gets the rest
    if 'T4' in test_config and test_config['T4'] == 'rest':
        rest_questions = [q for q in questions if q['unit'] not in assigned_units]
        result['T4'] = rest_questions
    
    # Print summary
    print(f"\n{subject_name} Test Distribution:")
    for t, qs in result.items():
        units_in_test = set(q['unit'] for q in qs)
        print(f"  {t}: {len(qs)} questions (units: {sorted(units_in_test)})")
    
    return result


# Define PDF files and their configurations
pdf_configs = {
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

# First, let's just extract and print text structure from each PDF
for subject, config in pdf_configs.items():
    pdf_path = config['file']
    if not os.path.exists(pdf_path):
        print(f"WARNING: {pdf_path} not found!")
        continue
    
    text = extract_text_from_pdf(pdf_path)
    
    # Save raw text for debugging
    with open(f'raw_text_{subject}.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    
    # Show first 2000 chars to understand format
    print(f"\n{'='*60}")
    print(f"SUBJECT: {subject.upper()}")
    print(f"File: {pdf_path}")
    print(f"Total text length: {len(text)}")
    print(f"First 2000 chars:")
    print(text[:2000])
    print(f"\n...")
    print(f"Last 500 chars:")
    print(text[-500:])

print("\n\nDone extracting raw text. Check raw_text_*.txt files for full content.")
