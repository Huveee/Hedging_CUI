# Tables:
#   participants: 1 row per user (group, completed, decision)
#   answers:      1 row per answer (survey + question_id)

from __future__ import annotations

import os
import sqlite3
import time
from contextlib import contextmanager
from typing import Any, Dict, Optional, Union, Tuple

DB_PATH = os.getenv("STUDY_DB_PATH", "data/app.db")


def _ensure_db_dir() -> None:
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)


@contextmanager
def get_conn():
    _ensure_db_dir()
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    try:
        conn.row_factory = sqlite3.Row

        # Pragmas (good defaults for small web apps)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA busy_timeout = 5000;")

        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Create DB and tables if they don't exist."""
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS participants (
                user_id    TEXT PRIMARY KEY,
                group_no   INTEGER NOT NULL CHECK(group_no IN (0,1,2)),
                completed  INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0,1)),
                decision   TEXT NULL CHECK(decision IN ('Yes','No') OR decision IS NULL),
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS answers (
                user_id     TEXT NOT NULL,
                survey      TEXT NOT NULL,   -- 'gaais' | 'hct' (or other)
                question_id TEXT NOT NULL,
                answer_text TEXT NULL,
                answer_num  REAL NULL,
                updated_at  REAL NOT NULL,
                PRIMARY KEY (user_id, survey, question_id),
                FOREIGN KEY (user_id) REFERENCES participants(user_id) ON DELETE CASCADE
            )
            """
        )

        # Helpful indices for analysis
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_answers_survey_qid ON answers (survey, question_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_participants_group_decision ON participants (group_no, decision)"
        )


# ----------------------------
# Participants
# ----------------------------

def create_participant_if_missing(
    user_id: str,
    group_no: int,
) -> None:
    """
    Idempotent insert. Use on Consent "Go".
    If the user_id already exists, it won't overwrite decision/completed.
    """
    now = time.time()
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO participants (user_id, group_no, completed, decision, created_at, updated_at)
            VALUES (?, ?, 0, NULL, ?, ?)
            ON CONFLICT(user_id) DO NOTHING
            """,
            (user_id, int(group_no), now, now),
        )


def upsert_participant(
    user_id: str,
    group_no: int,
    *,
    completed: Optional[bool] = None,
    decision: Optional[str] = None,
) -> None:
    """
    Update participant fields. group_no is always stored/updated.
    completed/decision are optional; if None, they are left unchanged.
    """
    now = time.time()
    with get_conn() as conn:
        # Ensure row exists
        conn.execute(
            """
            INSERT INTO participants (user_id, group_no, completed, decision, created_at, updated_at)
            VALUES (?, ?, 0, NULL, ?, ?)
            ON CONFLICT(user_id) DO NOTHING
            """,
            (user_id, int(group_no), now, now),
        )

        sets = ["group_no = ?", "updated_at = ?"]
        params: list[Any] = [int(group_no), now]

        if completed is not None:
            sets.append("completed = ?")
            params.append(1 if completed else 0)

        if decision is not None:
            if decision not in ("Yes", "No"):
                raise ValueError("decision must be 'Yes' or 'No'")
            sets.append("decision = ?")
            params.append(decision)

        params.append(user_id)

        conn.execute(
            f"UPDATE participants SET {', '.join(sets)} WHERE user_id = ?",
            tuple(params),
        )


def mark_completed(user_id: str, completed: bool = True) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE participants SET completed = ?, updated_at = ? WHERE user_id = ?",
            (1 if completed else 0, time.time(), user_id),
        )


def set_decision(user_id: str, decision: str) -> None:
    if decision not in ("Yes", "No"):
        raise ValueError("decision must be 'Yes' or 'No'")
    with get_conn() as conn:
        conn.execute(
            "UPDATE participants SET decision = ?, updated_at = ? WHERE user_id = ?",
            (decision, time.time(), user_id),
        )


def get_participant(user_id: str) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT user_id, group_no, completed, decision, created_at, updated_at FROM participants WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        if not row:
            return None
        return {
            "user_id": row["user_id"],
            "group": row["group_no"],
            "completed": bool(row["completed"]),
            "decision": row["decision"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }


def is_completed(user_id: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT completed FROM participants WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        return bool(row["completed"]) if row else False


# ----------------------------
# Answers
# ----------------------------

AnswerType = Union[str, int, float, None]


def upsert_answer(
    user_id: str,
    survey: str,
    question_id: str,
    answer: AnswerType,
) -> None:
    """
    Store one answer.
    - Likert/text -> answer_text
    - Numeric     -> answer_num
    - None        -> clears both
    """
    if not survey:
        raise ValueError("survey cannot be empty")
    if not question_id:
        raise ValueError("question_id cannot be empty")

    answer_text: Optional[str] = None
    answer_num: Optional[float] = None

    if answer is None:
        pass
    elif isinstance(answer, (int, float)):
        answer_num = float(answer)
    else:
        answer_text = str(answer)

    now = time.time()
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO answers (user_id, survey, question_id, answer_text, answer_num, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, survey, question_id) DO UPDATE SET
                answer_text = excluded.answer_text,
                answer_num  = excluded.answer_num,
                updated_at  = excluded.updated_at
            """,
            (user_id, survey, question_id, answer_text, answer_num, now),
        )


def upsert_answers_bulk(
    user_id: str,
    survey: str,
    answers: Dict[str, AnswerType],
) -> None:
    """Store multiple answers for the same survey."""
    for qid, ans in answers.items():
        upsert_answer(user_id, survey, qid, ans)


def get_answers(user_id: str, survey: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns answers as a dict: question_id -> value (num or text)
    If survey is None, returns all surveys flattened as: (survey, question_id) tuples are NOT used;
    instead it returns a nested dict: {survey: {question_id: value}}
    """
    with get_conn() as conn:
        if survey is None:
            rows = conn.execute(
                """
                SELECT survey, question_id, answer_text, answer_num
                FROM answers
                WHERE user_id = ?
                ORDER BY survey, question_id
                """,
                (user_id,),
            ).fetchall()

            out: Dict[str, Dict[str, Any]] = {}
            for r in rows:
                val = r["answer_num"] if r["answer_num"] is not None else r["answer_text"]
                out.setdefault(r["survey"], {})[r["question_id"]] = val
            return out

        rows = conn.execute(
            """
            SELECT question_id, answer_text, answer_num
            FROM answers
            WHERE user_id = ? AND survey = ?
            ORDER BY question_id
            """,
            (user_id, survey),
        ).fetchall()

        out2: Dict[str, Any] = {}
        for r in rows:
            out2[r["question_id"]] = r["answer_num"] if r["answer_num"] is not None else r["answer_text"]
        return out2
