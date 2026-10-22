# Mini-SIEM | Security Monitoring Dashboard

A lightweight, full-stack Security Information and Event Management (SIEM) project built with **Django REST Framework and React**. It records security events, detects potential brute-force login activity, generates severity-based alerts, and provides a dashboard for monitoring events and managing investigations.

## Features

- **Security Event Logging:** Record login successes, login failures, and suspicious activity.
- **Brute-Force Detection:** Detect repeated failed login attempts from the same source IP within a five-minute window.
- **Severity-Based Alerts:** Generate alerts with Low, Medium, High, and Critical severity levels.
- **JWT Authentication:** Protect API endpoints using JSON Web Tokens.
- **Security Dashboard:** Visualize security events, alerts, and monitoring statistics.
- **Searchable Event Logs:** Search security events using supported event fields.
- **Alert Management:** Update alert statuses to Open, Investigating, or Resolved.
- **Audit Logging:** Record security event creation and alert status changes.
- **Role-Based Access Control:** Restrict sensitive operations and audit-log access according to user permissions.
- **API Rate Limiting:** Apply request throttling to help limit excessive API requests and repeated login attempts.
- **Security Headers:** Configure browser security headers, including content-type protection and clickjacking protection.
- **Automated Tests:** Test detection logic, API validation, authentication, and permissions.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend development |
| Django | Backend framework |
| Django REST Framework | REST API |
| SimpleJWT | JWT authentication |
| React | Frontend dashboard |
| Vite | Frontend development server |
| Axios | HTTP requests |
| Recharts | Data visualization |
| Lucide React | Dashboard icons |
| SQLite | Local development database |

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
│   │   ├── permissions.py
│   │   ├── pagination.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
├── docs/
│   └── screenshots/
├── .gitignore
└── README.md
```

*Adjust the tree if your actual filenames or folders differ.*

## Getting Started

### Prerequisites

- Python
- Node.js and npm
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/M-Abubakar24/Mini-SIEM.git
cd Mini-SIEM
```

### 2. Set Up the Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The backend runs at `http://127.0.0.1:8000/`.

### 3. Set Up the Frontend

Open a second terminal from the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually `http://localhost:5173/`.

The frontend dependencies should be declared in `package.json`; you generally do not need to reinstall Axios, Recharts, and Lucide React separately if they are already listed there.

### 4. Authentication

Create an administrator account using `python manage.py createsuperuser`. Sign in through the dashboard using the credentials supported by your frontend.

The authentication endpoint returns JWT tokens. Protected API requests use the access token in this header:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Never commit real access tokens or passwords to GitHub.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/token/` | Obtain JWT access and refresh tokens |
| POST | `/api/token/refresh/` | Refresh an access token |
| GET, POST | `/api/events/` | List or create security events |
| GET | `/api/alerts/` | Retrieve security alerts |
| PATCH | `/api/alerts/<id>/status/` | Update an alert's status |
| GET | `/api/audit-logs/` | Retrieve audit logs with admin permissions |

The audit-log endpoint supports pagination, search, and ordering when configured in the backend. Example:

```text
/api/audit-logs/?page_size=20
/api/audit-logs/?search=ALERT_STATUS_CHANGED
/api/audit-logs/?ordering=created_at
```

## Brute-Force Detection

The demonstration detection rule checks failed login events from the same source IP within a five-minute window.

- **Threshold:** Five failed login attempts.
- **Detection window:** Five minutes.
- **Alert severity:** High.

When the threshold is reached, the system can generate a potential brute-force alert. This rule is intended for demonstration and does not establish that an attack has definitely occurred.

## Testing

Run the backend checks from the `backend` directory:

```bash
python manage.py check
python manage.py test monitoring
```

Build the frontend from the `frontend` directory:

```bash
npm run build
```

## Security Considerations

- Keep secret keys, passwords, tokens, and `.env` files out of version control.
- Use environment variables and a strong, private Django secret key outside local development.
- Restrict CORS to trusted frontend origins.
- Enforce appropriate authorization for alert updates and event ingestion.
- Use HTTPS, secure deployment settings, and a production database before deployment.
- Use synthetic test events when demonstrating detection rules.
- Treat logs as potentially sensitive data and apply suitable access controls.

**Disclaimer:** This project is intended for educational and portfolio purposes. It is not a production-ready SIEM.

## Roadmap

- [ ] Expand detection rules for suspicious activity.
- [ ] Add additional automated security tests.
- [ ] Improve dashboard filtering and investigation workflows.
- [ ] Configure and test PostgreSQL integration.
- [ ] Prepare a secure deployment configuration.

## Author

**Muhammad Abubakar**

GitHub: [M-Abubakar24](https://github.com/M-Abubakar24)
