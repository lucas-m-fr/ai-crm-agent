from datetime import datetime, timedelta
from db.database import get_conn, init_db
from agent.outreach import send_email
from agent.inbox_reader import process_inbox_reply
from workers.follow_up import run_follow_up_worker


def print_crm_state():
    print("\n--- CURRENT CRM STATE ---")
    with get_conn() as conn:
        rows = conn.execute("SELECT id, name, email, status FROM prospects").fetchall()
        for r in rows:
            print(f"ID {r['id']} | {r['name']:<10} | {r['email']:<22} | {r['status']}")
    print("-------------------------\n")


if __name__ == "__main__":
    init_db()

    # Seed test prospects
    with get_conn() as conn:
        conn.executemany(
            "INSERT INTO prospects (name, email) VALUES (?, ?)",
            [
                ("Alice", "alice@acme.com"),
                ("Bob", "bob@globex.com"),
                ("Charlie", "charlie@initech.com"),
            ],
        )

    print("=== STEP 1: INITIAL OUTREACH ===")
    send_email(1)  # Alice
    send_email(2)  # Bob
    send_email(3)  # Charlie
    print_crm_state()

    print("=== STEP 2: SIMULATE INBOX REPLIES ===")
    with get_conn() as conn:
        bob_msg_id = conn.execute("SELECT last_message_id FROM prospects WHERE id = 2").fetchone()[0]

    process_inbox_reply("bob@globex.com", "Please remove me from your list.", in_reply_to=bob_msg_id)
    process_inbox_reply("charlie@initech.com", "Sounds interesting, let's chat next week.")
    print_crm_state()

    print("=== STEP 3: GUARDRAIL TEST (TRYING TO DOUBLE-CONTACT BOB) ===")
    send_email(2)

    print("\n=== STEP 4: FOLLOW-UP WORKER (SIMULATING 4 DAYS PASSED FOR ALICE) ===")
    four_days_ago = (datetime.now() - timedelta(days=4)).isoformat()
    with get_conn() as conn:
        conn.execute("UPDATE prospects SET last_contacted_at = ? WHERE id = 1", (four_days_ago,))

    run_follow_up_worker(days_threshold=3)
    print_crm_state()
