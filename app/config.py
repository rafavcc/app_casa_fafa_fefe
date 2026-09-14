import os
import secrets

from dataclasses import dataclass
from functools import lru_cache

def _flag(name: str, default: bool = False):
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}

@dataclass(frozen=True, slots=True)
class Settings:
    database_url: str
    echo_sql: bool
    storage_secret: str
    autofill_on_startup: bool
    max_page_size: int

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv("CASA_DATABASE_URL", "Asqlite:///./casa.db"),
        echo_sql=_flag("CASA_ECHO_SQL", False),
        storage_secret=os.getenv("CASA_STORAGE_SECRET"),
        autofill_on_startup=_flag("CASA_AUTOFILL_ON_STARTUP", "True"),
        max_page_size=int(os.getenv("CASA_MAX_PAGE_SIZE", "500"))
    )


settings = get_settings()