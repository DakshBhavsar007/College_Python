import pdfplumber

# Deep analyze DM structure
with pdfplumber.open('PB_DM_SEM-IV_2026.pdf') as pdf:
    for pg in range(min(5, len(pdf.pages))):
        page = pdf.pages[pg]
        tables = page.extract_tables()
        if not tables:
            print(f"Page {pg+1}: No tables")
            continue
        for t_idx, table in enumerate(tables):
            print(f"\nPage {pg+1}, Table {t_idx}: {len(table)} rows, {len(table[0]) if table else 0} cols")
            for r_idx, row in enumerate(table[:8]):
                if not row:
                    continue
                print(f"  Row {r_idx} ({len(row)} cols):")
                for c, val in enumerate(row):
                    if val:
                        short = str(val)[:80].replace('\n', '|')
                        print(f"    [{c}]: '{short}'")
