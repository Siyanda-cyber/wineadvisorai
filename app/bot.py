from flask import Flask, request, render_template, jsonify
import os
import json
import random
import datetime
import re

# =====================
# PATH SETUP
# =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # app/
TEMPLATE_DIR = os.path.join(BASE_DIR, "..", "templates")  # templates/ at project root
RULES_FILE = os.path.join(BASE_DIR, "rules.json")        # wine pairing rules
SYN_FILE = os.path.join(BASE_DIR, "synonyms.json")      # synonyms file
LOG_FILE = os.path.join(BASE_DIR, "logs.json")

app = Flask(__name__, template_folder=TEMPLATE_DIR)

# =====================
# LOAD JSON FILES
# =====================
def load_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

rules = load_json(RULES_FILE)
synonyms = load_json(SYN_FILE)

# =====================
# LOGGING FUNCTION
# =====================
def log_interaction(user_input, bot_reply, status="matched"):
    try:
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w") as f:
                json.dump([], f)

        with open(LOG_FILE, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.append({
                "input": user_input,
                "reply": bot_reply,
                "status": status,
                "time": str(datetime.datetime.now())
            })
            f.seek(0)
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Logging error:", e)

# =====================
# FIND DISH FUNCTION WITH SYNONYMS
# =====================
def find_dish(message, rules, synonyms):
    """
    Find the dish by matching message to either the dish name
    or any of its synonyms.
    """
    message = message.lower()
    # Remove punctuation
    message = re.sub(r'[^\w\s]', '', message)
    # Check direct dish match
    for dish in rules:
        if dish.lower() in message:
            return dish
    # Check synonyms
    for dish, syn_list in synonyms.items():
        for syn in syn_list:
            syn_clean = syn.lower()
            if syn_clean in message:
                return dish
    return None

# =====================
# GOOFY PERSONALITY
# =====================
def get_intro():
    return random.choice([
        "Goofy here! 🍷 Let’s talk South African food!",
        "Ahh my friend! Goofy knows these flavors well 🍷",
        "Now that is a proper South African meal! 🇿🇦",
    ])

# =====================
# HOME ROUTE
# =====================
@app.route("/")
def home():
    return render_template("index.html")

# =====================
# CHAT ENDPOINT
# =====================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "").strip()

    dish = find_dish(message, rules, synonyms)

    if dish:
        wine = random.choice(rules[dish])
        reply = (
            f"{get_intro()}\n\n"
            f"You're enjoying **{dish.title()}**!\n\n"
            f"That pairs beautifully with:\n"
            f"👉 {wine} 🍷\n\n"
            f"South African food + wine = magic 🇿🇦"
        )
        log_interaction(message, reply, "matched")
        return jsonify({"reply": reply})

    fallback = (
        "Goofy says: I’m still learning that dish 🍷\n\n"
        "Try: pap, bobotie, stew or kota!"
    )
    log_interaction(message, fallback, "unknown")
    return jsonify({"reply": fallback})

# =====================
# RUN LOCAL OR RENDER
# =====================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)