import os
import json
from app import bot

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_FILE = os.path.join(BASE_DIR, "test_cases.json")

with open(TEST_FILE) as f:
    test_cases = json.load(f)

rules = bot.load_rules()

def simulate_chat(message):
    return bot.find_dish(message, rules)

passed = 0
failed = 0

for case in test_cases:
    input_msg = case["input"]
    expected = case["expected_dish"]

    result = simulate_chat(input_msg)

    if result == expected:
        print(f"✅ PASS | {input_msg} → {result}")
        passed += 1
    else:
        print(f"❌ FAIL | {input_msg}")
        print(f"   Expected: {expected}, Got: {result}")
        failed += 1

print("\n====================")
print(f"RESULT: {passed} passed, {failed} failed")
print("====================")
