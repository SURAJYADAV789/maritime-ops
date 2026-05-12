# MarineOPS — Maritime Operations & Compliance System

A web application to manage ship maintenance, safety drills, and compliance monitoring.

---

## Tech Stack

- **Backend** — Python, Django, Django REST Framework
- **Database** — PostgreSQL
- **Auth** — JWT (HttpOnly cookies)
- **Frontend** — HTML, CSS, JavaScript
- **DevOps** — Docker, Docker Compose, Nginx

---

## Features

- Ship fleet management
- Maintenance task tracking (Pending / In Progress / Completed / Overdue)
- Safety drill scheduling and attendance
- Compliance dashboard with charts
- Role-based access (Admin / Crew)
- REST API with JWT authentication

---

## Setup & Run

### Requirements

- Docker Desktop
- Git

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/SURAJYADAV789/maritime-ops.git
cd maritime-ops

# 2. Start the application
docker compose up --build

# 3. Create admin user
docker exec -it maritime_web python manage.py createsuperuser

# 4. Open browser
http://localhost:8000
```

---

## API Endpoints

| Method | Endpoint                  | Description       |
| ------ | ------------------------- | ----------------- |
| POST   | /api/v1/auth/register/    | Register user     |
| POST   | /api/v1/auth/login/       | Login             |
| POST   | /api/v1/auth/logout/      | Logout            |
| GET    | /api/v1/ships/            | List ships        |
| POST   | /api/v1/ships/            | Create ship       |
| GET    | /api/v1/maintenance/      | List tasks        |
| POST   | /api/v1/maintenance/      | Create task       |
| PATCH  | /api/v1/maintenance/{id}/ | Update task       |
| GET    | /api/v1/drills/           | List drills       |
| POST   | /api/v1/drills/           | Create drill      |
| GET    | /api/v1/compliance/       | Compliance report |

---

## Architecture

maritime-ops/
├── backend/
│ ├── apps/
│ │ ├── api/ # All REST API endpoints
│ │ ├── users/ # Auth, login, logout
│ │ ├── ships/ # Fleet management
│ │ ├── maintenance/ # Maintenance tasks
│ │ ├── drills/ # Safety drills
│ │ └── compliance/ # Dashboard & compliance logic
│ ├── maritime/ # Django settings & urls
│ └── templates/ # HTML pages
└── docker-compose.yml

---

## Login Credentials

| Role  | Username | Password  |
| ----- | -------- | --------- |
| Admin | admin    | admin123  |
| Crew  | crew1    | Test1234! |

---

## Compliance Calculation

Score = (Completed Tasks / Total Tasks) × 60%

- (Completed Drills / Total Drills) × 40%
  Risk Level:
  80-100% → Low Risk 🟢
  60-79% → Medium Risk 🟡
  0-59% → High Risk 🔴
