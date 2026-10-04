import os

os.environ["DATABASE_URL"] = "sqlite:///./test_employee_management.db"
os.environ["SECRET_KEY"] = "test-secret"

from fastapi.testclient import TestClient

from app.main import app
from app.db.database import Base, engine

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


client = TestClient(app)


def test_login():
    # The startup event creates the default admin.
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "Admin@123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def get_token():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "Admin@123"},
    )
    return response.json()["access_token"]


def test_company_and_employee():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    company = client.post(
        "/api/v1/companies",
        headers=headers,
        json={
            "name": "ABC Technologies",
            "email": "abc@example.com",
            "status": "active",
        },
    )
    assert company.status_code == 201
    company_id = company.json()["id"]

    employee = client.post(
        "/api/v1/employees",
        headers=headers,
        json={
            "company_id": company_id,
            "name": "Rahul Sharma",
            "email": "rahul@example.com",
            "designation": "Backend Developer",
            "status": "active",
        },
    )
    assert employee.status_code == 201
    employee_id = employee.json()["id"]

    company_details = client.get(
        f"/api/v1/companies/{company_id}",
        headers=headers,
    )
    assert company_details.status_code == 200
    assert len(company_details.json()["employees"]) == 1

    profile = client.post(
        f"/api/v1/employees/{employee_id}/profile",
        headers=headers,
        json={
            "phone": "9876543210",
            "address": "Mumbai",
            "bio": "Python developer",
        },
    )
    assert profile.status_code == 201

    duplicate_profile = client.post(
        f"/api/v1/employees/{employee_id}/profile",
        headers=headers,
        json={
            "phone": "9999999999",
            "address": "Pune",
            "bio": "Second profile",
        },
    )
    assert duplicate_profile.status_code == 409


def test_project_assignment_and_duplicate_prevention():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    company = client.post(
        "/api/v1/companies",
        headers=headers,
        json={
            "name": "Project Company",
            "email": "project-company@example.com",
            "status": "active",
        },
    )
    company_id = company.json()["id"]

    employee = client.post(
        "/api/v1/employees",
        headers=headers,
        json={
            "company_id": company_id,
            "name": "Amit",
            "email": "amit@example.com",
            "designation": "Developer",
            "status": "active",
        },
    )
    employee_id = employee.json()["id"]

    project = client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "name": "ERP Project",
            "description": "Employee management ERP",
            "status": "active",
        },
    )
    project_id = project.json()["id"]

    assignment = client.post(
        f"/api/v1/projects/{project_id}/employees/{employee_id}",
        headers=headers,
        json={"role": "Backend Developer"},
    )
    assert assignment.status_code == 201

    duplicate = client.post(
        f"/api/v1/projects/{project_id}/employees/{employee_id}",
        headers=headers,
        json={"role": "Backend Developer"},
    )
    assert duplicate.status_code == 409

    employees = client.get(
        f"/api/v1/projects/{project_id}/employees",
        headers=headers,
    )
    assert employees.status_code == 200
    assert len(employees.json()) == 1
