# Employee & Company Management API

Training project based on the supplied FastAPI assignment.

## Stack
- FastAPI
- Python 3.11+
- SQLAlchemy 2.x
- Pydantic v2
- SQLite by default for easy learning/testing
- MySQL/PostgreSQL supported through `DATABASE_URL`
- JWT authentication
- Argon2 password hashing
- pytest
- Uvicorn
- Alembic included as the migration tool

The assignment suggests MySQL/PostgreSQL; SQLite is the default here only to make the project runnable immediately. Set `DATABASE_URL` to MySQL or PostgreSQL for the production-style database.

## Project structure

```text
employee_company_fastapi/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   ├── database.py
│   │   └── models.py
│   ├── schemas/
│   │   └── schemas.py
│   └── api/
│       └── routes.py
├── tests/
│   └── test_api.py
├── alembic/
├── .env.example
├── requirements.txt
└── README.md
```

## 1. Create virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

## 2. Install packages

```bash
pip install -r requirements.txt
```

## 3. Create `.env`

Copy `.env.example` to `.env`.

For the easiest start, keep:

```env
DATABASE_URL=sqlite:///./employee_management.db
SECRET_KEY=change-this-to-a-long-random-secret
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## 4. Start server

```bash
uvicorn app.main:app --reload
```

Open:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Default admin

On startup the application creates this training user if it does not exist:

```text
email: admin@example.com
password: Admin@123
role: admin
```

Change this before using the project outside training.

## Main endpoints

```text
POST   /api/v1/auth/login

POST   /api/v1/companies
GET    /api/v1/companies
GET    /api/v1/companies/{id}
PATCH  /api/v1/companies/{id}
DELETE /api/v1/companies/{id}

POST   /api/v1/employees
GET    /api/v1/employees/{id}
GET    /api/v1/employees/{id}/profile

POST   /api/v1/employees/{id}/profile
PATCH  /api/v1/employees/{id}/profile
DELETE /api/v1/employees/{id}/profile

POST   /api/v1/projects
POST   /api/v1/projects/{id}/employees/{employee_id}
DELETE /api/v1/projects/{id}/employees/{employee_id}
GET    /api/v1/projects/{id}/employees
```

## Authentication

First call login:

```json
{
  "email": "admin@example.com",
  "password": "Admin@123"
}
```

Copy the returned access token into Swagger's **Authorize** button:

```text
Bearer <token>
```

Mutation endpoints require authentication.

## Relationships

### Company -> Employee

One company can have many employees. `employee.company_id` is the foreign key because the "many" side stores the reference to the one company.

### Employee -> EmployeeProfile

One employee has one profile. `employee_profiles.employee_id` has both a foreign key and a UNIQUE constraint. Therefore the database prevents a second profile for the same employee.

### Employee <-> Project

An employee can work on many projects and a project can have many employees. `employee_projects` is the association model. It also stores `assigned_at` and `role`.

A unique constraint on `(employee_id, project_id)` prevents duplicate assignments.

## Error behavior

- 401: missing/invalid JWT
- 403: authenticated but insufficient role
- 404: resource not found
- 409: duplicate email/profile/assignment
- 422: Pydantic validation error

Passwords and password hashes are never returned by the API.

## Run tests

```bash
pytest
```
