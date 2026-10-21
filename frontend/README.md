# Mini-SIEM | Security Monitoring Dashboard

A lightweight Security Information and Event Management (SIEM) project built with **Django REST Framework and React**. It records security events, detects potential brute-force login activity, generates severity-based alerts, and provides a dashboard for reviewing events and managing alerts.

## Features

- **Security Event Logging** — Record login successes, login failures, and suspicious activity.
- **Brute-Force Detection** — Identify repeated failed login attempts from the same source IP within a defined time window.
- **Severity-Based Alerts** — Generate alerts with severity levels such as Low, Medium, High, and Critical.
- **JWT Authentication** — Protect API endpoints using JSON Web Tokens.
- **Security Dashboard** — View security events, alerts, and monitoring statistics.
- **Searchable Event Logs** — Search events by username, source IP, event type, and message.
- **Alert Management** — Update alert statuses to Open, Investigating, or Resolved.
- **REST API** — Expose monitoring data through Django REST Framework endpoints.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend development |
| Django | Backend framework |
| Django REST Framework | REST API |
| Simple JWT | API authentication |
| React | Frontend dashboard |
| Vite | Frontend development server |
| Axios | HTTP requests |
| Recharts | Data visualization |
| Lucide React | Dashboard icons |
| SQLite | Local development database by default |

> PostgreSQL integration is a planned improvement unless it has been configured and tested in your environment.

## Project Structure

```text
Mini-SIEM/
├── backend/
│   ├── config/
│   │   ├── settings.py
│   │   └── urls.py
│   ├── monitoring/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── detection.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.css
│   └── package.json
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

Install the following:

- Python
- Node.js and npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/M-Abubakar24/Mini-SIEM.git
cd Mini-SIEM
```

### 2. Set up the Django backend

Open a terminal in the project directory:

```bash
cd backend
python -m venv venv
```

Activate the virtual environment on Windows:

```cmd
venv\Scripts\activate
```

Install the backend dependencies:

```bash
pip install -r requirements.txt
```

Apply database migrations:

```bash
python manage.py migrate
```

Create an administrator account:

```bash
python manage.py createsuperuser
```

Start the backend:

```bash
python manage.py runserver
```

The backend will be available at:

`http://127.0.0.1:8000/`

### 3. Set up the React frontend

Open a second terminal:

```bash
cd frontend
npm install
npm install axios recharts lucide-react
npm run dev
```

Open the frontend URL displayed in your terminal, usually:

`http://localhost:5173/`

### 4. Sign in

Use the Django superuser credentials created during backend setup to sign in to the dashboard.

The frontend obtains a JWT access token from the backend and uses it to request security events and alerts.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/token/` | Obtain JWT access and refresh tokens |
| POST | `/api/token/refresh/` | Refresh an access token |
| GET | `/api/events/` | Retrieve security events |
| POST | `/api/events/` | Create a security event |
| GET | `/api/alerts/` | Retrieve security alerts |
| PATCH | `/api/alerts/<id>/status/` | Update an alert's status |

Protected endpoints require a valid access token in the request header:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Brute-Force Detection

The current detection rule checks failed login events from the same source IP within a five-minute window.

- **Threshold:** Five failed login attempts
- **Detection window:** Five minutes
- **Alert severity:** High

When the threshold is reached, the system generates a potential brute-force alert. This is a demonstration rule, not a guarantee that an attack has occurred.

## Security Considerations

- Keep passwords, secret keys, access tokens, and `.env` files out of version control.
- Use environment variables and a strong, private Django secret key outside local development.
- Restrict CORS to trusted frontend origins.
- Enforce appropriate authorization for alert updates and event ingestion.
- Use HTTPS, secure deployment settings, and a production database before deployment.
- Use synthetic test events when demonstrating detection rules.

**This project is intended for educational and portfolio purposes. It is not a production-ready SIEM.**

## Roadmap

- [ ] Add event and alert analytics charts.
- [ ] Expand detection rules for suspicious activity.
- [ ] Add stronger role-based access controls.
- [ ] Improve automated API and detection-rule tests.
- [ ] Integrate PostgreSQL