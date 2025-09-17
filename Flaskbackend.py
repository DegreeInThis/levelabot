from flask import Flask, render_template, request, jsonify, redirect
import os

app = Flask(__name__, template_folder='Templates', static_folder='Static')

# --- Session Tracking ---
user_sessions = {}

# --- Chatbot Logic ---
def get_response(user_id, user_input):
    user_input = user_input.lower().strip()

    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "stage": "start",
            "name": "",
            "email": "",
            "project": "",
            "features": ""
        }

    session = user_sessions[user_id]

    if session["stage"] == "start":
        session["stage"] = "ask_project_type"
        return "Hi! I'm LevelaBot. Are you looking for an instant website or a bespoke one?"

    if session["stage"] == "ask_project_type":
        if "instant" in user_input or "template" in user_input:
            session["project"] = "instant"
            session["stage"] = "collect_name"
            return "Great! Instant websites start at £249 and are ready in 24 hours. What’s your name?"
        elif "bespoke" in user_input or "custom" in user_input:
            session["project"] = "bespoke"
            session["stage"] = "collect_name"
            return "Perfect! Bespoke sites are tailored to your needs. What’s your name?"
        else:
            return "Just checking — are you after an instant website or a bespoke one?"

    if session["stage"] == "collect_name":
        session["name"] = user_input.title()
        session["stage"] = "collect_email"
        return f"Thanks, {session['name']}! What’s the best email to reach you on?"

    if session["stage"] == "collect_email":
        if "@" in user_input and "." in user_input:
            session["email"] = user_input
            session["stage"] = "collect_features"
            return "Got it! What features do you need — contact form, gallery, booking system, or something else?"
        else:
            return "Hmm, that doesn’t look like a valid email. Could you double-check it?"

    if session["stage"] == "collect_features":
        session["features"] = user_input
        session["stage"] = "quote_summary"
        if session["project"] == "instant":
            return f"Here’s your summary:\n• Type: Instant Website\n• Price: £249\n• Setup: 24 hours\n• Features: {session['features']}\n\nWould you like to preview templates or proceed to payment?"
        else:
            return f"Here’s your bespoke quote summary:\n• Type: Bespoke Website\n• Estimated Price: £499–£999\n• Setup: 1–3 days\n• Features: {session['features']}\n\nWould you like a formal quote emailed to you or speak to someone?"

    if session["stage"] == "quote_summary":
        if "preview" in user_input:
            return "You can browse templates at [levelasolutions.co.uk/GetYourWebsiteNow](https://www.levelasolutions.co.uk/GetYourWebsiteNow). Let me know which one you like!"
        elif "pay" in user_input or "proceed" in user_input:
            session["stage"] = "ready_for_payment"
            return "Click below to complete your payment securely:\n\n[Proceed to Payment](/create-checkout-session)"
        elif "quote" in user_input or "email" in user_input:
            return f"Perfect — I’ll send a quote to {session['email']} shortly. Anything else you'd like to ask?"
        elif "speak" in user_input or "human" in user_input:
            return "No problem — I’ll arrange a callback or email follow-up. Someone from Levela will be in touch soon."
        else:
            return "Would you like to preview templates, proceed to payment, or request a formal quote?"

    if "price" in user_input or "cost" in user_input:
        return "Instant websites are £249. Bespoke sites range from £499 to £999 depending on features."

    if "setup" in user_input or "how long" in user_input:
        return "Instant sites are ready in 24 hours. Bespoke sites take 1–3 days depending on complexity."

    if "stripe" in user_input or "payment" in user_input:
        return "We use Stripe for secure payments. You’ll be guided through it during checkout."

    if "bye" in user_input or "thanks" in user_input:
        return "You're very welcome! Let me know if you need anything else."

    if "human" in user_input or "support" in user_input or "help" in user_input:
        return "I’m here to help! If you'd prefer to speak to someone directly, I can arrange a callback or email follow-up."

    return "Hmm, I didn’t quite catch that. Want to preview templates, get a quote, or speak to someone?"

# --- Flask Routes ---
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def chatbot_response():
    user_input = request.form["msg"]
    user_id = request.remote_addr
    reply = get_response(user_id, user_input)
    return jsonify({"reply": reply})

# --- Optional Stripe Checkout ---
stripe_key = os.getenv("STRIPE_SECRET_KEY")
if stripe_key:
    import stripe
    stripe.api_key = stripe_key

    @app.route("/create-checkout-session", methods=["GET"])
    def create_checkout_session():
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "gbp",
                    "product_data": {
                        "name": "Instant Website",
                    },
                    "unit_amount": 24900,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="https://www.levelasolutions.co.uk/success",
            cancel_url="https://www.levelasolutions.co.uk/cancel",
        )
        return redirect(session.url, code=303)

if __name__ == "__main__":
    app.run(debug=True)