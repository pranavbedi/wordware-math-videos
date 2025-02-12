import json
import re
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

def find_manim_code(obj):
    """
    Recursively search through a nested dictionary/list structure
    to find a string that contains "from manim import *".
    Returns the first match found. If none is found, returns None.
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and "from manim import *" in v:
                return v  # Found a string that looks like a Manim script.
            # Otherwise, search deeper.
            result = find_manim_code(v)
            if result is not None:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = find_manim_code(item)
            if result is not None:
                return result
    return None

def clean_extracted_code(code: str) -> str:
    """
    Removes any leading/trailing code fence markers (like ``` or ```python)
    from the extracted code.
    """
    lines = code.splitlines()
    cleaned_lines = []
    for line in lines:
        # Skip lines that start with ``` (case-insensitive)
        if line.strip().lower().startswith("```"):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

def replace_tex_keywords(code: str) -> str:
    """
    Replaces any occurrence of 'tex', 'latex', or 'mathtex' (case-insensitive)
    with 'Text' in the provided code.
    """
    # The regex \b ensures we match whole words only.
    pattern = r'(?i)\b(tex|latex|mathtex)\b'
    return re.sub(pattern, 'Text', code, flags=re.IGNORECASE)

def extract_manim_code(file_path):
    """
    Reads the entire file content from response.txt and extracts
    the Manim Python code by searching for any string that contains
    "from manim import *". The extracted code is printed with its
    original newline characters preserved (but without code fences).
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Use regex to capture all top-level JSON chunks.
    raw_objects = re.findall(r'(?s)\{.*?\}(?=\n\{|$)', content)

    manim_code = None

    # Process each JSON chunk.
    for obj_text in raw_objects:
        try:
            parsed = json.loads(obj_text)
        except json.JSONDecodeError:
            # Skip if this chunk isn't valid JSON.
            continue

        # Recursively search for the Manim code in this JSON object.
        found_code = find_manim_code(parsed)
        if found_code:
            manim_code = found_code
            break  # Stop at the first match.

    if manim_code:
        cleaned_code = clean_extracted_code(manim_code)
        # Replace keywords: any mention of tex, latex, or mathtex becomes "Text"
        replaced_code = replace_tex_keywords(cleaned_code)
        sys.stdout.write(replaced_code)
    else:
        sys.stdout.write("No Manim code was found in any parsed JSON object.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stdout.write("Usage: python extract_manim_code.py response.txt")
    else:
        extract_manim_code(sys.argv[1])
