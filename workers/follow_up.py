from datetime import datetime, timedelta
from db.database import get_conn
from agent.outreach import send_email


def run_follow_up_worker(days_threshold: int = 3):
    cutoff = (datetime.now() - timedelta(days=days_threshold)).isoformat()
    with get_conn() as conn:
        stale_prospects = conn.execute(
            """
            SELECT id, email, status FROM prospects
            WHERE status IN ('CONTACTED', 'FOLLOW_UP_1')
            AND last_contacted_at < ?
            """,
            (cutoff,),
        ).fetchall()

        print(f"\n[WORKER] Found {len(stale_prospects)} prospect(s) due for follow-up.")
        for p in stale_prospects:
            send_email(p["id"], is_follow_up=True)
