import os
import json
import pandas as pd
from flask import Flask, request, render_template, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI
from flask_cors import CORS

# ===============================
# CONFIG
# ===============================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__, template_folder="templates")  # HTML in templates/
CORS(app)  # Allow AJAX calls from front-end

# ===============================
# LOAD DATA
# ===============================
foods = pd.read_csv("foods.csv")

with open("Pairing_rules.json") as f:
    rules = json.load(f)

# ===============================
# LOCAL DISH SLANG
# ===============================
local_dish_synonyms = {
    "vetkoek": "amagwinya",
    "braai meat": "boerewors",
    "kota": "kota",
    "umngqusho": "umngqusho",
    "pap": "pap",
    "chakalaka": "pap & chakalaka"
}

# ===============================
# DISH DETECTION WITH GPT
# ===============================
def detect_dish_with_gpt(message: str):
    # Replace local slang with standard dish names
    for slang, real in local_dish_synonyms.items():
        message = message.replace(slang, real)

    prompt = f"""
You are a South African food expert.
Identify all South African dishes mentioned in the user's message.
Return ONLY a JSON array of dish names.

Message: "{message}"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}]
        )

        dishes = json.loads(response.choices[0].message.content)
        print("Detected dishes:", dishes)
        return dishes

    except Exception as e:
        print("Error in dish detection:", e)
        return []

# ===============================
# WINE RECOMMENDATION
# ===============================
def recommend_wine_with_gpt(dishes: list):
    dish_info = []

    # Build structured info for GPT to pair
    for dish in dishes:
        row = foods[foods["dish_name"].str.lower() == dish.lower()]
        if not row.empty:
            row = row.iloc[0]
            dish_info.append({
                "dish": dish,
                "flavor": row["flavor_profile"],
                "fat": row["fat_level"],
                "spice": row["spice_level"],
                "method": row["cooking_method"],
                "protein": row["protein"]
            })

    if not dish_info:
        return []

    prompt = f"""
You are a professional South African wine sommelier.
The user is eating these dishes: {dish_info}
Recommend 3 wines per dish from the Western Cape (Stellenbosch, Paarl, Franschhoek, Constantia).
Return a JSON array like this:

[
 {{
  "dish": "dish name",
  "wines": [
   {{
    "name": "Wine name",
    "grape": "grape variety",
    "region": "region",
    "reason": "short pairing explanation"
   }}
  ]
 }}
]
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.4,
            messages=[{"role": "user", "content": prompt}]
        )
        wines = json.loads(response.choices[0].message.content)
        return wines
    except Exception as e:
        print("Wine recommendation error:", e)
        return []

# ===============================
# HEALTH CHECK / HTML UI
# ===============================
@app.route("/health")
def health():
    return "OK"

# ===============================
# WHATSAPP BOT
# ===============================
@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    incoming_msg = request.values.get("Body", "").lower()
    resp = MessagingResponse()
    msg = resp.message()

    dishes = detect_dish_with_gpt(incoming_msg)

    if dishes:
        recommendations = recommend_wine_with_gpt(dishes)
        if recommendations:
            reply = "🍷 Wine Recommendations\n\n"
            for rec in recommendations:
                reply += f"{rec['dish'].title()}\n"
                for wine in rec["wines"]:
                    reply += f"• {wine['name']} ({wine['grape']} – {wine['region']})\n{wine['reason']}\n"
                reply += "\n"
        else:
            reply = "Sorry, no wine recommendations found for your dish."
    else:
        reply = (
            "Hi! I'm your Wine Advisor 🍷\n\n"
            "Tell me what you're eating and I'll recommend a Western Cape wine.\n\n"
            "Examples:\n• boerewors\n• mogodu\n• bobotie\n• braai meat"
        )

    msg.body(reply)
    return str(resp)

# ===============================
# WEBHOOK TEST
# ===============================
@app.route("/webhook", methods=["GET","POST"])
def webhook():
    if request.method == "GET":
        return "Webhook working", 200
    data = request.json
    print("Incoming message:", data)
    return jsonify({"status": "ok"})

# ===============================
# CHAT UI AJAX
# ===============================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")

    dishes = detect_dish_with_gpt(message)
    reply = ""

    if dishes:
        recommendations = recommend_wine_with_gpt(dishes)
        if recommendations:
            for rec in recommendations:
                reply += f"\n🍷 {rec['dish'].title()}\n"
                for wine in rec["wines"]:
                    reply += f"- {wine['name']} ({wine['grape']} – {wine['region']})\n{wine['reason']}\n"
        else:
            reply = "No wine recommendations found for your dish."
    else:
        reply = "Tell me what South African dish you're eating."

    return jsonify({"reply": reply})

# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
