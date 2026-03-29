import json
import re
import os

def run():
    file_path = "data/questions.json"
    with open(file_path, "r", encoding="utf-8") as f:
        qs = json.load(f)
        
    for q in qs:
        # Remove (Variant X) from the question text using regex
        q["question"] = re.sub(r'\s*\(Variant \d+\)', '', q["question"])
            
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(qs, f, indent=2)
        
    print(f"Sanitized {len(qs)} questions successfully.")

if __name__ == "__main__":
    run()
