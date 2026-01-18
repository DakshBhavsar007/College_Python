
import json
import re

json_path = r"c:\Users\parul\Desktop\html\PythonMCQs\extracted_python.json"
html_path = r"c:\Users\parul\Desktop\html\PythonMCQs\index.html"

try:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Convert to a JS-like string (though valid JSON is also valid JS object, 
    # but we want to match the style if possible, or just use JSON)
    # The existing code has keys without quotes: { q: "...", options: [...], ans: 1 }
    # Standard JSON: { "q": "...", "options": [...], "ans": 1 }
    # JS parsers allow quoted keys, so standardized JSON is fine.
    
    # We'll just format it nicely.
    new_python_data = json.dumps(data, indent=4)
    # json.dumps puts quotes around keys. valid for JS.

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Regex to find python: { ... } inside QUESTION_BANK
    # We look for `python: {` followed by anything until `fsd:` or end of object.
    # Actually, `index.html` structure:
    # const QUESTION_BANK = {
    #     python: {
    #         ...
    #     },
    #     fsd: {
    #         ...
    #     }
    # };
    
    # We replace everything from `python: {` to the matching closing brace.
    # Or simpler: replace `python: { ... }` where `...` goes until `},` before `fsd:`
    
    # Let's try a regex that captures the python block
    # Pattern: python:\s*\{(?:[^{}]|{[^{}]*})*\}
    # This handles one level of nesting, but MCQs have arrays of objects.
    
    # Alternative: construct the NEW python block and find where it fits.
    # We know `python:` starts the block.
    # We know `fsd:` starts the next block.
    # So we can replace everything between `python:` and `fsd:`
    
    pattern = r'(python:\s*\{[\s\S]*?)(,\s*fsd:)'
    # This matches from python: { ... until , fsd:
    
    # Replacement:
    # python: <new_json_data>
    
    replacement = f"python: {new_python_data}"
    # Escape backslashes for re.sub because it processes escapes in the replacement string
    replacement = replacement.replace('\\', '\\\\')
    
    new_html_content = re.sub(pattern, f"{replacement}\\2", html_content, count=1)
    
    # If fsd is not there (temp hidden as per comments in HTML file), we might need another anchor.
    # Looking at file: fsd IS there in the JS object.
    # 402: python: {
    # ...
    # 419: },
    # 420: fsd: {
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html_content)

    print("Updated index.html successfully.")

except Exception as e:
    print(f"Error updating HTML: {e}")
