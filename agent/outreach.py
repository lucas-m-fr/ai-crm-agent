import uuid
from datetime import datetime
from db.database import get_conn, TERMINAL_STATES
from db.guardrails import is_suppressed


def send_email(prospect_id: int, is_follow_up: bool = False) -> bool:
    with get_conn() as conn:
        prospect = conn.execute(
            "SELECT * FROM prospects WHERE id = ?", (prospect_id,)
        ).fetchone()

        if not prospect:
            print(f"[BLOCKED] Prospect ID {prospect_id} not found.")
            return False

        email = prospect["email"]
        status = prospect["status"]

        # 1. Hard check against global suppression list
        if is_suppressed(email):
            print(f"[BLOCKED] {email} is on the global suppression list.")
            return False

        # 2. Hard check against state machine rules
        if not is_follow_up and status != "NEW":
            print(f"[BLOCKED] {email} already in state '{status}'. Cannot double-contact.")
            return False

        if status in TERMINAL_STATES:
            print(f"[BLOCKED] {email} is in terminal state '{status}'.")
            return False

        # Generate deterministic Message-ID for header-based reply tracking
        msg_id = f"<{uuid.uuid4()}@yourcompany.com>"
        now = datetime.now().isoformat()

        # Determine next state
        if status == "NEW":
            next_status = "CONTACTED"
        elif status == "CONTACTED":
            next_status = "FOLLOW_UP_1"
        elif status == "FOLLOW_UP_1":
            next_status = "FOLLOW_UP_2"
        else:
            print(f"[STOPPED] {email} reached max follow-ups.")
            return False

        # --- SWAP IN YOUR SMTP / GMAIL API CALL HERE ---
        print(f"[SENT] To: {email} | State: {status} -> {next_status} | Msg-ID: {msg_id}")

        conn.execute(
            """
            UPDATE prospects
            SET status = ?, last_message_id = ?, last_contacted_at = ?
            WHERE id = ?
            """,
            (next_status, msg_id, now, prospect_id),
        )
        return True
