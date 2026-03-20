import requests
import json

URL = "http://127.0.0.1:5000/chat"

with open("test_cases.json") as f:
    tests = json.load(f)

passed_count = 0

for test in tests:

    # ✅ THIS MUST COME FIRST
    res = requests.post(URL, json={"message": test["input"]})

    # ✅ DEBUG PRINT (AFTER res exists)
    print("RAW RESPONSE:", res.json())

    reply = res.json()["reply"]

    passed = test["expected"].lower() in reply.lower()

    if passed:
        passed_count += 1

    print("INPUT:", test["input"])
    print("EXPECTED:", test["expected"])
    print("BOT:", reply)
    print("PASS" if passed else "FAIL")
    print("-" * 40)

accuracy = (passed_count / len(tests)) * 100
print(f"\nACCURACY: {accuracy:.2f}%")
