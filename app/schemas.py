from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, ConfigDict

from typing import Optional
from datetime import datetime
from enum import Enum

FROM_ATTRIBUTES = ConfigDict(from_attributes=True)

def _current_year() -> int:
	return datetime.now().year

class Payer(str, Enum):
    FAFA = "FAFA"
    FEFE = "FEFE"

class ExpenseBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    day : int = Field(..., ge=1, le=31)
    month : int = Field(..., ge=1, le=12)
    year : int = Field(default_factory=lambda: datetime.now().year)
    value : float = Field(..., gt=0)
    paid_by : str = Field(..., pattern="^(FAFA|FEFE)$")
    category_name : str = Field(..., min_length=1)
    notes : str | None = Field(default=None, max_length=1000)

    @field_validator("category_name", "notes")
    @classmethod
    def _strip(cls, value : str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

class VariableExpenseCreate(ExpenseBase):
    place : str = Field(..., min_length=3, max_length=300)
    

class RegularExpenseCreate(BaseModel):
    pass

class ExpenseRead(BaseModel):
    id: int
    day: int
    month : int
    year : int
    value: float
    paid_by : str
    category_name: str
    notes : str | None = None
    created_at = datetime
    model_config = FROM_ATTRIBUTES


class RegularExpenseResponse(ExpenseRead):
     pass

class VariableExpenseResponse(ExpenseRead):
    place: str
    pass

class MonthRatioCreate(BaseModel):
	month : int = Field(..., ge=1, le=12)
	year : int = Field(default_factory = _current_year, ge=2000, le=2100)
	fafa_ratio : float = Field(..., gt=0, lt=1, description="Fafa share as decimal")

class MonthRatioResponse(BaseModel):
    month : int
    year : int
    fafa_ratio : float
    fefe_ratio : float
    model_config = FROM_ATTRIBUTES

class MonthlyBalance(BaseModel):
    """
    Full monthly balance calculation
    """

    month : int
    year : int
    total_expenses: float
    variable_total: float
    regular_total : float
    fafa_ratio : float
    fefe_ratio : float
    fafa_should_pay : float
    fefe_should_pay : float
    fafa_paid : float
    fefe_paid : float
    balance : float
    debtor: str | None = None
    creditor: str | None = None
    settlement: float = 0.0

    model_config = FROM_ATTRIBUTES