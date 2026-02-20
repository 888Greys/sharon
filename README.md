# ICT Help Desk Support System

Django-based help desk application for managing users, tickets, and reports.

## Tech Stack
- Python 3.11+
- Django 5
- SQLite (default and only configured database)

## Local Setup (SQLite)
1. Open a terminal in the project root:
   ```bash
   cd "I:/Sharon project/sharon"
   ```
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate the environment:
   ```bash
   .venv/Scripts/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Start the development server:
   ```bash
   python manage.py runserver
   ```

Open `http://127.0.0.1:8000/` in your browser.

## Useful Commands
- Django checks:
  ```bash
  python manage.py check
  ```
- Run tests:
  ```bash
  python manage.py test
  ```
- Create admin user:
  ```bash
  python manage.py createsuperuser
  ```
- Seed sample data:
  ```bash
  python setup_data.py
  ```

## Create Users by Role
You can create users in two ways:

1. Quick seed (creates an admin + technician + categories):
   ```bash
   python setup_data.py
   ```
   Default seeded accounts:
   - `admin` / `admin123` (role: `admin`)
   - `tech_net` / `password123` (role: `technician`)

2. Manual creation for any role:
   ```bash
   python manage.py shell
   ```
   Then run:
   ```python
   from django.contrib.auth import get_user_model
   User = get_user_model()

   User.objects.create_user(
       username="student1",
       email="student1@example.com",
       password="change-me",
       role="student",
       first_name="Student",
       last_name="One",
   )

   User.objects.create_user(
       username="staff1",
       email="staff1@example.com",
       password="change-me",
       role="staff",
       first_name="Staff",
       last_name="One",
   )

   User.objects.create_user(
       username="tech1",
       email="tech1@example.com",
       password="change-me",
       role="technician",
       first_name="Tech",
       last_name="One",
   )

   User.objects.create_superuser(
       username="admin2",
       email="admin2@example.com",
       password="change-me",
       role="admin",
   )
   ```

## Notes
- Docker files were removed from this project.
- Database data is stored in local SQLite files (`db.sqlite3`).
