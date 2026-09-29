from datetime import datetime

from sqlalchemy import (
    create_engine,
    String,
    Integer,
    Float,
    Text,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)

from .config import settings


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# --------------------------------------------------
# BASE CLASS
# --------------------------------------------------

class Base(DeclarativeBase):
    pass


# --------------------------------------------------
# USER TABLE
# --------------------------------------------------

class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    age: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    weight: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    goal: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    intensity: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    plans: Mapped[list["FitnessPlan"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


# --------------------------------------------------
# FITNESS PLAN TABLE
# --------------------------------------------------

class FitnessPlan(Base):

    __tablename__ = "fitness_plans"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    workout_plan: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    nutrition_tip: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    updated_plan: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    user: Mapped[User] = relationship(
        back_populates="plans"
    )


# --------------------------------------------------
# CREATE DATABASE TABLES
# --------------------------------------------------

def create_tables():

    Base.metadata.create_all(
        bind=engine
    )


# --------------------------------------------------
# DATABASE DEPENDENCY
# --------------------------------------------------

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()