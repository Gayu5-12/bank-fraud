# server/transaction_blocker.py
import time
import random
from threading import Lock

store_lock = Lock()
account_locked = {}          # user_id -> bool
approved_beneficiaries = {}  # user_id -> set()
pending_otps = {}            # session_id -> {otp, expires, transfer}

OTP_VALID_SECONDS = 300

def lock_account(user_id):
    with store_lock:
        account_locked[user_id] = True

def unlock_account(user_id):
    with store_lock:
        account_locked[user_id] = False

def is_account_locked(user_id):
    return account_locked.get(user_id, False)

def get_approved_beneficiaries(user_id):
    return approved_beneficiaries.get(user_id, set())

def add_approved_beneficiary(user_id, beneficiary):
    approved_beneficiaries.setdefault(user_id, set()).add(beneficiary)

def generate_session_id():
    return str(time.time_ns())

def generate_otp():
    return random.randint(100000, 999999)

def require_otp_for_transfer(user_id, to_account, amount, threshold_amount=10000):
    """
    If beneficiary not approved or amount > threshold => require otp
    Returns: {'need_otp': bool, 'session_id':..., 'otp':... (for demo printed by server)}
    """
    if is_account_locked(user_id):
        return {"blocked": True, "reason": "account_locked"}

    ben_set = get_approved_beneficiaries(user_id)
    if to_account not in ben_set or amount > threshold_amount:
        session = generate_session_id()
        otp = generate_otp()
        pending_otps[session] = {
            "otp": otp,
            "expires": time.time() + OTP_VALID_SECONDS,
            "transfer": {"user_id": user_id, "to_account": to_account, "amount": amount}
        }
        # NOTE: In production send OTP through secure channel (SMS/Email/Push)
        return {"need_otp": True, "session_id": session, "otp": otp}
    # allowed
    return {"need_otp": False}

def confirm_otp(session_id, otp_input, approve_beneficiary=False):
    rec = pending_otps.get(session_id)
    if not rec:
        return {"status": "error", "reason": "no_such_session"}
    if time.time() > rec["expires"]:
        del pending_otps[session_id]
        return {"status": "error", "reason": "otp_expired"}
    if int(rec["otp"]) != int(otp_input):
        return {"status": "error", "reason": "invalid_otp"}
    transfer = rec["transfer"]
    user_id = transfer["user_id"]
    to_account = transfer["to_account"]
    if approve_beneficiary:
        add_approved_beneficiary(user_id, to_account)
    # simulate execution
    del pending_otps[session_id]
    return {"status": "executed", "transfer": transfer}
