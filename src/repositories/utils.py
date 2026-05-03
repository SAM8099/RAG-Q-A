import psycopg2
import psycopg2.extras
from src.modules.config import DATABASE_URL


def get_connection():

    return psycopg2.connect(DATABASE_URL)


def init_db() -> None:
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS history (
        id          SERIAL PRIMARY KEY,
        topic       VARCHAR(100)    NOT NULL,
        difficulty  VARCHAR(20)     NOT NULL,
        questions   JSONB           NOT NULL,
        created_at  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
    );
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(create_table_query)
        conn.commit()
    finally:
        conn.close()