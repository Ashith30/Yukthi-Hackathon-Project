import os
import json
from dotenv import load_dotenv

load_dotenv()

from services.decision_service import get_finance_decision

print("TESTING FINANCE DECISION 1:")
result = get_finance_decision("SIP vs lumpsum investment", {"personality_type": "Analyzer"})
print(json.dumps(result, indent=2))

print("\n\nTESTING FINANCE DECISION 2:")
result2 = get_finance_decision("Emergency fund — how much?", {"personality_type": "Analyzer"})
print(json.dumps(result2, indent=2))
