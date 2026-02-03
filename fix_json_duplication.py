
try:
    with open('index.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Targets (1-based to 0-based)
    start_idx = 7810 - 1
    end_idx = 15112 - 1

    # Verify content to be extremely safe
    print(f"Line {start_idx+1}: {lines[start_idx].strip()}")
    print(f"Line {end_idx+1}: {lines[end_idx].strip()}")

    if "etc: {" not in lines[start_idx]:
        print("Mismatch at start index!")
        # Try searching nearby
        for i in range(start_idx-10, start_idx+10):
            if "etc: {" in lines[i]:
                print(f"Found etc: {{ at {i+1}")
                start_idx = i
                break
    
    if "de: {" not in lines[end_idx]:
        print("Mismatch at end index!")
         # Try searching nearby
        for i in range(end_idx-10, end_idx+10):
            if "de: {" in lines[i]:
                print(f"Found de: {{ at {i+1}")
                end_idx = i
                break

    if "etc: {" in lines[start_idx] and "de: {" in lines[end_idx]:
        new_lines = lines[:start_idx] + lines[end_idx:]
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print("Successfully removed duplicate blocks.")
    else:
        print("Aborting due to mismatch.")

except Exception as e:
    print(f"Error: {e}")
