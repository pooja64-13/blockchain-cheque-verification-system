import pdfplumber

with pdfplumber.open("cheque.pdf") as pdf:
    text = ""
    for page in pdf.pages:
        text += page.extract_text()

print("Extracted Data:\n")
print(text)