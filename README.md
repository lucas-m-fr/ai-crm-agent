# AI Sales CRM Agent

An automated outbound sales agent that manages prospect lifecycles using a strict state machine, header-based inbox matching, and a global suppression list.

## System Flow
1. **Outreach (`agent/outreach.py`)**: Checks `db/guardrails.py` before sending. Generates a unique `Message-ID` and sets status to `CONTACTED`.
2. **Inbox Reader (`agent/inbox_reader.py`)**: Matches incoming `In-Reply-To` headers to `last_message_id` and routes the body to `agent/classifier.py`.
3. **State & Suppression (`db/database.py`)**: Updates status (`RESPONDED`, `DECLINED`, `OPTED_OUT`) and writes opt-outs to `suppression_list`.
4. **Follow-up Worker (`workers/follow_up.py`)**: Queries stale `CONTACTED` / `FOLLOW_UP_1` prospects and triggers follow-ups if not suppressed.

## Quick Start
```bash
python main.py
```
