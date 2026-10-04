from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.security import hash_password
from app.db.database import Base, SessionLocal, engine
from app.db.models import User


def create_tables_and_admin():
    # For this training project, create_all makes the first run simple.
    # Use Alembic migrations for controlled production schema changes.
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "viraj@abc.com").first()
        if not existing:
            db.add(
                User(
                    email="viraj@abc.com",
                    password_hash=hash_password("viraj@123"),
                    role="admin",
                )
            )
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables_and_admin()
    yield


app = FastAPI(
    title="Employee & Company Management API",
    version="1.0.0",
    description="Training project based on the supplied FastAPI assignment.",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "Employee & Company Management API",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
