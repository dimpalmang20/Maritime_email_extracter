from extraction.parser import process_email

# READ EMAIL FILE
with open("data/raw_emails/sample_email.txt", "r", encoding="utf-8") as file:
    email_text = file.read()

# PROCESS EMAIL
result = process_email(email_text)

# PRINT RESULT
print(result)