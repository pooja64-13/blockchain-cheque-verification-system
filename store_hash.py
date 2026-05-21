from web3 import Web3
import hashlib
import pdfplumber

# Connect to Ganache
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Check connection
if not web3.is_connected():
    print("❌ Blockchain connection failed")
    exit()

print("✅ Connected to Blockchain")

# Extract text from cheque PDF
with pdfplumber.open("cheque.pdf") as pdf:
    text = ""

    for page in pdf.pages:
        extracted = page.extract_text()

        if extracted:
            text += extracted

# Generate SHA-256 hash
hash_value = hashlib.sha256(text.encode()).hexdigest()

print("\nGenerated Hash:")
print(hash_value)

# Sender account from Ganache
sender = web3.eth.accounts[0]

# Create transaction
transaction = {
    'from': sender,
    'to': sender,
    'value': 0,
    'gas': 100000,
    'gasPrice': web3.to_wei('20', 'gwei'),
    'nonce': web3.eth.get_transaction_count(sender),
    'data': hash_value.encode().hex()
}

# Send transaction
tx_hash = web3.eth.send_transaction(transaction)

print("\n✅ Hash stored on Blockchain!")
print("Transaction Hash:")
print(tx_hash.hex())