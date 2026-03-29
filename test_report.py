import sys
import json
import traceback

sys.path.append('.')

from services.personality_service import generate_personality_report

def run_test():
    answers = [
        {"question": "Q1", "answer": "A1"},
        {"question": "Q2", "answer": "A2"}
    ]
    try:
        report = generate_personality_report(answers, "Test User")
        print("Success!")
        print(json.dumps(report, indent=2))
    except Exception as e:
        print("Failed!")
        traceback.print_exc()

if __name__ == '__main__':
    run_test()
