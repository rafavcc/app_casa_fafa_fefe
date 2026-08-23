from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db, get_session, init_db
from app import crud
from app.schemas import *
from app.balance import calculate_monthly_balance

# ── NiceGUI pages ───────────────────────────────────────
from nicegui import ui
from app.pages.home import build_home
from app.pages.variable import build_variable_expenses
from app.pages.regular import build_regular_expenses
from app.pages.balance import build_balance
from app.theme import apply_app_theme

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with get_session() as db:
        crud.autofill_current_month_regular_expenses(db)
    yield

app = FastAPI(title = "Mansao Fefael", lifespan = lifespan)

@app.post("/api/variable-expense",
          response_model=VariableExpenseResponse)
def add_variable_expense(data : VariableExpenseCreate, db: Session = Depends(get_db)):
    return crud.create_variable_expense(db, data.model_dump())

@app.get("/api/variable-expense", response_model=list[VariableExpenseResponse])
def list_variable_expenses(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = None,
    category : Optional[str] = None,
    db: Session = Depends(get_db)
):
    return crud.get_variable_expenses(db, month=month, year=year, category=category)

@app.delete("/api/variable-expense/{expense_id}")
def remove_variable_expense(expense_id: int, db : Session = Depends(get_db)):
    if not crud.delete_variable_expense(db, expense_id):
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"ok":True}

# ── Regular Expenses ───────────────────────────────────

@app.post("/api/regular-expense", response_model=RegularExpenseResponse)
def add_regular_expense(data: RegularExpenseCreate, db : Session = Depends(get_db)):
    return crud.create_regular_expense(db, data.model_dump())

@app.get("/api/regular-expense", response_model=list[RegularExpenseResponse])
def list_regular_expense(month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)):
    return crud.get_regular_expenses(db, month=month, year=year, category=category)

@app.delete("/api/regular-expense/{expense_id}")
def remove_regular_expense(expense_id: int, db : Session = Depends(get_db)):
    if not crud.delete_regular_expense(db, expense_id):
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"ok": True}

# ── Categories ─────────────────────────────────────────

@app.get("/api/variable-categories")
def list_variable_categories(db: Session = Depends(get_db)):
    return [c.name for c in crud.get_variable_categories(db)]

@app.get("/api/regular-categories")
def list_regular_categories(db: Session = Depends(get_db)):
    return [c.name for c in crud.get_regular_categories(db)]

# ── Month Ratios ───────────────────────────────────────

@app.get("/api/month-ratio")
def get_ratio(month: int, year: int,db : Session = Depends(get_db)):
    r = crud.get_month_ratio(db, month=month, year=year)
    return {"month": month, "year": year, "fafa_ratio": r.fafa_ratio, "fefe_ratio": r.fefe_ratio}

@app.put("/api/month-ratio", response_model=MonthRatioResponse)
def set_ratio(data: MonthRatioCreate, db: Session = Depends(get_db)):
    return crud.set_month_ratio(db, data.month, data.year, data.fafa_ratio)

# ── Balance ────────────────────────────────────────────

@app.get("/api/balance", response_model=MonthlyBalance)
def get_balance(month: int, year: int, db : Session = Depends(get_db)):
    return calculate_monthly_balance(db, month, year)

@app.get("/api/health")
def health():
    """Verify the server is running."""
    return {"status": "ok"}

def _nav_header(title: str, active: str):
    """Shared navigation bar rendered on every page."""
    apply_app_theme()
    items = [
        ("home", "Início", "home", "/"),
        ("variable", "Variáveis", "receipt_long", "/variable"),
        ("regular", "Fixos", "event_repeat", "/regular"),
        ("balance", "Balanço", "account_balance_wallet", "/balance"),
    ]

    with ui.header(elevated=False).classes("casa-header"):
        ui.label(title).classes("text-lg font-bold")
        ui.space()
        with ui.row().classes("casa-nav gap-1 items-center"):
            for key, label, icon, target in items:
                classes = "is-active" if key == active else ""
                ui.button(label, icon=icon, on_click=lambda path=target: ui.navigate.to(path)) \
                    .props("flat dense no-caps") \
                    .classes(classes)
        ui.button(icon="dark_mode", on_click=lambda: ui.run_javascript("window.casaTheme.toggle()")) \
            .props("flat round dense") \
            .classes("ml-2") \
            .tooltip("Alternar tema")

@ui.page("/")
def page_home():
    _nav_header("Mansao Fefael", "home")
    build_home()

@ui.page("/variable")
def page_variable():
    _nav_header("Gastos Variáveis", "variable")
    build_variable_expenses()

@ui.page("/regular")
def page_regular():
    _nav_header("Gastos Fixos", "regular")
    build_regular_expenses()

@ui.page("/balance")
def page_balance():
    _nav_header("Balanço", "balance")
    build_balance()


ui.run_with(app, mount_path="/", storage_secret="casa_fafa_fefe")
