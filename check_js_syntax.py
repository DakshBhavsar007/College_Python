from bs4 import BeautifulSoup
import json
import re

try:
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract JSON object from script
    match = re.search(r'const QUESTION_BANK = ({.*});', content, re.DOTALL)
    if match:
        json_str = match.group(1)
        # Javascript object keys might not be quoted, requiring loose parsing or cleanup
        # But here I generated it, so it should be valid JSON mostly.
        # However, the previous integration script simply wrote the dict str(). 
        # Python dict str() uses single quotes! JSON requires double quotes.
        # THIS IS THE PROBLEM!
        
        # Valid JSON: {"key": "value"}
        # Python dict string: {'key': 'value'}
        
        # Let's check if the file uses single quotes.
        print("First 100 chars of JSON:", json_str[:200])
        
    else:
        print("Could not find QUESTION_BANK variable.")

except Exception as e:
    print(e)
