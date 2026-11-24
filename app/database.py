import psycopg
from psycopg.rows import dict_row
from contextlib import contextmanager
from app.config import settings

def get_connection():
    """Retorna uma nova conexao com o PostgreSQL."""
    return psycopg.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        dbname=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        row_factory=dict_row
    )

@contextmanager
def get_db_cursor(commit: bool = True):
    """Context manager para operacoes de banco com commit e rollback automaticos."""
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
