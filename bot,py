from flask import Flask, request, render_template, jsonify
import os
import json
import random
import datetime

# =====================
# PATH SETUP
# =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "..", "templates")

app = Flask(__name__, template_folder=TEMPLATE_DIR)

RULES_FILE = os.path.join(BASE_DIR, "rules.json")
LOG_FILE = os.path.join(BASE_DIR, "logs.json")
FOODS_FILE = os.path.join(BASE_DIR, "foods.json")  # optional dataset

# =====================
# LOAD RULES
# =====================
def load_rules():
    try:
        with open(RULES_FILE) as f:
            return json.load(f)
    except Exception as e:
        print("Error loading rules:", e)
        return {}

# =====================
# LOAD FOODS (OPTIONAL)
# =====================
def load_foods():
    try:
        with open(FOODS_FILE) as f:
            return json.load(f)
    except:
        return {}

# =====================
# LOGGING FUNCTION
# =====================
def log_interaction(user_input, bot_reply, status="matched"):
    try:
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w") as f:
                json.dump([], f)

        with open(LOG_FILE, "r+") as f:
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
# FIND DISH FUNCTION
# =====================
def find_dish(message, rules):
    message = message.lower()
    for dish in rules:
        if dish in message:
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
    rules = load_rules()
    data = request.json
    message = data.get("message", "").strip().lower()

    dish = find_dish(message, rules)

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
