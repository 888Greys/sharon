# Security & Deployment Guide

This document outlines the security measures implemented in the **ICT Help Desk Support System** and provides deployment instructions.

## 1. Security Features ("Elite" Tech)

The system is built on **Django 5**, which includes robust security mechanisms out of the box.

### A. CSRF Protection (Cross-Site Request Forgery)
- **What it is**: Prevents malicious websites from performing actions on behalf of authenticated users without their consent.
- **Implementation**: Every form (login, ticket creation) includes a `{% csrf_token %}` tag. Django validates this token on every POST request.
- **Defense Answer**: "We used Django's middleware to enforce strict CSRF validation, ensuring that all state-changing requests originate from our trusted domain."

### B. SQL Injection Prevention
- **What it is**: Ensuring that user input cannot alter database queries to expose or delete data.
- **Implementation**: We use Django's ORM (Object-Relational Mapper) which automatically parameterizes queries.
- **Defense Answer**: "The system uses Python's ORM to abstract database interactions. All inputs are sanitized and parameterized, making SQL injection mathematically impossible in standard usage."

### C. Password Hashing (PBKDF2)
- **What it is**: Storing passwords as encrypted hashes, not plain text.
- **Implementation**: Django uses `PBKDF2` with a SHA-256 hash by default, with 600,000 iterations (in Django 5.0).
- **Defense Answer**: "User credentials are protected using the industry-standard PBKDF2 algorithm with SHA-256 hashing, compliant with NIST security guidelines."

### D. XSS Protection (Cross-Site Scripting)
- **What it is**: Preventing users from injecting malicious JavaScript into pages.
- **Implementation**: Django templates automatically escape specific characters in variables.

---

## 2. Deployment (Docker & Render)

The application is containerized using **Docker**, making it cloud-agnostic and scalable.

### Prerequisites
- Docker & Docker Compose installed.

### Local Development (SQLite)
Run the server locally:
```bash
python manage.py runserver
```

### Production Deployment (Docker + PostgreSQL)
We use `gunicorn` as the production application server and `whitenoise` for static files.

1. **Build and Run**:
   ```bash
   docker-compose up --build
   ```

2. **Access**:
   The app will be available at `http://localhost:8000`.

### Cloud Hosting (Render.com)
1. Push code to GitHub.
2. Connect repo to Render.
3. Add Environment Variables:
   - `DATABASE_URL`: (Internal DB URL from Render PostgreSQL)
   - `SECRET_KEY`: (Generate a strong key)
   - `DEBUG`: `False`
4. Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
5. Start Command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
