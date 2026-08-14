# Datastraw Support CRM

A lightweight customer support ticketing system built for the Datastraw assessment.
Create tickets, search/filter them, and track status + notes through resolution.

## Stack

- **Backend:** Python + FastAPI
- **Database:** SQLite (via SQLAlchemy ORM)
- **Frontend:** Plain HTML + Tailwind CSS (CDN) + vanilla JS — no build step
- **Deploy target:** Railway.app

## Features

1. Create tickets (customer name/email, subject, description, auto ticket ID + timestamp)
2. List all tickets (ID, name, subject, status, priority, created date)
3. Live search across name, email, ticket ID, and description
4. Filter by status (Open / In Progress / Closed)
5. Ticket detail view with status updates and notes
6. **Stand out feature — Priority + SLA tracking:** every ticket gets a priority
   (Low/Medium/High/Urgent) that maps to an SLA deadline (Urgent = 2h, High = 8h,
   Medium = 24h, Low = 72h). Tickets past their deadline are flagged "SLA breached"
   in red on the list and detail views. This is the kind of triage signal a team
   handling hundreds of tickets/day actually needs — a flat FIFO list doesn't scale.
   **Tradeoff:** SLA hours are hardcoded per priority rather than configurable per
   client/team, to keep the schema at 2 tables as specified. A production version
   would move this into a settings table.

## Project structure

```
datastraw-crm/
├── backend/
│   ├── main.py        # FastAPI app + routes + static file serving
│   ├── database.py     # SQLAlchemy engine/session setup
│   ├── models.py        # Ticket, Note ORM models
│   ├── schemas.py     # Pydantic request/response models
│   └── crud.py            # DB query logic (create/list/get/update, SLA calc)
├── frontend/
│   ├── index.html      # Ticket list, search, filter
│   ├── create.html    # New ticket form
│   ├── ticket.html    # Ticket detail + update
│   └── static/app.js  # Shared JS: API calls, formatting helpers
├── requirements.txt
├── Procfile             # Railway/Heroku-style start command
├── .env.example
└── .gitignore
```

## Local setup

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd datastraw-crm

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (optional) copy env example
cp .env.example .env

# 5. Run the app
uvicorn backend.main:app --reload

# App will be live at http://127.0.0.1:8000
```

SQLite tables are created automatically on first run — no migration step needed.

## API endpoints

| Method | Endpoint                | Description                                  |
|--------|--------------------------|-----------------------------------------------|
| POST   | `/api/tickets`           | Create a ticket                               |
| GET    | `/api/tickets`           | List tickets (`?status=`, `?search=`)         |
| GET    | `/api/tickets/{ticket_id}` | Get full ticket detail incl. notes         |
| PUT    | `/api/tickets/{ticket_id}` | Update status and/or add a note            |

Interactive API docs are available at `/docs` (Swagger UI) once the app is running.

## Deployment (Railway)

1. Push this repo to GitHub.
2. In Railway, create a new project → **Deploy from GitHub repo**.
3. Railway auto-detects Python and installs `requirements.txt`.
4. Set the start command (if not picked up automatically from the `Procfile`):
   `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. SQLite works out of the box on a single Railway instance (file-based, no
   separate DB service needed). For multi-instance scaling, swap `DATABASE_URL`
   to a Railway Postgres addon — the SQLAlchemy models don't need to change.
6. Deploy — Railway gives you a public URL.

## Notes on database design

Two tables only, as specified:

- **tickets**: id, ticket_id (unique, `TKT-0001` style), customer_name,
  customer_email, subject, description, status, priority, sla_deadline,
  created_at, updated_at
- **notes**: id, ticket_id (FK), note_text, created_at

`priority`/`sla_deadline` are the only additions beyond the base spec, in
support of the SLA stand-out feature described above.
