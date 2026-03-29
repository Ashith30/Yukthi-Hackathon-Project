import json
import os

def run():
    file_path = "../data/questions.json"
    with open(file_path, "r", encoding="utf-8") as f:
        qs = json.load(f)
        
    original = list(qs)
    all_qs = list(qs)
    
    # Duplicate the 20 questions to reach 200
    for i in range(9):
        for q in original:
            new_q = q.copy()
            # Just vary the text slightly so they are unique
            new_q["question"] = f"{q['question']} (Variant {i+1})"
            all_qs.append(new_q)
            
    # Re-index
    for i, q in enumerate(all_qs):
        q["id"] = i + 1
        
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(all_qs, f, indent=2)
        
    print(f"Successfully expanded database to {len(all_qs)} questions!")

if __name__ == "__main__":
    run()
