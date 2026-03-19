from flask import Flask, request, render_template, jsonify
import random
import json
import datetime

app = Flask(__name__, template_folder="templates")

# =====================
# LOAD RULES
# =====================
def load_rules():
    try:
        with open("rules.json") as f:
            return json.load(f)
    except:
        return {}

wine_pairs = load_rules()

# =====================
# LOGGING FUNCTION
# =====================
def log_interaction(user_input, bot_reply, status="matched"):
    try:
        with open("logs.json", "r+") as f:
            data = json.load(f)
            data.append({
                "input": user_input,
                "reply": bot_reply,
                "status": status,
                "time": str(datetime.datetime.now())
            })
            f.seek(0)
            json.dump(data, f, indent=2)
    except:
        # create file if it doesn't exist
        with open("logs.json", "w") as f:
            json.dump([], f)

# =====================
# HELPER: FIND MATCH
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
# LANDING PAGE
# =====================
@app.route("/")
def home():
    return render_template("index.html")

# =====================
# CHAT ENDPOINT
# =====================
@app.route("/chat", methods=["POST"])
def chat():

    global wine_pairs
    wine_pairs = load_rules()  # reload rules dynamically

    data = request.json
    message = data.get("message", "").lower()

    # find dish
    dish = find_dish(message, wine_pairs)

    if dish:
        wine = random.choice(wine_pairs[dish])

        reply = (
            f"{get_intro()}\n\n"
            f"You're enjoying **{dish.title()}**!\n\n"
            f"That dish pairs beautifully with:\n"
            f"👉 {wine} 🍷\n\n"
            f"In South Africa we share food, laughter, and wine around the table 🇿🇦"
        )

        log_interaction(message, reply, "matched")
        return jsonify({"reply": reply})

    # fallback (unknown dish)
    fallback_reply = (
        "Goofy says: I’m still learning that dish 🍷\n\n"
        "Try dishes like: pap, bobotie, stew or kota!"
    )

    log_interaction(message, fallback_reply, "unknown")

    return jsonify({"reply": fallback_reply})


# =====================
# RUN LOCAL
# =====================
if __name__ == "__main__":
    app.run(debug=True)

