from flask import Flask, request, render_template, jsonify
import random

app = Flask(__name__, template_folder="templates")

# Simple wine suggestions
wine_pairs = {
    "bobotjie": [
        "Pinotage from Stellenbosch 🍷",
        "Shiraz from Paarl 🍷",
        "Cape Blend from Franschhoek 🍷"
    ],
    "pap": [
        "Chenin Blanc from Stellenbosch 🍷",
        "Chardonnay from Constantia 🍷"
    ],
    "kota": [
        "Bold Pinotage 🍷",
        "Spicy Shiraz 🍷"
    ],
    "stew": [
        "Cabernet Sauvignon 🍷",
        "Merlot 🍷"
    ]
}

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

    data = request.json
    message = data.get("message","").lower()

    # Goofy personality responses
    goofy_intro = [
        "Goofy here! 🍷 Let’s talk South African food!",
        "Ahh my friend! Goofy knows these flavors well 🍷",
        "Now that is a proper South African meal! 🇿🇦",
    ]

    # detect dish
    for dish in wine_pairs:

        if dish in message:

            wine = random.choice(wine_pairs[dish])

            reply = (
                f"{random.choice(goofy_intro)}\n\n"
                f"You're enjoying **{dish.title()}**!\n\n"
                f"That dish loves a glass of:\n"
                f"👉 {wine}\n\n"
                f"In South Africa we share food, laughter, and wine around the table 🍷"
            )

            return jsonify({"reply": reply})

    # fallback
    return jsonify({
        "reply":
        "Goofy says: Tell me what South African food you're eating!\n\nTry: pap, bobotjie, stew or kota 🍷"
    })


# =====================
# RUN LOCAL
# =====================

if __name__ == "__main__":
    app.run(debug=True)
