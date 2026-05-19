# API endpoints
from api.schemas import EmailPayload, BulkEmailPayload
from fastapi import FastAPI
from extraction.parser import process_email



app = FastAPI()

from database.db import engine
from database.models import Base

Base.metadata.create_all(bind=engine)

@app.get("/records")

def get_records():

    db = SessionLocal()

    records = db.query(MaritimeRecord).all()

    results = []

    for r in records:

        results.append({

            "id": r.id,

            "cargo": r.cargo,

            "cargo_type": r.cargo_type,

            "vessel_name": r.vessel_name,

            "vessel_type": r.vessel_type,

            "imo": r.imo,

            "load_port": r.load_port,

            "discharge_port": r.discharge_port,

            "open_port": r.open_port,

            "quantity": r.quantity,

            "grain_capacity": r.grain_capacity,

            "dwt": r.dwt,

            "laycan": r.laycan,

            "confidence_score": r.confidence_score,

            "extraction_status": r.extraction_status

        })

    db.close()

    return {

        "records": results

    }

@app.post("/extract")
def extract_email(data: dict):

    text = data["email"]

    result = process_email(text)

    return result



@app.get("/search/{field}/{value}")

def search_records(field: str, value: str):

    from database.db import SessionLocal
    from database.models import MaritimeRecord

    db = SessionLocal()

    allowed_fields = [

    "vessel_name",
    "cargo",
    "load_port",
    "open_port",
    "vessel_type",
    "laycan",
    "template_type"

]

    if field not in allowed_fields:

        return {

            "error":"Invalid field"

        }

    column = getattr(MaritimeRecord, field)

    try:

       records = db.query(MaritimeRecord).filter(

        column.ilike(f"%{value}%")

    ).all()

    except Exception as e:

      return {

        "error": str(e)

    }

    results = []

    for r in records:

        results.append({

            "vessel_name": r.vessel_name,
            "cargo": r.cargo,
            "open_port": r.open_port,
            "vessel_type": r.vessel_type,
            "dwt": r.dwt,
            "laycan": r.laycan

        })

    return {

        "results": results

    }




@app.post("/email-parser")
def email_parser(payload: EmailPayload):

    email_text = payload.body

    result = process_email(email_text)

    return {

        "subject": payload.subject,

        "sender": payload.sender,

        "extraction_result": result
    }


@app.post("/bulk-email-parser")
def bulk_email_parser(payload: BulkEmailPayload):

    results = []

    for email in payload.emails:

        extracted = process_email(email.body)

        results.append({

            "subject": email.subject,

            "sender": email.sender,

            "result": extracted
        })

    return {

        "processed_emails": len(results),

        "results": results
    }