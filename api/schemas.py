from pydantic import BaseModel


class EmailPayload(BaseModel):

    subject: str

    sender: str

    body: str

class BulkEmailPayload(BaseModel):

    emails: list[EmailPayload]