import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator

VALID_STATUSES = {"Open", "In Progress", "Closed"}
VALID_PRIORITIES = {"Low", "Medium", "High", "Urgent"}

class AgentSignup(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def check_password_length(cls, v):
        if len(v) < 6:
            raise ValueError("password must be at least 6 characters")
        return v


class AgentLogin(BaseModel):
    email: EmailStr
    password: str


class AgentOut(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    agent: AgentOut


class TicketCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    subject: str
    description: str
    priority: Optional[str] = "Medium"

    @field_validator("priority")
    @classmethod
    def check_priority(cls, v):
        if v not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {VALID_PRIORITIES}")
        return v


class TicketCreateResponse(BaseModel):
    ticket_id: str
    created_at: datetime.datetime


class TicketListItem(BaseModel):
    ticket_id: str
    customer_name: str
    subject: str
    status: str
    priority: str
    created_at: datetime.datetime
    is_sla_breached: bool = False

    class Config:
        from_attributes = True


class NoteOut(BaseModel):
    note_text: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class TicketDetail(BaseModel):
    ticket_id: str
    customer_name: str
    customer_email: str
    subject: str
    description: str
    status: str
    priority: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    sla_deadline: Optional[datetime.datetime] = None
    is_sla_breached: bool = False
    notes: List[NoteOut] = []

    class Config:
        from_attributes = True


class TicketUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None  # new note text to append

    @field_validator("status")
    @classmethod
    def check_status(cls, v):
        if v is not None and v not in VALID_STATUSES:
            raise ValueError(f"status must be one of {VALID_STATUSES}")
        return v


class TicketUpdateResponse(BaseModel):
    success: bool
    updated_at: datetime.datetime
