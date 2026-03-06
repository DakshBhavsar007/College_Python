import pdfplumber
import json

# Analyze each PDF to understand column structure
pdf_files = [
    ('dm', 'PB_DM_SEM-IV_2026.pdf'),
    ('coa', 'PB_COA_SEM-IV_2026.pdf'),
    ('python2', 'PB_Python-2_Sem-IV_2026.pdf'),
    ('fsd2', 'PB_FSD 2_SEM-IV_2026.pdf'),
    ('toc', 'PB_TOC_SEM-IV_2026.pdf')
]

for subject, pdf_path in pdf_files:
    print(f"\n{'='*60}")
    print(f"Subject: {subject}")
    
    with pdfplumber.open(pdf_path) as pdf:
        # Just check page 1, table 0, first few data rows
        for pg in range(min(3, len(pdf.pages))):
            page = pdf.pages[pg]
            tables = page.extract_tables()
            if tables:
                table = tables[0]
                print(f"  Page {pg+1}: {len(table)} rows, cols={len(table[0]) if table else 0}")
                for r in range(min(4, len(table))):
                    row = table[r]
                    print(f"    Row {r} ({len(row)} cols):")
                    for c, val in enumerate(row):
                        short = str(val)[:50].replace('\n', ' ') if val else 'None'
                        print(f"      [{c}]: {short}")
                break  # Just first page with tables
