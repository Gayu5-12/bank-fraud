# model.py
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib
import pickle
import re

MODEL_FILE = "spam_model.pkl"
VECTORIZER_FILE = "vectorizer.pkl"

def train_model():
    # Try loading dataset from data/ folder
    data_path = "data/spam_dataset.csv"
    if not os.path.exists(data_path):
        # Download sample UCI dataset if not found
        print("[INFO] Dataset not found. Downloading sample...")
        url = "https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv"
        df = pd.read_csv(url, sep='\t', header=None, names=['label', 'message'])
    else:
        df = pd.read_csv(data_path)

    # Ensure correct columns
    df.columns = ['label', 'message']
    df['label'] = df['label'].map({'ham': 0, 'spam': 1})

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        df['message'], df['label'], test_size=0.2, random_state=42
    )

    # Vectorize text
    vectorizer = TfidfVectorizer(stop_words='english')
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Train Naive Bayes
    model = MultinomialNB()
    model.fit(X_train_vec, y_train)

    # Save model + vectorizer
    joblib.dump(model, MODEL_FILE)
    joblib.dump(vectorizer, VECTORIZER_FILE)

    print(f"[INFO] Model trained. Test accuracy: {model.score(X_test_vec, y_test):.2f}")

def predict_message(message):
    # Load model + vectorizer
    model = joblib.load(MODEL_FILE)
    vectorizer = joblib.load(VECTORIZER_FILE)

    # Transform input
    msg_vec = vectorizer.transform([message])
    proba = model.predict_proba(msg_vec)[0][1]  # probability of spam

    # Use higher threshold to avoid false positives
    if proba > 0.8:
        return "spam"
    else:
        return "ham"

if __name__ == "__main__":
    if not os.path.exists(MODEL_FILE):
        train_model()
        
import re

def predict_label(text):
    text_lower = text.lower()

    # 1. Spam keywords
    spam_keywords = [
        'win', 'free', 'offer', 'credit', 'loan', 'lottery', 'prize',
        'urgent', 'cashback', 'reward', 'claim now', 'guaranteed'
    ]

    # 2. OTP / Verification scam keywords
    otp_keywords = [
        'otp', 'one time password', 'verification code',
        'confirm account', 'secure code', 'security code'
    ]

    # 3. Suspicious link patterns
    link_pattern = r"(http[s]?://\S+|www\.\S+|\S+\.(com|net|org|in|io|ly))"

    # Flags
    is_spam = any(word in text_lower for word in spam_keywords)
    has_otp = any(word in text_lower for word in otp_keywords)
    has_suspicious_link = bool(re.search(link_pattern, text_lower))

    # Decision logic
    if is_spam or has_otp or has_suspicious_link:
        return "spam"
    else:
        return "ham"


def predict_proba(text):
    """
    Returns [ham_prob, spam_prob]
    Just for demonstration — in a real model, probabilities come from ML prediction.
    """
    label = predict_label(text)
    if label == "spam":
        return [0.1, 0.9]
    else:
        return [0.9, 0.1]

