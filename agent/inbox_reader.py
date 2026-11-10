from typing import Optional
from db.database import get_conn
from db.guardrails import add_to_suppression
from agent.classifier import classify_reply_intent


def process_inbox_reply(sender_email: str, body: str, in_reply_to: Optional[str] = None):
    with get_conn() as conn:
        prospect = None

        # 1. Primary Match: Header-based (In-Reply-To -> last_message_id)
        if in_reply_to:
            prospect = conn.execute(
                "SELECT * FROM prospects WHERE last_message_id = ?", (in_reply_to,)
            ).fetchone()

        # 2. Fallback Match: Sender email
        if not prospect:
            prospect = conn.execute(
                "SELECT * FROM prospects WHERE email = ?", (sender_email.lower(),)
            ).fetchone()

        if not prospect:
            print(f"[INBOX] Unmatched reply from {sender_email}. Ignoring.")
            return

        intent = classify_reply_intent(body)
        print(f"[INBOX] Matched {prospect['email']} (via {'Message-ID' if in_reply_to else 'Email'}) -> Intent: {intent}")

        if intent == "OPT_OUT":
            conn.execute(
                "UPDATE prospects SET status = 'OPTED_OUT' WHERE id = ?", (prospect["id"],)
            )
            add_to_suppression(prospect["email"], "User opted out via email reply")
            print(f"[ACTION] {prospect['email']} marked OPTED_OUT and added to suppression list.")
        elif intent == "DECLINED":
            conn.execute(
                "UPDATE prospects SET status = 'DECLINED' WHERE id = ?", (prospect["id"],)
            )
            print(f"[ACTION] {prospect['email']} marked DECLINED. Follow-ups halted.")
        else:
            conn.execute(
                "UPDATE prospects SET status = 'RESPONDED' WHERE id = ?", (prospect["id"],)
            )
            print(f"[ACTION] {prospect['email']} marked RESPONDED. Ready for human handoff.")
