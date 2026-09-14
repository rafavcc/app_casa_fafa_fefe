from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    String, Integer, Float, DateTime, 
    ForeignKey, CheckConstraint, UniqueConstraint, Index
)
    
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.database import Base

FAFA = "FAFA"
FEFE = "FEFE"
PAYERS = (FAFA, FEFE)
DEFAULT_FAFA_RATIO = 6/10

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    """
    Represents one user that can pay for expenses
    'Fafa' or 'Fefe'
    Name is a primary key
    """

    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String, primary_key=True)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)

    variable_expenses : Mapped[list["VariableExpense"]] = relationship(back_populates ="payer", lazy="raise_on_sql")
    regular_expenses : Mapped[list["RegularExpense"]] = relationship(back_populates="payer", lazy = "raise_on_sql")

class VariableCategory(Base):
    __tablename__ = "variable_categories"

    name : Mapped[str] = mapped_column(String, primary_key=True)
    expenses : Mapped[list["VariableExpense"]] = relationship(back_populates="category", lazy="raise_on_sql")

class RegularCategory(Base):
    __tablename__ = "regular_categories"

    name: Mapped[str] = mapped_column(String, primary_key=True)
    expenses : Mapped[list["RegularExpense"]] = relationship( back_populates="category", lazy="raise_on_sql")

class MonthRatio(Base):
    __tablename__ = "month_ratios"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    month : Mapped[int] = mapped_column(Integer, nullable=False)
    year : Mapped[int] = mapped_column(Integer, nullable=False)
    fafa_ratio : Mapped[float] = mapped_column(Float, nullable=False, default=DEFAULT_FAFA_RATIO)

    @property
    def fefe_ratio(self) -> float:
        return round(1.0 - self.fafa_ratio, 2)

    __table_args__ = (
        UniqueConstraint("month", "year", name="uq_month_ratio"),
        CheckConstraint("month BETWEEN 1 AND 12", name="ck_ratio_month"),
        CheckConstraint("fafa_ratio > 0 AND fafa_ratio < 1", name="ck_ratio_range"),
        Index("ix")
    )

class VariableExpense(Base):
    __tablename__ = "variable_expenses"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    place : Mapped[str] = mapped_column(String, nullable=False)
    day : Mapped[int] = mapped_column(Integer, nullable=False)
    month : Mapped[int] = mapped_column(Integer, nullable=False)
    year : Mapped[int] = mapped_column(Integer, nullable=False)
    value : Mapped[float] = mapped_column(Float, nullable=False)
    paid_by : Mapped[str] = mapped_column(String, ForeignKey("users.name"), nullable=False)
    category_name : Mapped[str] = mapped_column(String, ForeignKey("variable_categories.name"), nullable = False)
    notes : Mapped[str | None] = mapped_column(String, nullable=True)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda:datetime.now(timezone.utc))
    payer : Mapped["User"] =  relationship(back_populates = "variable_expenses")
    category : Mapped["VariableCategory"] = relationship(back_populates="expenses")

    __table_args__ = (
        CheckConstraint("day BETWEEN 1 AND 31", name="ck_var_day"),
        CheckConstraint("month BETWEEN 1 AND 12", name="ck_var_day"),
        CheckConstraint("value > 0", name = "ck_var_value"),
        Index("ix_y_m", "year", "month"),
        Index("ix_y_m_pb_v", "year", "month", "paid_by", "value"),
        Index("ix_y_m_cn", "year", "month", "category_name"),
        Index("ix_p", "place")
    )

class RegularExpense(Base):
    __tablename__ = "regular_expenses"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    place : Mapped[str] = mapped_column(String, nullable=False)
    day : Mapped[int] = mapped_column(Integer, nullable=False)
    month : Mapped[int] = mapped_column(Integer, nullable=False)
    year : Mapped[int] = mapped_column(Integer, nullable=False)
    value : Mapped[float] = mapped_column(Float, nullable=False)
    paid_by : Mapped[str] = mapped_column(String, ForeignKey("users.name"), nullable=False)
    category_name : Mapped[str] = mapped_column(String, ForeignKey("variable_categories.name"), nullable = False)

    notes : Mapped[str | None] = mapped_column(String, nullable=True)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda:datetime.now(timezone.utc))

    payer : Mapped["User"] =  relationship(back_populates = "regular_expenses")
    category : Mapped["RegularCategory"] = relationship(back_populates="expenses")

    __table_args__ = (
        CheckConstraint("day BETWEEN 1 AND 31", name="ck_var_day"),
        CheckConstraint("month BETWEEN 1 AND 12", name="ck_var_day"),
        CheckConstraint("value > 0", name = "ck_var_value"),
        UniqueConstraint("month", "year", "category_name", name = "uq_reg_per_month"),
        Index("ix_y_m_pb_v", "year", "month", "paid_by", "value")
    )
