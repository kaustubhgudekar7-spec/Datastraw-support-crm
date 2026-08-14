from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from . import models, schemas, crud
from .database import engine, get_db, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Datastraw Support CRM")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")


# ---------- API ----------

@app.post("/api/tickets", response_model=schemas.TicketCreateResponse)
def create_ticket(payload: schemas.TicketCreate, db: Session = Depends(get_db)):
    ticket = crud.create_ticket(db, payload)
    return {"ticket_id": ticket.ticket_id, "created_at": ticket.created_at}


@app.get("/api/tickets", response_model=List[schemas.TicketListItem])
def list_tickets(status: Optional[str] = None, search: Optional[str] = None, db: Session = Depends(get_db)):
    tickets = crud.list_tickets(db, status=status, search=search)
    result = []
    for t in tickets:
        item = schemas.TicketListItem.model_validate(t)
        item.is_sla_breached = crud.is_breached(t)
        result.append(item)
    return result


@app.get("/api/tickets/{ticket_id}", response_model=schemas.TicketDetail)
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    detail = schemas.TicketDetail.model_validate(ticket)
    detail.is_sla_breached = crud.is_breached(ticket)
    return detail


@app.put("/api/tickets/{ticket_id}", response_model=schemas.TicketUpdateResponse)
def update_ticket(ticket_id: str, payload: schemas.TicketUpdate, db: Session = Depends(get_db)):
    ticket = crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket = crud.update_ticket(db, ticket, payload)
    return {"success": True, "updated_at": ticket.updated_at}


# ---------- Frontend (static) ----------
# Serve the plain HTML/JS frontend from the same service so a single
# deployment (e.g. Railway) exposes both the API and the UI.

app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")


@app.get("/")
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/create")
def serve_create():
    return FileResponse(os.path.join(FRONTEND_DIR, "create.html"))


@app.get("/ticket")
def serve_ticket():
    return FileResponse(os.path.join(FRONTEND_DIR, "ticket.html"))