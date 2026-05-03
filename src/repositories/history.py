import json
import psycopg2.extras
from src.repositories.utils import get_connection
from src.utils.singleton import Singleton

class HistoryRepository(Singleton):
    
    @staticmethod
    def insert_session(topic: str, difficulty: str, questions: list[dict]) -> int:
        """
        Insert a new Q&A session into the history table.
        Returns the new row's ID.
        """
        query = """
        INSERT INTO history (topic, difficulty, questions)
        VALUES (%s, %s, %s)
        RETURNING id;
        """
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, (topic, difficulty, json.dumps(questions)))
                row_id = cur.fetchone()[0]
            conn.commit()
            return row_id
        finally:
            conn.close()


    @staticmethod
    def get_all_sessions(limit: int = 50) -> list[dict]:
        """
        Fetch all history sessions, most recent first.
        """
        query = """
        SELECT id, topic, difficulty, questions, created_at
        FROM history
        ORDER BY created_at DESC
        LIMIT %s;
        """
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, (limit,))
                rows = cur.fetchall()
            return [
                {
                    "id": row["id"],
                    "topic": row["topic"],
                    "difficulty": row["difficulty"],
                    "questions": row["questions"],
                    "timestamp": row["created_at"].strftime("%Y-%m-%d %H:%M"),
                }
                for row in rows
            ]
        finally:
            conn.close()


    @staticmethod
    def get_session_by_id(session_id: int) -> dict | None:
        """
        Fetch a single session by its ID.
        Returns None if not found.
        """
        query = """
        SELECT id, topic, difficulty, questions, created_at
        FROM history
        WHERE id = %s;
        """
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, (session_id,))
                row = cur.fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "topic": row["topic"],
                "difficulty": row["difficulty"],
                "questions": row["questions"],
                "timestamp": row["created_at"].strftime("%Y-%m-%d %H:%M"),
            }
        finally:
            conn.close()

    @staticmethod
    def get_sessions_by_topic(topic: str) -> list[dict]:
        """
        Fetch all sessions filtered by topic.
        """
        query = """
        SELECT id, topic, difficulty, questions, created_at
        FROM history
        WHERE topic = %s
        ORDER BY created_at DESC;
        """
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, (topic,))
                rows = cur.fetchall()
            return [
                {
                    "id": row["id"],
                    "topic": row["topic"],
                    "difficulty": row["difficulty"],
                    "questions": row["questions"],
                    "timestamp": row["created_at"].strftime("%Y-%m-%d %H:%M"),
                }
                for row in rows
            ]
        finally:
            conn.close()


    @staticmethod
    def delete_session_by_id(session_id: int) -> bool:
        """
        Delete a single session by ID.
        Returns True if a row was deleted, False if not found.
        """
        query = "DELETE FROM history WHERE id = %s RETURNING id;"
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, (session_id,))
                deleted = cur.fetchone()
            conn.commit()
            return deleted is not None
        finally:
            conn.close()

    @staticmethod
    def delete_all_sessions() -> int:
        """
        Delete all history sessions.
        Returns count of deleted rows.
        """
        query = "DELETE FROM history RETURNING id;"
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query)
                count = len(cur.fetchall())
            conn.commit()
            return count
        finally:
            conn.close()

    @staticmethod
    def update_session_questions(session_id: int, questions: list[dict]) -> bool:
        """
        Update questions for an existing session.
        Returns True if updated, False if session not found.
        """
        query = """
        UPDATE history
        SET questions = %s
        WHERE id = %s
        RETURNING id;
        """
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, (json.dumps(questions), session_id))
                updated = cur.fetchone()
            conn.commit()
            return updated is not None
        finally:
            conn.close()