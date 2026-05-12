# MarineOPS — Business Flow Document

## 1. System Overview

MarineOPS is a maritime operations platform that helps marine organizations manage ship maintenance, safety drills, and regulatory compliance across their fleet.

---

## 2. User Roles

| Role  | Access                                                     |
| ----- | ---------------------------------------------------------- |
| Admin | Full access — manage ships, tasks, drills, view compliance |
| Crew  | Limited access — view assigned tasks, mark attendance      |

---

## 3. Business Flows

### 3.1 Ship Maintenance Flow

Admin creates task
↓
Assigns to crew member + sets due date
↓
Crew views assigned task
↓
Crew updates status → In Progress
↓
Crew adds notes/comments
↓
Crew marks → Completed
↓
System records completion time
If due date passes and not completed:
↓
Task marked → Overdue
↓
Appears as non-compliant in dashboard

### 3.2 Safety Drill Flow

Admin schedules drill
↓
Sets ship + date + drill type
↓
System auto-creates attendance records for all crew on ship
↓
Crew views upcoming drill
↓
Crew marks attendance
↓
Crew submits completion
↓
Admin marks drill as Completed
If scheduled date passes and not completed:
↓
Drill marked → Missed
↓
Appears as non-compliant in dashboard

### 3.3 Compliance Calculation Flow

System checks all ships daily
↓
For each ship:
→ Count total tasks vs completed tasks
→ Count total drills vs completed drills
↓
Maintenance Score = (Completed Tasks / Total Tasks) × 60%
Drill Score = (Completed Drills / Total Drills) × 40%
Overall Score = Maintenance Score + Drill Score
↓
Risk Level assigned:
80-100% → Low Risk 🟢
60-79% → Medium Risk 🟡
0-59% → High Risk 🔴
↓
Dashboard displays results

---

## 4. Pages & Features

| Page          | Role         | Features                                  |
| ------------- | ------------ | ----------------------------------------- |
| Dashboard     | Admin + Crew | Compliance score, charts, ship status     |
| Fleet         | Admin + Crew | List all ships, view ship details         |
| Maintenance   | Admin + Crew | Create tasks, update status, add comments |
| Safety Drills | Admin + Crew | Schedule drills, mark attendance          |

---

## 5. Business Rules

| Rule              | Description                                               |
| ----------------- | --------------------------------------------------------- |
| Overdue Task      | Task not completed by due date = non-compliant            |
| Missed Drill      | Drill not completed by scheduled date = non-compliant     |
| Compliance Weight | Maintenance 60% + Drills 40%                              |
| Auto Attendance   | System creates attendance records when drill is scheduled |
| Role Access       | Crew can only see their ship's data                       |

---

## 6. API Security

- JWT authentication with HttpOnly cookies
- Refresh token stored in HttpOnly cookie (7 days)
- Access token expires in 15 minutes
- Token blacklisting on logout
- Role-based permission on every endpoint

---

## 7. System Architecture

Browser
↓
Nginx (Port 80)
↓
Django (Port 8000)
↓
PostgreSQL (Port 5432)

---

## 8. Database Tables

| Table             | Description             |
| ----------------- | ----------------------- |
| users             | Admin and crew accounts |
| ships             | Registered vessels      |
| maintenance_tasks | Maintenance activities  |
| task_comments     | Notes on tasks          |
| safety_drills     | Scheduled drills        |
| drill_attendances | Crew attendance records |
