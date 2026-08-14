import datetime
from typing import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session

from . import models, schemas

# Hours until SLA breach, keyed by priority. Simple hardcoded map instead of
# a config table -- deliberate tradeoff to keep the schema to 2 tables as
# instructed; real teams would make this configurable per-client.
SLA_HOURS = {"Urgent": 2, "High": 8, "Medium": 24, "Low": 72}


def _next_ticket_id(db: Session) -> str:
    last = db.query(models.Ticket).order_by(models.Ticket.id.desc()).first()
    next_num = (last.id + 1) if last else 1
    return f"TKT-{next_num:04d}"


def create_ticket(db: Session, data: schemas.TicketCreate) -> models.Ticket:
    ticket_id = _next_ticket_id(db)
    now = datetime.datetime.utcnow()
    sla_deadline = now + datetime.timedelta(hours=SLA_HOURS.get(data.priority, 24))

    ticket = models.Ticket(
        ticket_id=ticket_id,
        customer_name=data.customer_name,
        customer_email=data.customer_email,
        subject=data.subject,
        description=data.description,
        status="Open",
        priority=data.priority,
        sla_deadline=sla_deadline,
        created_at=now,
        updated_at=now,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def list_tickets(db: Session, status: Optional[str] = None, search: Optional[str] = None):
    query = db.query(models.Ticket)

    if status:
        query = query.filter(models.Ticket.status == status)

    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                models.Ticket.customer_name.ilike(like),
                models.Ticket.customer_email.ilike(like),
                models.Ticket.ticket_id.ilike(like),
                models.Ticket.subject.ilike(like),
                models.Ticket.description.ilike(like),
            )
        )

    return query.order_by(models.Ticket.created_at.desc()).all()


def get_ticket(db: Session, ticket_id: str) -> Optional[models.Ticket]:
    return db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()


def update_ticket(db: Session, ticket: models.Ticket, data: schemas.TicketUpdate) -> models.Ticket:
    if data.status:
        ticket.status = data.status
    if data.notes:
        note = models.Note(ticket_id=ticket.ticket_id, note_text=data.notes)
        db.add(note)
    ticket.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    return ticket


def is_breached(ticket: models.Ticket) -> bool:
    if ticket.status == "Closed" or not ticket.sla_deadline:
        return False
    return datetime.datetime.utcnow() > ticket.sla_deadline