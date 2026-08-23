from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class VariableExpenseCreate(BaseModel):
	place : str = Field(..., min_length=3, max_length=300)
	day : int = Field(..., ge=1, le=31)
	month : int = Field(..., ge=1, le=12)
	year : int = Field(default_factory=lambda: datetime.now().year)
	value : float = Field(..., gt=0)
	paid_by : str = Field(..., pattern="^(FAFA|FEFE)$")
	category_name : str = Field(..., min_length=1)
	notes : Optional[str] = None

class VariableExpenseResponse(BaseModel):
	id : int
	place : str
	day : int
	month : int
	year : int
	value : float
	paid_by : str
	category_name : str
	notes : Optional[str] = None
	created_at : datetime

	model_config = {"from_attributes":  True}

class RegularExpenseCreate(BaseModel):
        day : int = Field(..., ge=1, le=31)
        month : int = Field(..., ge=1, le=12)
        year : int = Field(default_factory=lambda: datetime.now().year)
        value : float = Field(..., gt=0)
        paid_by : str = Field(..., pattern="^(FAFA|FEFE)$")
        category_name : str = Field(..., min_length=1)
        notes : Optional[str] = None

class RegularExpenseResponse(BaseModel):
        id : int
        day : int
        month : int
        year : int
        value : float
        paid_by : str
        category_name : str
        notes : Optional[str] = None
        created_at : datetime

        model_config = {"from_attributes":  True}

class MonthRatioCreate(BaseModel):
	month : int = Field(..., ge=1, le=12)
	year : int = Field(default_factory = lambda: datetime.now().year)
	fafa_ratio : float = Field(..., gt=0, lt=1, description="Fafa share as decimal")

class MonthRatioResponse(BaseModel):
	id : int
	month : int
	year : int
	fafa_ratio : float
	fefe_ratio : float
	model_config = {"from_attributes" : True}

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
