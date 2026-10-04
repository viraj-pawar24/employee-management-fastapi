from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CompanyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    status: str = Field(default="active", pattern="^(active|inactive)$")


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    email: EmailStr | None = None
    status: str | None = Field(default=None, pattern="^(active|inactive)$")


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    status: str
    created_at: datetime


class EmployeeCreate(BaseModel):
    company_id: int
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    designation: str = Field(min_length=2, max_length=100)
    status: str = Field(default="active", pattern="^(active|inactive)$")


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    name: str
    email: EmailStr
    designation: str
    status: str


class CompanyWithEmployees(CompanyResponse):
    employees: list[EmployeeResponse] = []


class ProfileCreate(BaseModel):
    phone: str = Field(min_length=7, max_length=30)
    address: str = Field(min_length=2, max_length=255)
    bio: str | None = Field(default=None, max_length=2000)


class ProfileUpdate(BaseModel):
    phone: str | None = Field(default=None, min_length=7, max_length=30)
    address: str | None = Field(default=None, min_length=2, max_length=255)
    bio: str | None = Field(default=None, max_length=2000)


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    phone: str
    address: str
    bio: str | None


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: str = Field(min_length=2, max_length=5000)
    status: str = Field(default="active", pattern="^(active|inactive)$")


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    status: str


class AssignmentCreate(BaseModel):
    role: str = Field(min_length=2, max_length=100)


class AssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    project_id: int
    assigned_at: datetime
    role: str


class ProjectEmployeeResponse(BaseModel):
    employee_id: int
    name: str
    email: EmailStr
    designation: str
    role: str
    assigned_at: datetime
