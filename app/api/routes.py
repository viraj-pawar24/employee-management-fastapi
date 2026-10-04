from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.security import (
    create_access_token,
    get_current_user,
    require_roles,
    verify_password,
)
from app.db.database import get_db
from app.db.models import (
    Company,
    Employee,
    EmployeeProfile,
    EmployeeProject,
    Project,
    User,
)
from app.schemas.schemas import (
    AssignmentCreate,
    AssignmentResponse,
    CompanyCreate,
    CompanyResponse,
    CompanyUpdate,
    CompanyWithEmployees,
    EmployeeCreate,
    EmployeeResponse,
    LoginRequest,
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate,
    ProjectCreate,
    ProjectEmployeeResponse,
    ProjectResponse,
    TokenResponse,
)

router = APIRouter(prefix="/api/v1")


def get_company_or_404(db: Session, company_id: int) -> Company:
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


def get_employee_or_404(db: Session, employee_id: int) -> Employee:
    employee = db.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


def get_project_or_404(db: Session, project_id: int) -> Project:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/auth/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(user))


@router.post(
    "/companies",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_company(
    data: CompanyCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "manager")),
):
    company = Company(**data.model_dump())
    db.add(company)
    try:
        db.commit()
        db.refresh(company)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Company name or email already exists")
    return company


@router.get("/companies", response_model=list[CompanyResponse])
def list_companies(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return db.scalars(
        select(Company).offset(skip).limit(limit)
    ).all()


@router.get("/companies/{company_id}", response_model=CompanyWithEmployees)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    company = db.scalar(
        select(Company)
        .options(joinedload(Company.employees))
        .where(Company.id == company_id)
    )
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.patch("/companies/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    data: CompanyUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "manager")),
):
    company = get_company_or_404(db, company_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(company, key, value)
    try:
        db.commit()
        db.refresh(company)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Company name or email already exists")
    return company


@router.delete("/companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    company = get_company_or_404(db, company_id)
    db.delete(company)
    db.commit()


@router.post(
    "/employees",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "manager")),
):
    if not db.get(Company, data.company_id):
        raise HTTPException(status_code=404, detail="Company not found")

    employee = Employee(**data.model_dump())
    db.add(employee)
    try:
        db.commit()
        db.refresh(employee)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Employee email already exists")
    return employee


@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return get_employee_or_404(db, employee_id)


@router.post(
    "/employees/{employee_id}/profile",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_profile(
    employee_id: int,
    data: ProfileCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "manager")),
):
    get_employee_or_404(db, employee_id)

    if db.scalar(
        select(EmployeeProfile).where(EmployeeProfile.employee_id == employee_id)
    ):
        raise HTTPException(status_code=409, detail="Employee already has a profile")

    profile = EmployeeProfile(employee_id=employee_id, **data.model_dump())
    db.add(profile)
    try:
        db.commit()
        db.refresh(profile)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Employee already has a profile")
    return profile


@router.get("/employees/{employee_id}/profile", response_model=ProfileResponse)
def get_profile(
    employee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    get_employee_or_404(db, employee_id)
    profile = db.scalar(
        select(EmployeeProfile).where(EmployeeProfile.employee_id == employee_id)
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.patch("/employees/{employee_id}/profile", response_model=ProfileResponse)
def update_profile(
    employee_id: int,
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "manager")),
):
    get_employee_or_404(db, employee_id)
    profile = db.scalar(
        select(EmployeeProfile).where(EmployeeProfile.employee_id == employee_id)
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/employees/{employee_id}/profile", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(
    employee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "manager")),
):
    get_employee_or_404(db, employee_id)
    profile = db.scalar(
        select(EmployeeProfile).where(EmployeeProfile.employee_id == employee_id)
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    db.delete(profile)
    db.commit()


@router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "manager")),
):
    project = Project(**data.model_dump())
    db.add(project)
    try:
        db.commit()
        db.refresh(project)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Project name already exists")
    return project


@router.post(
    "/projects/{project_id}/employees/{employee_id}",
    response_model=AssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_employee(
    project_id: int,
    employee_id: int,
    data: AssignmentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "manager")),
):
    get_project_or_404(db, project_id)
    get_employee_or_404(db, employee_id)

    assignment = EmployeeProject(
        project_id=project_id,
        employee_id=employee_id,
        role=data.role,
    )
    db.add(assignment)
    try:
        db.commit()
        db.refresh(assignment)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Employee is already assigned to this project",
        )
    return assignment


@router.delete(
    "/projects/{project_id}/employees/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_employee(
    project_id: int,
    employee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "manager")),
):
    get_project_or_404(db, project_id)
    assignment = db.scalar(
        select(EmployeeProject).where(
            EmployeeProject.project_id == project_id,
            EmployeeProject.employee_id == employee_id,
        )
    )
    if not assignment:
        raise HTTPException(status_code=404, detail="Employee assignment not found")
    db.delete(assignment)
    db.commit()


@router.get(
    "/projects/{project_id}/employees",
    response_model=list[ProjectEmployeeResponse],
)
def list_project_employees(
    project_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    get_project_or_404(db, project_id)
    assignments = db.scalars(
        select(EmployeeProject)
        .options(joinedload(EmployeeProject.employee))
        .where(EmployeeProject.project_id == project_id)
    ).all()

    return [
        ProjectEmployeeResponse(
            employee_id=a.employee.id,
            name=a.employee.name,
            email=a.employee.email,
            designation=a.employee.designation,
            role=a.role,
            assigned_at=a.assigned_at,
        )
        for a in assignments
    ]
