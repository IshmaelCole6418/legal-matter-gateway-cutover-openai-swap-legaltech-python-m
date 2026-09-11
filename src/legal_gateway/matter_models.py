from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl


class MatterUrgency(StrEnum):
    ROUTINE = "routine"
    PRIORITY = "priority"
    IMMEDIATE = "immediate"


class MatterIntake(BaseModel):
    matter_id: str = Field(min_length=1)
    client_name: str = Field(min_length=1)
    summary: str = Field(min_length=10)
    jurisdiction: str = Field(min_length=2)
    response_deadline: date
    signed_document_url: HttpUrl | None = None


class IntakeClassification(BaseModel):
    matter_type: str
    urgency: MatterUrgency
    intake_note: str


class MatterWorkflow(BaseModel):
    matter_id: str
    matter_type: str
    urgency: MatterUrgency
    delivery_status: str
    follow_up_action: str
    follow_up_on: date
    intake_note: str
