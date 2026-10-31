# Jogging Tracker

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-2.2-092E20?logo=django&logoColor=white)
![Django REST Framework](https://img.shields.io/badge/DRF-3.9-A30000?logo=django&logoColor=white)
![Database](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)

A Django and Django REST Framework application for recording jogging sessions, calculating average speed, and reviewing weekly running statistics.

The project includes a Vue 3 single-page interface served by Django. All authenticated actions are performed through the REST API using AJAX requests, so the page does not need to be refreshed after creating, updating, filtering, or deleting a run.

## Table of Contents

- [Features](#-features)
- [Roles and Permissions](#-roles-and-permissions)
- [Quickstart](#-quickstart)
- [Configuration and Security](#-configuration-and-security)
- [GitHub and Render Deployment](#-github-and-render-deployment)
- [Using the Application](#-using-the-application)
- [REST API](#-rest-api)
- [Testing](#-testing)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Features

- Create an account and sign in with JWT authentication.
- Add, edit, and delete jogging entries.
- Store the date, distance, and duration for each entry.
- Calculate and display the average speed for every entry.
- Filter entries and reports by an optional date range.
- Generate weekly totals for distance and duration, including average speed.
- Restrict records and user-management actions according to the current user's role.
- Use the REST API directly with tools such as cURL or Postman.
- Use a responsive, minimal Vue 3 interface served from `templates/index.html`.

## 🔐 Roles and Permissions

The application supports three roles:

| Role | Permissions |
| --- | --- |
| Regular user (`USER`) | Create, view, update, and delete their own jogging entries. |
| User manager (`MANAGER`) | Manage users and their own jogging entries. |
| Administrator (`ADMIN`) | Manage users and view or manage all jogging entries. Administrators can assign a new entry to another user. |

New accounts are created as regular users. Roles are stored on the user's `UserProfile`.

## ⚡ Quickstart

### Windows PowerShell

Create a virtual environment, install the dependencies, apply migrations, and start the development server:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

### macOS or Linux

```shell
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python manage.py migrate
./.venv/bin/python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in a browser.

The default database is the SQLite file `db.sqlite3`. For a new installation, `manage.py migrate` creates the required Django tables.

## ⚙️ Configuration and Security

The checked-in settings are intended for local development only:

- `DEBUG` is enabled.
- CORS allows all origins.
- The Django `SECRET_KEY` is currently defined in `server/settings.py`.
- SQLite is used as the default database.

Before deploying publicly, set `DJANGO_SECRET_KEY`, restrict `DJANGO_ALLOWED_HOSTS` and CORS origins, disable `DEBUG`, and use a production-ready database and web server. Never reuse the development secret in production. A template is provided in `.env.example`.

## ☁️ GitHub and Render Deployment

### Upload to GitHub

Create an empty repository on GitHub, then run these commands from the project directory:

```shell
git init
git add .
git commit -m "Initial project setup"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repository>.git
git push -u origin main
```

Do not commit `.env`, virtual environments, or `db.sqlite3`; they are excluded by `.gitignore`.

### Deploy on Render

After pushing the repository:

1. In Render, choose **New → Web Service** and connect the GitHub repository.
2. Select **Python 3**.
3. Use `pip install -r requirements.txt` as the build command.
4. Use `gunicorn server.wsgi:application` as the start command.
5. Add these environment variables:
   - `DJANGO_SECRET_KEY`: a long, random secret
   - `DJANGO_ALLOWED_HOSTS`: your Render hostname, such as `jogging-tracker.onrender.com`
6. Deploy, then run migrations with `python manage.py migrate` using Render's shell or a release command.

The included `Procfile` supplies the Gunicorn start command. SQLite is suitable for local development but is ephemeral on many cloud platforms; use a managed PostgreSQL database for persistent production data and configure Django's database settings before going live.

## 🏃 Using the Application

1. Select **Create account** and register with a username, email address, and password.
2. Sign in with the new account.
3. Add a run with its distance, duration, and date.
4. Use the date filters to narrow the run list and weekly report.
5. Edit or delete an existing run from the **Runs** table.
6. Sign out when finished.

Distance is entered in kilometres and duration in minutes. The displayed average speed uses the same values as the API calculation: `distance / duration`.

## 🌐 REST API

All API paths are under `/api/`. Login and registration are public; the remaining endpoints require a JWT bearer token.

### Authentication

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/auth/signup/` | Create a regular user account. |
| `POST` | `/api/auth/login/` | Authenticate and return a JWT token and user details. |

Example login request:

```shell
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"runner","password":"strong-pass-123"}'
```

For PowerShell, use a one-line request:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/auth/login/ -H "Content-Type: application/json" -d '{"username":"runner","password":"strong-pass-123"}'
```

Use the returned token on protected requests:

```text
Authorization: Bearer your-jwt-token
```

### Jogging entries

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/entry/` | List entries visible to the authenticated user. |
| `POST` | `/api/entry/` | Create an entry. |
| `GET` | `/api/entry/<id>/` | Retrieve one entry. |
| `PUT` | `/api/entry/<id>/` | Update one entry. |
| `DELETE` | `/api/entry/<id>/` | Delete one entry. |

Add `from` and/or `to` query parameters to filter by date:

```text
/api/entry/?from=2026-01-01&to=2026-01-31
```

An entry contains `distance`, `duration`, and `date`. Responses also include the owner, entry ID, and calculated `average_speed`.

### User management

Users with the `MANAGER` or `ADMIN` role can use the user endpoint:

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/user/` | List users. |
| `POST` | `/api/user/` | Create a regular user. |
| `GET` | `/api/user/<id>/` | Retrieve a user. |
| `PUT` | `/api/user/<id>/` | Update a user. |
| `DELETE` | `/api/user/<id>/` | Delete a user. |

### Weekly report

```text
GET /api/weekly-report/
GET /api/weekly-report/?from=2026-01-01&to=2026-01-31
```

The response groups entries by year and week and returns:

- `total_distance`
- `total_duration`
- `average_speed`

The legacy alias `/api/weeklyReport/` is also available.

## 🧪 Testing

Run the API test suite with:

### Windows PowerShell

```powershell
.\.venv\Scripts\python.exe manage.py test api
```

### macOS or Linux

```shell
./.venv/bin/python manage.py test api
```

The tests cover registration, password hashing, authentication failures, entry ownership, date filtering, weekly reports, administrator access, and user-management permissions.

## 📁 Project Structure

```text
api/
  models.py       User profiles and jogging entries
  serializers.py  REST request and response serializers
  permissions.py  Role and ownership permissions
  views.py        Authentication, CRUD, and reporting endpoints
  tests.py        REST API tests
server/
  settings.py     Django and REST framework configuration
  urls.py         Application routing
templates/
  index.html      Vue 3 single-page interface
manage.py         Django command-line entry point
requirements.txt  Python dependencies
```

## 🤝 Contributing

1. Create a feature branch.
2. Make focused changes and add or update tests where appropriate.
3. Run `python manage.py test api`.
4. Open a pull request describing the change and its validation.

Bug reports and feature requests are welcome through GitHub Issues.

## 📄 License

No license has been specified for this project yet. Add a `LICENSE` file before distributing or accepting external contributions.
