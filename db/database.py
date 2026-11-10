import sqlite3

DB_PATH = "sales_crm.db"

ACTIVE_STATES = {"NEW", "QUEUED", "CONTACTED", "FOLLOW_UP_1", "FOLLOW_UP_2"}
TERMINAL_STATES = {"RESPONDED", "DECLINED", "OPTED_OUT", "BOUNCED"}


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript("""
            DROP TABLE IF EXISTS prospects;
            DROP TABLE IF EXISTS suppression_list;

            CREATE TABLE prospects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL DEFAULT 'NEW',
                last_message_id TEXT,
                last_contacted_at TEXT
            );

            CREATE TABLE suppression_list (
                email TEXT PRIMARY KEY,
                reason TEXT NOT NULL,
                added_at TEXT NOT NULL
            );
        """)
