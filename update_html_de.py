
import json
import re

json_path = r"c:\Users\parul\Desktop\html\PythonMCQs\extracted_de.json"
html_path = r"c:\Users\parul\Desktop\html\PythonMCQs\index.html"

try:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Convert to JS object string (keys quoted)
    new_de_data = json.dumps(data, indent=4)

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 1. Inject Data into QUESTION_BANK
    # We need to add "de: { ... }" to QUESTION_BANK.
    # We can look for `python: { ... },` and append `de: ...` after it.
    
    # Locate the end of the python block.
    # It's safer to use a regex to find the `python: { ... }` block if we can,
    # or just find where `python` starts and find its matching brace?
    # Actually, `index.html` structure is:
    # const QUESTION_BANK = {
    #     python: { ... },
    #     fsd: { ... }
    # };
    # We'll insert `de` before the closing brace of QUESTION_BANK.
    
    # We can search for the last closing brace of QUESTION_BANK.
    # `const QUESTION_BANK = { ... };` capture the content inside.
    
    # Let's try to just insert it after `python: { ... },`
    # But `python` block is huge.
    
    # Strategy: Find `const QUESTION_BANK = {` and insert `de: ... ,` right after it?
    # Or find `};` that closes QUESTION_BANK?
    # Note: there might be other `};` in the file.
    
    # Let's use the fact that `python:` is there.
    # We can replace `const QUESTION_BANK = {` with `const QUESTION_BANK = {\n    de: ${new_de_data},`
    
    pattern_data = r'(const\s+QUESTION_BANK\s*=\s*\{)'
    # Escape backslashes for re.sub replacement string
    safe_de_data = new_de_data.replace('\\', '\\\\')
    replacement_data = f"const QUESTION_BANK = {{\n            de: {safe_de_data},"
    
    if "de: {" not in html_content:
        html_content = re.sub(pattern_data, replacement_data, html_content, count=1)
        print("Injected DE data.")
    else:
        print("DE data might already be present. Updating functionality only?")
        # If it is present, we might want to update it. 
        # For now, let's assume if it's there, we might be re-running.
        # Let's simple replace `de: { ... },` if it exists, or insert if not.
        pass

    # 2. Add DE to Menu
    # Search for: `selectSubject('python')` button in nav and add DE button.
    # Structure:
    # <button onclick="selectSubject('python')" ...> ... </button>
    # We can add DE button before or after.
    
    # We'll look for the python button in the nav and append DE button after it.
    nav_python_btn_regex = r'(<button onclick="selectSubject\(\'python\'\)"[\s\S]*?<\/button>)'
    
    de_nav_btn = """
                        <button onclick="selectSubject('de')"
                            class="text-left text-purple-600 font-semibold flex items-center gap-3 py-3 px-2 rounded hover:bg-purple-50 md:hover:bg-transparent">
                            <i class="fa-solid fa-microchip text-xl"></i> DE
                        </button>"""
                        
    # Check if already added
    if "selectSubject('de')" not in html_content:
        # Insert after Python button in Nav
        # Note: there are two python buttons (one in nav, one in home section).
        # The nav one is inside `<div id="nav-content" ...`
        # We can be specific.
        
        # Let's replace the one in the nav list.
        # Valid marker: `selectSubject('python')` followed by `selectSubject('fsd')` (which is commented out).
        
        # Insert before the FSD button (even if commented) or after Python.
        html_content = re.sub(nav_python_btn_regex, f"\\1{de_nav_btn}", html_content, count=1) 
        # count=1 only replaces the first occurrence? 
        # The first occurrence is primarily the NAV button as it appears earlier in file (line 166) vs Home (line 194).
        print("Added DE to Nav.")

    # 3. Add DE Card to Home Section
    # Find the python card and insert DE card after it.
    # The python card has `onclick="selectSubject('python')"` and `class="... hover-card ..."`
    
    # We can look for the Python card specifically in the home section.
    # It's inside `<div class="flex flex-col md:flex-row ... max-w-5xl mx-auto">`
    
    de_home_card = """
                <button onclick="selectSubject('de')"
                    class="w-full md:w-80 text-center glass hover-card rounded-3xl p-12 md:p-14 group relative overflow-hidden focus:outline-none transform transition-all duration-300 hover:scale-105 border border-purple-500/20">
                    <div
                        class="absolute top-0 right-0 w-48 h-48 bg-purple-500/15 rounded-full blur-3xl -mr-20 -mt-20 group-hover:bg-purple-500/25 transition-all duration-300">
                    </div>
                    <div
                        class="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-all duration-300 rounded-3xl">
                    </div>
                    <div class="relative z-10 flex flex-col items-center text-center">
                        <div
                            class="w-28 h-28 bg-gradient-to-br from-purple-400/30 to-purple-600/20 rounded-2xl flex items-center justify-center mb-6 shadow-xl border-2 border-purple-500/40 group-hover:border-purple-500/70 transition-all duration-300">
                            <i
                                class="fa-solid fa-microchip text-6xl text-purple-600 group-hover:scale-110 transition-transform duration-300"></i>
                        </div>
                        <h2
                            class="text-4xl font-black text-gray-900 mb-3 group-hover:text-purple-700 transition-colors duration-300">
                            DE</h2>
                        <p class="text-gray-700 text-base mb-6 font-semibold">View & Test (T1 - T4)</p>
                        <span
                            class="text-purple-700 font-bold text-base bg-gradient-to-r from-purple-400/30 to-purple-400/15 px-6 py-3 rounded-full border-2 border-purple-500/40 group-hover:border-purple-500/70 group-hover:bg-purple-400/30 transition-all duration-300">Enter
                            &rarr;</span>
                    </div>
                </button>
    """
    
    # The home card is the SECOND occurrence of `selectSubject('python')`.
    # Let's find it by looking for the card classes.
    python_card_marker = 'onclick="selectSubject(\'python\')"'
    
    # Find all occurrences
    matches = [m.start() for m in re.finditer(re.escape(python_card_marker), html_content)]
    
    if len(matches) >= 2:
        # The second match should be the home card.
        # We want to insert AFTER the closing </button> of this card.
        # Find the closing </button> after the second match.
        idx = matches[1]
        closing_tag = "</button>"
        end_idx = html_content.find(closing_tag, idx) + len(closing_tag)
        
        # Check if DE card is already there (look ahead)
        if "selectSubject('de')" not in html_content[end_idx:end_idx+500]:
            html_content = html_content[:end_idx] + "\n" + de_home_card + html_content[end_idx:]
            print("Added DE to Home.")

    # 4. Update selectSubject function color logic
    # Line 6342: `class="text-${subject === 'python' ? 'yellow' : 'blue'}-400 ...`
    # We need to handle 'de' (purple).
    # Regex replace the ternary with a function call or nested ternary?
    # Or just replace the line.
    
    old_color_logic = r"subject === 'python' \? 'yellow' : 'blue'"
    new_color_logic = "subject === 'python' ? 'yellow' : (subject === 'de' ? 'purple' : 'blue')"
    
    html_content = re.sub(re.escape(old_color_logic), new_color_logic, html_content)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print("Updated index.html successfully.")

except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error updating HTML: {e}")
