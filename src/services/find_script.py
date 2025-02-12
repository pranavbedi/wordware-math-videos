import json
import re
import sys
sys.stdout.reconfigure(encoding="utf-8")

def find_script(obj):
    """
    Recursively search through a nested dictionary/list structure
    to find a value corresponding to the key 'Script'.
    Returns the first match found. If none is found, returns None.
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "Clean Script" and isinstance(v, str):
                return v
            result = find_script(v)
            if result is not None:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = find_script(item)
            if result is not None:
                return result
    return None

def extract_script(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex to capture all top-level JSON chunks that start with '{' and end with '}'
    raw_objects = re.findall(r'(?s)\{.*?\}(?=\n\{|$)', content)
    script_code = None

    for obj_text in raw_objects:
        try:
            parsed = json.loads(obj_text)
        except json.JSONDecodeError:
            continue

        found_code = find_script(parsed)
        if found_code:
            script_code = found_code  # Overwrite to get the last occurrence

    if script_code:
        # Remove any segments enclosed in square brackets, e.g. [text]
        stripped_script = re.sub(r'\[.*?\]', '', script_code, flags=re.DOTALL)
        # Clean up any extra whitespace
        print(stripped_script.strip())
    else:
        print("No 'Script' was found in any parsed JSON object.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_script.py response.txt")
    else:
        extract_script(sys.argv[1])
