import re
from urllib.parse import urlparse
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

from model import predict_label, predict_proba
import transaction_blocker as tb

app = Flask(__name__, static_folder="../client", static_url_path="")
CORS(app)

URL_REGEX = re.compile(r"(https?://[^\s]+)", re.IGNORECASE)

# Demo local blocklist and bank domains (customize)
LOCAL_BLOCKED_DOMAINS = {"malicious.example.com", "fakebank-login.example.com"}
VERIFIED_BANK_DOMAINS = {"www.yourbank.com", "online.yourbank.com"}

# Fixed OTP for demo
VALID_OTP = "123456"

# ------------------------------
# Utility Functions
# ------------------------------
def extract_urls(text):
    return URL_REGEX.findall(text or "")

def domain_from_url(url):
    try:
        p = urlparse(url)
        return p.netloc.lower()
    except:
        return None

def check_url_safety(url):
    domain = domain_from_url(url)
    if not domain:
        return {"safe": False, "reason": "invalid_url"}
    if domain in LOCAL_BLOCKED_DOMAINS:
        return {"safe": False, "reason": "local_blocklist"}
    if any(k in domain for k in ["bank", "pay", "secure", "online"]):
        if domain not in VERIFIED_BANK_DOMAINS:
            return {"safe": False, "reason": "unverified_banking_domain"}
    return {"safe": True, "reason": "ok"}

# ------------------------------
# Routes
# ------------------------------
@app.route("/")
def home():
    index_path = os.path.join(app.static_folder, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(app.static_folder, "index.html")
    return jsonify({"message": "Bank Fraud Protector API is running!"})

@app.route("/receive_sms", methods=["POST"])
def receive_sms():
    payload = request.get_json() or {}
    user_id = payload.get("user_id", "user1")
    text = payload.get("text", "")
    sender = payload.get("from", "unknown")

    label = predict_label(text)
    prob = None
    try:
        probs = predict_proba(text)
        if probs is not None:
            prob = max(probs).item() if hasattr(probs[0], "item") else max(probs)
    except Exception:
        prob = None

    urls = extract_urls(text)
    url_checks = [check_url_safety(u) for u in urls]

    is_spam = (label == "spam") or any(not c["safe"] for c in url_checks)

    return jsonify({
        "user_id": user_id,
        "from": sender,
        "text": text,
        "predicted_label": label,
        "confidence": prob,
        "urls": url_checks,
        "action": "quarantine" if is_spam else "allow",
        "account_locked": False   # never lock in demo
    })

@app.route("/open_link", methods=["POST"])
def open_link():
    payload = request.get_json() or {}
    url = payload.get("url", "")
    check = check_url_safety(url)

    if not check["safe"]:
        return jsonify({"allowed": False, "reason": check["reason"], "account_locked": False})

    return jsonify({"allowed": True, "reason": "ok", "account_locked": False})

@app.route("/initiate_transfer", methods=["POST"])
def initiate_transfer():
    payload = request.get_json() or {}
    to_account = payload.get("to_account")
    amount = float(payload.get("amount", 0))

    if not to_account or amount <= 0:
        return jsonify({"status": "error", "reason": "invalid_parameters"}), 400

    # Always ask for OTP in demo
    return jsonify({
        "status": "otp_required",
        "session_id": "demo-session-123",
        "note": "Use OTP: 123456"
    }), 200

@app.route("/confirm_transfer", methods=["POST"])
def confirm_transfer():
    payload = request.get_json() or {}
    otp = payload.get("otp")
    if otp == VALID_OTP:
        return jsonify({"status": "executed", "message": "✅ Transfer successful!"}), 200
    else:
        return jsonify({"status": "error", "reason": "❌ Invalid OTP"}), 400

@app.route("/status/<user_id>", methods=["GET"])
def status(user_id):
    return jsonify({
        "user_id": user_id,
        "account_locked": False,
        "approved_beneficiaries": []
    })

@app.route("/unfreeze", methods=["POST"])
def unfreeze():
    return jsonify({"status": "unfrozen", "note": "Account blocking disabled in demo"})

if __name__ == "__main__":
    print("Starting bank_fraud_protector demo on http://127.0.0.1:5000")
    app.run(debug=True)
