from pydantic import BaseModel

class TriggerResponse(BaseModel):
    triggered: bool
    job: str
    message: str

class StatusResponse(BaseModel):
    service: str
    watermark_last_created_at: str | None
    current_utc: str