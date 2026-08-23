from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    """
    Represents one user that can pay for expenses
    'Fafa' or 'Fefe'
    Name is a primary key
    """

    __tablename__ = "users"
    name = Column(String, primary_key=True)
    full_name = Column(String, nullable=True)

    variable_expenses = relationship("VariableExpense", back_populates ="payer")
    regular_expenses = relationship("RegularExpense", back_populates="payer")

class VariableCategory(Base):
    __tablename__ = "variable_categories"
    name=Column(String, primary_key=True)
    expenses = relationship("VariableExpense", back_populates="category")

class RegularCategory(Base):
    __tablename__ = "regular_categories"
    name=Column(String, primary_key=True)
    expenses = relationship("RegularExpense", back_populates="category")

class MonthRatio(Base):
    __tablename__ = "month_ratios"
    id=Column(Integer, primary_key=True, autoincrement=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    fafa_ratio = Column(Float, nullable=False, default=2/3)

    @property
    def fefe_ratio(self) -> float:
        return round(1.0 - self.fafa_ratio, 2)

    __table_args__ = (
        UniqueConstraint("month", "year", name="uq_month_ratio"),
    )

class VariableExpense(Base):
    __tablename__ = "variable_expenses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    place = Column(String, nullable=False)
    day = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    value =Column(Float, nullable=False)
    paid_by = Column(String, ForeignKey("users.name"), nullable=False)
    category_name = Column(String, ForeignKey("variable_categories.name"), nullable = False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda:datetime.now(timezone.utc))
    payer = relationship("User", back_populates = "variable_expenses")
    category = relationship("VariableCategory", back_populates="expenses")

    __table_args__ = (
        CheckConstraint("day >= 1 AND day <= 31", name="ck_var_day"),
        CheckConstraint("value > 0", name = "ck_var_value")
    )

class RegularExpense(Base):
    __tablename__ = "regular_expenses"
    id = Column(Integer, primary_key=True, autoincrement = True)
    day = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    value = Column(Float, nullable = False)
    paid_by = Column(String, ForeignKey("users.name"), nullable = False)
    category_name = Column(String, ForeignKey("regular_categories.name"), nullable = False)
    notes = Column(String,nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    payer = relationship("User", back_populates = "regular_expenses")
    category = relationship("RegularCategory", back_populates = "expenses")

    __table_args__ = (
        CheckConstraint("day >= 1 AND day <= 31", name = "ck_reg_day"),
        CheckConstraint("value > 0", name = "ck_reg_value"),
        UniqueConstraint("month", "year", "category_name", name = "uq_reg_per_month")
    )
