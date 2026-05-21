import hashlib
import pdfplumber

# ORIGINAL HASH (stored on blockchain)
original_hash = "9123d8c439d4be365e01fc53f2127efd9a386cc8210dae26cab6417c90d54110"

# Extract text from cheque
with pdfplumber.open("cheque.pdf") as pdf:
    text = ""

    for page in pdf.pages:
        extracted = page.extract_text()

        if extracted:
            text += extracted

# Generate new hash
new_hash = hashlib.sha256(text.encode()).hexdigest()

print("Generated Hash:")
print(new_hash)

# Compare hashes
if new_hash == original_hash:
    print("\n✅ CHEQUE IS VALID")
else:
    print("\n❌ CHEQUE HAS BEEN TAMPERED")