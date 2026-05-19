from extraction.parser import process_email
from database import (
    create_database,
    search_by_cargo,
    search_by_port,
    search_by_vessel,
    get_all_records
)
create_database()
# READ EMAIL FILE
with open("data/raw_emails/sample_email.txt", "r", encoding="utf-8") as file:
    email_text = file.read()

# PROCESS EMAIL
result = process_email(email_text)

# PRINT RESULT
print(result)

print("\nALL RECORDS:")
print(get_all_records())

print("\nSEARCH BY CARGO:")
print(search_by_cargo("Corn"))

print("\nSEARCH BY PORT:")
print(search_by_port("Doha"))

print("\nSEARCH BY VESSEL:")
print(search_by_vessel("Panamax"))