import os
import json
import pandas as pd
from flask import Flask, request, render_template, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import openai

# ===============================
# CONFIG
# ===============================
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__, template_folder="templates")  # HTML in templates/

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
# DISH DETECTION
# ===============================
def detect_dish(message: str):
    for slang, real in local_dish_synonyms.items():
        message = message.replace(slang, real)
    prompt = f"""
You are a South African food expert.
Identify all South African dishes mentioned in the user's message.
Return ONLY a JSON array of dish names.

Message: "{message}"
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print("Dish detection error:", e)
        return []

# ===============================
# WINE RECOMMENDATION
# ===============================
def recommend_wine(dishes):
    dish_info = []
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
You are a professional South African sommelier.
The user is eating these dishes: {dish_info}
Recommend 3 wines per dish from the Western Cape (Stellenbosch, Paarl, Franschhoek, Constantia).
Return JSON like this:
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
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            temperature=0.4,
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print("Wine recommendation error:", e)
        return []

# ===============================
# CHAT ENDPOINT
# ===============================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    mode = data.get("mode", "fun")  # default to tourism fun

    reply = "Goofy is thinking... 🍷"

    try:
        if mode == "fun":
            # Tourism / Fun Mode
            prompt = f"""
You are Goofy, a fun, quirky South African wine guide.
Answer the user in a playful, engaging way.
Talk about South African dishes, flavors, history, and crafted wines.
Message: "{message}"
"""
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                temperature=0.6,
                messages=[{"role": "user", "content": prompt}]
            )
            reply = response.choices[0].message.content

        elif mode == "pairing":
            # Strict Sommelier Mode
            dishes = detect_dish(message)
            if dishes:
                wines = recommend_wine(dishes)
                if wines:
                    reply = ""
                    for rec in wines:
                        reply += f"\n🍷 {rec['dish'].title()}\n"
                        for wine in rec["wines"]:
                            reply += f"- {wine['name']} ({wine['grape']} – {wine['region']})\n"
                            reply += f"{wine['reason']}\n"
                else:
                    reply = "No wine pairings found for your dish."
            else:
                # user might ask wine-related questions in pairing mode
                prompt = f"""
You are Goofy, a strict South African sommelier.
Answer the user's wine or dish question precisely and professionally.
Message: "{message}"
"""
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    temperature=0.4,
                    messages=[{"role": "user", "content": prompt}]
                )
                reply = response.choices[0].message.content

    except Exception as e:
        print("Chat error:", e)
        reply = "Oops! Goofy spilled the wine 🍷 Try again."

    return jsonify({"reply": reply})

# ===============================
# HEALTH CHECK
# ===============================
@app.route("/health")
def health():
    return "OK"

# ===============================
# RUN
# ===============================
if __name__ == "__main__":

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)

