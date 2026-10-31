# Jogging Tracker

Jogging Tracker is a small Django project for keeping track of running sessions. It has a simple Vue interface and a REST API behind it.

You can create an account, save your runs, see your average speed, filter runs by date, and view a weekly summary.

## What it includes

- User registration and JWT login
- Add, edit, and delete running entries
- Distance, duration, date, and average speed for each entry
- Date range filtering
- Weekly distance, duration, and speed reports
- Three user roles: regular user, manager, and admin
- REST API for all of the main actions
- A small Vue 3 single-page frontend

## User roles

| Role | Access |
| --- | --- |
| `USER` | Manage their own runs |
| `MANAGER` | Manage users and their own runs |
| `ADMIN` | Manage users and all runs |

New users are given the `USER` role automatically.

## Running it locally

This project uses Python 3.11 and SQLite.

### Windows

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

### macOS/Linux

```bash
python3.11 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python manage.py migrate
./.venv/bin/python manage.py runserver
```

Then open http://127.0.0.1:8000/ in your browser.

The local database is stored in `db.sqlite3`. It is created when the migrations are run.

## API

The API is available under `/api/`. Login and registration do not require authentication. Other endpoints require a token in the request header:

```text
Authorization: Bearer your-jwt-token
```

### Authentication

| Method | URL | Purpose |
| --- | --- | --- |
| `POST` | `/api/auth/signup/` | Create an account |
| `POST` | `/api/auth/login/` | Log in and get a JWT token |

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"runner","password":"strong-pass-123"}'
```

### Running entries

| Method | URL | Purpose |
| --- | --- | --- |
| `GET` | `/api/entry/` | List runs |
| `POST` | `/api/entry/` | Add a run |
| `GET` | `/api/entry/<id>/` | View one run |
| `PUT` | `/api/entry/<id>/` | Update a run |
| `DELETE` | `/api/entry/<id>/` | Delete a run |

Use `from` and `to` to filter by date:

```text
/api/entry/?from=2026-01-01&to=2026-01-31
```

Distance is measured in kilometres and duration is measured in minutes. Average speed is calculated as:

```text
distance / duration
```

### Users

Managers and admins can use `/api/user/` to list, create, update, and delete users.

### Weekly report

```text
GET /api/weekly-report/
GET /api/weekly-report/?from=2026-01-01&to=2026-01-31
```

The report groups runs by year and week and returns the total distance, total duration, and average speed.

## Running the tests

Windows:

```powershell
.\.venv\Scripts\python.exe manage.py test api
```

macOS/Linux:

```bash
./.venv/bin/python manage.py test api
```

## Deployment

The project includes a `Procfile` for running with Gunicorn:

```text
web: gunicorn server.wsgi:application
```

It can be deployed to services such as Render. Set these environment variables on the hosting platform:

- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`

The current SQLite setup is fine for local use, but a hosted deployment should use a persistent database such as PostgreSQL.

The settings in this project are mainly for development. Before deploying publicly, turn off `DEBUG`, restrict allowed hosts and CORS origins, and use a production database.

## Project layout

```text
api/          Models, serializers, views, permissions, and tests
server/       Django project settings and URLs
templates/    Vue single-page interface
manage.py     Django command-line utility
requirements.txt
```

## License

No license has been added yet.
