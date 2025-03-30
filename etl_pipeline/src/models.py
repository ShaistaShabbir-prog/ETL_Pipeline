from sqlalchemy import Date, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


class Employees(Base):
    """Defines the Employee model for storing employee-related data."""

    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    date_of_birth: Mapped[Date] = mapped_column(Date)
    salary: Mapped[float] = mapped_column(Float)

    def __repr__(self) -> str:
        """Return a string representation of the Employees object."""
        return f"<Employees(id={self.id}, name='{self.name}', date_of_birth='{self.date_of_birth}', salary={self.salary})>"
