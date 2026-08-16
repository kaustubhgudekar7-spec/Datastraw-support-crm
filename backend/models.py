import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, unique=True, index=True, nullable=False)  # e.g. TKT-0001
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, default="Open", nullable=False)  # Open / In Progress / Closed

    # --- Stand Out feature: priority + SLA tracking ---
    # Real support teams triage by urgency; a flat ticket list doesn't scale past a
    # handful of tickets/day. Priority + an SLA deadline lets the UI surface
    # "about to breach" tickets first instead of oldest-first or FIFO only.
    priority = Column(String, default="Medium", nullable=False)  # Low/Medium/High/Urgent
    sla_deadline = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    notes = relationship("Note", back_populates="ticket", cascade="all, delete-orphan")

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, ForeignKey("tickets.ticket_id"), nullable=False)
    note_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    ticket = relationship("Ticket", back_populates="notes")
