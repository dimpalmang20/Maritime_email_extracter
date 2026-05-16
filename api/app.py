# API endpoints

from fastapi import FastAPI
from extraction.parser import process_email

app = FastAPI()


@app.post("/extract")
def extract_email(data: dict):

    text = data["email"]

    result = process_email(text)

    return result