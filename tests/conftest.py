import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import RegularCategory, User, VariableCategory


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    with session_factory() as db:
        db.add_all([
            User(name="FAFA"),
            User(name="FEFE"),
            VariableCategory(name="Mercado"),
            RegularCategory(name="Aluguel"),
        ])
        db.commit()
        yield db
    engine.dispose()
