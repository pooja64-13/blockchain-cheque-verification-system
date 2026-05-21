import hashlib
import pdfplumber

# Extract text from PDF
with pdfplumber.open("cheque.pdf") as pdf:
    text = ""

    for page in pdf.pages:
        extracted = page.extract_text()
        
        if extracted:
            text += extracted

# Generate SHA-256 hash
hash_value = hashlib.sha256(text.encode()).hexdigest()

print("Extracted Text:\n")
print(text)

print("\nSHA-256 Hash:\n")
print(hash_value)