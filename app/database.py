import psycopg
from psycopg.rows import dict_row
from contextlib import contextmanager
import time
from app.config import settings

_pg_available = None
_last_check = 0

def is_postgres_available() -> bool:
    global _pg_available, _last_check
    now = time.time()
    # Cacheia o status por 10 segundos para nao travar requisicoes caso o PostgreSQL esteja offline
    if _pg_available is not None and (now - _last_check) < 10:
        return _pg_available

    try:
        with psycopg.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            connect_timeout=1
        ) as conn:
            _pg_available = True
            _last_check = now
            return True
    except Exception:
        _pg_available = False
        _last_check = now
        return False

def get_connection():
    """Retorna uma nova conexao com o PostgreSQL."""
    return psycopg.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        dbname=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        row_factory=dict_row,
        connect_timeout=1
    )

@contextmanager
def get_db_cursor(commit: bool = True):
    """Context manager para operacoes de banco com commit e rollback automaticos."""
    if not is_postgres_available():
        raise psycopg.OperationalError("PostgreSQL indisponivel no momento em localhost:5432.")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
