# bank_fraud_protector - demo

## Setup
1. Create a virtual environment and install dependencies:
   python -m venv venv
   venv\Scripts\activate   # windows powershell
   pip install -r server/requirements.txt

2. (Optional) Put your dataset in `data/spam_dataset.csv` (or the UCI `SMSSpamCollection` file) to get a better model. If no file present, a tiny sample dataset is used.

3. Run the server:
   cd server
   python app.py

   The server starts at http://127.0.0.1:5000

4. Open the frontend:
   Open `client/index.html` in your browser (double click). The page calls the Flask API at 127.0.0.1:5000

## Notes
- OTP values for transfer confirmation are printed in console only for demo.
- Use the `/unfreeze` endpoint only for demo; protect it with authentication in production.
- Replace `check_url_safety` in `app.py` with a real threat-intel API (Google Safe Browsing / VirusTotal) for production-grade detection.
