from flask import Flask, render_template, request
import pdfplumber
import hashlib
import os
import json
from datetime import datetime
from web3 import Web3

app = Flask(__name__)

# =========================
# BLOCKCHAIN CONNECTION
# =========================

ganache_url = "http://127.0.0.1:7545"

web3 = Web3(Web3.HTTPProvider(ganache_url))

sender_account = web3.eth.accounts[0]

# =========================
# UPLOAD FOLDER
# =========================

UPLOAD_FOLDER = "demo_cheques"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# HOME PAGE
# =========================

@app.route('/')
def home():
    return render_template("index.html")

# =========================
# REGISTER PAGE
# =========================

@app.route('/register-page')
def register_page():
    return render_template("register.html")

# =========================
# REGISTER CHEQUE
# =========================

@app.route('/register-cheque', methods=['POST'])
def register_cheque():

    uploaded_file = request.files['file']

    # File validation

    if uploaded_file.filename == '':
        return "❌ No file selected"

    if not uploaded_file.filename.endswith('.pdf'):
        return "❌ Only PDF files are allowed"

    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)

    uploaded_file.save(file_path)

    # Extract text

    try:

        with pdfplumber.open(file_path) as pdf:

            text = ""

            for page in pdf.pages:

                extracted = page.extract_text()

                if extracted:
                    text += extracted

    except:
        return "❌ Invalid or corrupted PDF file"

    # Empty PDF validation

    if text.strip() == "":
        return "❌ No readable text found in PDF"

    # Generate hash

    hash_value = hashlib.sha256(text.encode()).hexdigest()

    # Extract cheque number

    cheque_number = None

    lines = text.splitlines()

    for line in lines:

        if "Cheque No" in line:

            cheque_number = line.split(":")[1].strip()

            break

    if cheque_number is None:
        return "❌ Cheque Number Not Found"

    # Load hashes

    with open("hashes.json", "r") as file:

        hashes = json.load(file)

    # =========================
    # STORE HASH ON BLOCKCHAIN
    # =========================

    transaction = {
        'from': sender_account,
        'to': sender_account,
        'value': 0,
        'gas': 100000,
        'gasPrice': web3.to_wei('20', 'gwei'),
        'data': web3.to_hex(text=hash_value)
    }

    tx_hash = web3.eth.send_transaction(transaction)

    # Save blockchain transaction hash locally

    hashes[cheque_number] = {
        "tx_hash": tx_hash.hex()
    }

    # Save updated hashes

    with open("hashes.json", "w") as file:

        json.dump(hashes, file, indent=4)

    return f"""
<h2>✅ Cheque Registered Successfully!</h2>

<h3>Cheque No: {cheque_number}</h3>

<h3>Blockchain Transaction Stored Successfully</h3>

<p><b>Transaction Hash:</b></p>

<p style="word-wrap: break-word; color: blue;">
{tx_hash.hex()}
</p>
"""

# =========================
# VERIFY PAGE
# =========================

@app.route('/verify-page')
def verify_page():
    return render_template("verify.html")

# =========================
# VERIFY CHEQUE
# =========================

@app.route('/verify', methods=['POST'])
def verify():

    uploaded_file = request.files['file']

    # File validation

    if uploaded_file.filename == '':
        return "❌ No file selected"

    if not uploaded_file.filename.endswith('.pdf'):
        return "❌ Only PDF files are allowed"

    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)

    uploaded_file.save(file_path)

    # Extract text

    try:

        with pdfplumber.open(file_path) as pdf:

            text = ""

            for page in pdf.pages:

                extracted = page.extract_text()

                if extracted:
                    text += extracted

    except:
        return "❌ Invalid or corrupted PDF file"

    # Empty PDF validation

    if text.strip() == "":
        return "❌ No readable text found in PDF"

    # Generate new hash

    new_hash = hashlib.sha256(text.encode()).hexdigest()

    # Extract cheque number

    cheque_number = None

    lines = text.splitlines()

    for line in lines:

        if "Cheque No" in line:

            cheque_number = line.split(":")[1].strip()

            break

    if cheque_number is None:
        return "❌ Cheque Number Not Found"

    # Load hashes

    with open("hashes.json", "r") as file:

        hashes = json.load(file)

    # Check if cheque exists

    if cheque_number not in hashes:
        return "❌ Cheque Not Registered"

    # =========================
    # FETCH HASH FROM BLOCKCHAIN
    # =========================

    tx_hash = hashes[cheque_number]["tx_hash"]

    transaction = web3.eth.get_transaction(tx_hash)

    blockchain_hash = web3.to_text(transaction['input']).replace('\x00', '')

    # =========================
    # COMPARE HASHES
    # =========================

    if new_hash == blockchain_hash:

        result = "✅ CHEQUE IS VALID"

    else:

        result = "❌ CHEQUE HAS BEEN TAMPERED"

    # =========================
    # LOG ENTRY
    # =========================

    log_entry = {
    "file": uploaded_file.filename,
    "cheque_number": cheque_number,
    "status": result,
    "hash": new_hash,
    "tx_hash": tx_hash,
    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

    # Load logs

    with open("logs.json", "r") as file:

        logs = json.load(file)

    # Add log

    logs.append(log_entry)

    # Save logs

    with open("logs.json", "w") as file:

        json.dump(logs, file, indent=4)

    return render_template(
    "result.html",
    result=result,
    hash_value=new_hash,
    cheque_number=cheque_number,
    tx_hash=tx_hash
)

# =========================
# DASHBOARD
# =========================

@app.route('/dashboard')
def dashboard():

    with open("logs.json", "r") as file:

        logs = json.load(file)

    total = len(logs)

    valid_count = 0

    tampered_count = 0

    for log in logs:

        if "VALID" in log["status"]:

            valid_count += 1

        else:

            tampered_count += 1

    return render_template(
        "dashboard.html",
        total=total,
        valid=valid_count,
        tampered=tampered_count
    )

# =========================
# ARCHITECTURE PAGE
# =========================

@app.route('/architecture')
def architecture():
    return render_template("architecture.html")

# =========================
# LOGS PAGE
# =========================

@app.route('/logs')
def logs():

    with open("logs.json", "r") as file:

        logs_data = json.load(file)

    return render_template("logs.html", logs=logs_data)

# =========================
# RUN APP
# =========================

if __name__ == '__main__':
    app.run(debug=True)