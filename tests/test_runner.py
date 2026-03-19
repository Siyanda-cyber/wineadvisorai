import requests
import json

URL = "http://127.0.0.1:5000/chat"

with open("test_cases.json") as f:
    tests = json.load(f)

for test in tests:
    res = requests.post(URL, json={"message": test["input"]})
    reply = res.json()["reply"]

    passed = test["expected"].lower() in reply.lower()

    print("INPUT:", test["input"])
    print("EXPECTED:", test["expected"])
    print("BOT:", reply)
    print("PASS" if passed else "FAIL")
    print("-" * 40)
