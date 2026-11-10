from datetime import datetime
from db.database import get_conn


def is_suppressed(email: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM suppression_list WHERE email = ?", (email.lower(),)
        ).fetchone()
        return row is not None


def add_to_suppression(email: str, reason: str):
    with get_conn() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO suppression_list (email, reason, added_at)
            VALUES (?, ?, ?)
            """,
            (email.lower(), reason, datetime.now().isoformat()),
        )
