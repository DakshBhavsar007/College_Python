
import json
import re

html_path = r"c:\Users\parul\Desktop\html\PythonMCQs\index.html"
etc_json_path = r"c:\Users\parul\Desktop\html\PythonMCQs\extracted_etc.json"
ci_json_path = r"c:\Users\parul\Desktop\html\PythonMCQs\extracted_ci.json"

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

print("Loading data...")
etc_data = load_json(etc_json_path)
ci_data = load_json(ci_json_path)

print("Reading HTML...")
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# 1. Update QUESTION_BANK
print("Updating QUESTION_BANK...")
# Find the start of QUESTION_BANK
qb_match = re.search(r'const QUESTION_BANK = \{', html_content)
if not qb_match:
    print("Error: QUESTION_BANK not found!")
    exit(1)

# we will inject the new keys after 'const QUESTION_BANK = {'
injection_point = qb_match.end()

# Prepare new JSON strings (keys only)
etc_str = f"\n            etc: {json.dumps(etc_data, indent=4)},\n"
ci_str = f"            ci: {json.dumps(ci_data, indent=4)},\n"

# Insert
new_html = html_content[:injection_point] + etc_str + ci_str + html_content[injection_point:]


# 2. Update Navbar
print("Updating Navbar...")
# Find <button onclick="selectSubject('de')" ... </button>
# logic: find the closing of DE button and append ETC and CI buttons
nav_regex = r'(<button onclick="selectSubject\(\'de\'\)"[\s\S]*?<\/button>)'
nav_match = re.search(nav_regex, new_html)

if nav_match:
    nav_end = nav_match.end()
    
    new_nav_buttons = """
                        <button onclick="selectSubject('etc')"
                            class="text-left text-green-600 font-semibold flex items-center gap-3 py-3 px-2 rounded hover:bg-green-50 md:hover:bg-transparent">
                            <i class="fa-solid fa-signal text-xl"></i> ETC
                        </button>
                        <button onclick="selectSubject('ci')"
                            class="text-left text-orange-600 font-semibold flex items-center gap-3 py-3 px-2 rounded hover:bg-orange-50 md:hover:bg-transparent">
                            <i class="fa-solid fa-scale-balanced text-xl"></i> CI
                        </button>"""
    
    new_html = new_html[:nav_end] + new_nav_buttons + new_html[nav_end:]
else:
    print("Warning: Navbar DE button not found, skipping navbar update.")


# 3. Update Home Cards
print("Updating Home Cards...")
# Find the DE card container and append after it.
# The DE card looks like <button onclick="selectSubject('de')" ... class="w-full md:w-80 ..."> ... </button>
# This regex is tricky because of nested divs.
# We can search for the specific text inside the card: "View & Test (T1 - T4)" inside the DE button.

# Let's find the closing tag of the DE button.
# Assume the DE button ends before the FSD button comment or the next button.
# Look for "<!-- FSD card temporarily hidden" or just append to the container.
# The container is <div class="flex flex-col md:flex-row ... max-w-5xl mx-auto">
# We can try to insert before the closing </div> of that container?
# But there might be commented out FSD card.
# Let's target the DE button specifically.

de_card_pattern = r'(<button onclick="selectSubject\(\'de\'\)"[\s\S]*?<\/button>\s*)'
# This greedy match might eat too much if not careful.
# Better to find the specific unique content of DE card and then find the next </button>
de_content_idx = new_html.find("onclick=\"selectSubject('de')\"")
if de_content_idx != -1:
    # Find the closing </button> for this tag.
    # It must be a balanced match, which is hard with regex. 
    # But indentation helps?
    # Or counts.
    # Simple hack: split by "onclick="selectSubject" to isolate blocks.
    pass

# Alternative: Replace the commented FSD card with ETC and CI cards?
# Or just insert before "<!-- FSD card temporarily hidden"
start_marker = "<!-- FSD card temporarily hidden"
marker_idx = new_html.find(start_marker)

if marker_idx != -1:
    # Insert before the comment
    cards_html = """
                <button onclick="selectSubject('etc')"
                    class="w-full md:w-80 text-center glass hover-card rounded-3xl p-12 md:p-14 group relative overflow-hidden focus:outline-none transform transition-all duration-300 hover:scale-105 border border-green-500/20">
                    <div
                        class="absolute top-0 right-0 w-48 h-48 bg-green-500/15 rounded-full blur-3xl -mr-20 -mt-20 group-hover:bg-green-500/25 transition-all duration-300">
                    </div>
                    <div
                        class="absolute inset-0 bg-gradient-to-br from-green-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-all duration-300 rounded-3xl">
                    </div>
                    <div class="relative z-10 flex flex-col items-center text-center">
                        <div
                            class="w-28 h-28 bg-gradient-to-br from-green-400/30 to-green-600/20 rounded-2xl flex items-center justify-center mb-6 shadow-xl border-2 border-green-500/40 group-hover:border-green-500/70 transition-all duration-300">
                            <i
                                class="fa-solid fa-signal text-6xl text-green-600 group-hover:scale-110 transition-transform duration-300"></i>
                        </div>
                        <h2
                            class="text-4xl font-black text-gray-900 mb-3 group-hover:text-green-700 transition-colors duration-300">
                            ETC</h2>
                        <p class="text-gray-700 text-base mb-6 font-semibold">View & Test (T1 - T2)</p>
                        <span
                            class="text-green-700 font-bold text-base bg-gradient-to-r from-green-400/30 to-green-400/15 px-6 py-3 rounded-full border-2 border-green-500/40 group-hover:border-green-500/70 group-hover:bg-green-400/30 transition-all duration-300">Enter
                            &rarr;</span>
                    </div>
                </button>

                <button onclick="selectSubject('ci')"
                    class="w-full md:w-80 text-center glass hover-card rounded-3xl p-12 md:p-14 group relative overflow-hidden focus:outline-none transform transition-all duration-300 hover:scale-105 border border-orange-500/20">
                    <div
                        class="absolute top-0 right-0 w-48 h-48 bg-orange-500/15 rounded-full blur-3xl -mr-20 -mt-20 group-hover:bg-orange-500/25 transition-all duration-300">
                    </div>
                    <div
                        class="absolute inset-0 bg-gradient-to-br from-orange-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-all duration-300 rounded-3xl">
                    </div>
                    <div class="relative z-10 flex flex-col items-center text-center">
                        <div
                            class="w-28 h-28 bg-gradient-to-br from-orange-400/30 to-orange-600/20 rounded-2xl flex items-center justify-center mb-6 shadow-xl border-2 border-orange-500/40 group-hover:border-orange-500/70 transition-all duration-300">
                            <i
                                class="fa-solid fa-scale-balanced text-6xl text-orange-600 group-hover:scale-110 transition-transform duration-300"></i>
                        </div>
                        <h2
                            class="text-4xl font-black text-gray-900 mb-3 group-hover:text-orange-700 transition-colors duration-300">
                            CI</h2>
                        <p class="text-gray-700 text-base mb-6 font-semibold">View & Test (T1 - T4)</p>
                        <span
                            class="text-orange-700 font-bold text-base bg-gradient-to-r from-orange-400/30 to-orange-400/15 px-6 py-3 rounded-full border-2 border-orange-500/40 group-hover:border-orange-500/70 group-hover:bg-orange-400/30 transition-all duration-300">Enter
                            &rarr;</span>
                    </div>
                </button>
    """
    new_html = new_html[:marker_idx] + cards_html + new_html[marker_idx:]
else:
    print("Warning: FSD card comment not found, skipping cards update.")

print("Writing updated index.html...")
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_html)

print("Done.")
