
import time
import textwrap
import base64
import hashlib
import hmac
import os
import re
import secrets
import sqlite3
from datetime import datetime, timedelta
from io import BytesIO

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_AVAILABLE = True
except ImportError:
    AUTOREFRESH_AVAILABLE = False

try:
    from reportlab.lib import colors as pdf_colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# ============================================================
# SMART KITCHEN HOOD AI DASHBOARD - FULL RESPONSIVE REPAIRED VERSION
# ============================================================

st.set_page_config(
    page_title="Smart Kitchen Hood AI Dashboard",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ========================= CSS =========================

st.markdown(
    """
<style>
.stApp {
    background:
        radial-gradient(circle at 75% 0%, rgba(0, 177, 255, 0.08), transparent 25%),
        linear-gradient(180deg, #07111d 0%, #09131f 100%);
    color: #EAF4FF;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101a2a 0%, #0b1523 100%);
    border-right: 1px solid #26384e;
}

.block-container {
    max-width: 1700px;
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

.dashboard-title {
    font-size: 34px;
    font-weight: 900;
    color: #F5FAFF;
    letter-spacing: -0.03em;
}

.dashboard-subtitle {
    color: #8EA2B7;
    font-size: 13px;
}

.kpi-card {
    background: linear-gradient(145deg, rgba(16,29,45,.98), rgba(9,18,30,.98));
    border: 1px solid #263A52;
    border-radius: 14px;
    padding: 16px;
    min-height: 145px;
    box-shadow: 0 10px 24px rgba(0,0,0,.18);
}

.kpi-label {
    color: #93A7BA;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: .04em;
}

.kpi-value {
    font-size: 29px;
    font-weight: 900;
    margin-top: 4px;
}

.kpi-state {
    font-size: 13px;
    font-weight: 800;
    margin-top: 7px;
}

.panel {
    background: linear-gradient(145deg, rgba(15,28,44,.98), rgba(8,18,30,.98));
    border: 1px solid #263A52;
    padding: 16px;
    border-radius: 14px;
    margin-bottom: 12px;
    box-shadow: 0 8px 22px rgba(0,0,0,.15);
}

.section-title {
    color: #58CBFF;
    font-weight: 900;
    font-size: 14px;
    letter-spacing: .03em;
    margin-bottom: 10px;
}

.status-pill {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 999px;
    font-weight: 900;
    border: 1px solid currentColor;
    background: rgba(255,255,255,.025);
}

.rule-row {
    display:flex;
    justify-content:space-between;
    gap:10px;
    padding:8px 0;
    border-bottom:1px solid rgba(150,180,210,.10);
    font-size:.86rem;
}

.small-note {
    color:#93A7BA;
    font-size:12px;
    line-height:1.55;
}

.metric-box {
    background:#0D1725;
    border:1px solid #263A52;
    border-radius:12px;
    padding:14px;
    text-align:center;
}

.metric-box .label {
    color:#8EA2B7;
    font-size:12px;
}

.metric-box .value {
    color:#F4F9FF;
    font-size:24px;
    font-weight:900;
    margin-top:4px;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(16,29,45,.98), rgba(9,18,30,.98));
    border: 1px solid #263A52;
    border-radius: 14px;
    padding: 14px;
}

div.stButton > button, [data-testid="stDownloadButton"] button {
    border-radius: 10px;
    border: 1px solid #2D5876;
    background: #10243A;
    color: #EAF4FF;
    font-weight: 800;
}

div.stButton > button:hover, [data-testid="stDownloadButton"] button:hover {
    border-color: #20C5FF;
    color: #20C5FF;
}

hr {
    border-color:#26384e;
}


.ai-period-summary-card {
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
}

.ai-period-summary-text {
    font-size: 0.88rem !important;
    line-height: 1.65 !important;
    color: #D8E7F5 !important;
    white-space: normal !important;
    word-break: normal !important;
    overflow-wrap: break-word !important;
    writing-mode: horizontal-tb !important;
    text-orientation: mixed !important;
}

.ai-period-summary-card .section-title {
    white-space: normal !important;
    word-break: normal !important;
    overflow-wrap: break-word !important;
    writing-mode: horizontal-tb !important;
}


/* ================= RESPONSIVE LAYOUT REPAIR ================= */
html, body, [data-testid="stAppViewContainer"], .stApp {
    width: 100%;
    max-width: 100%;
    overflow-x: hidden !important;
}

.block-container {
    width: 100%;
    max-width: 1700px;
    padding-left: 1.25rem;
    padding-right: 1.25rem;
    box-sizing: border-box;
}

[data-testid="stHorizontalBlock"] {
    width: 100%;
    max-width: 100%;
    gap: .75rem;
    align-items: stretch;
}

[data-testid="column"] {
    min-width: 0 !important;
    overflow: visible;
}

.kpi-card, .panel, .metric-box, [data-testid="stMetric"] {
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
    overflow-wrap: anywhere;
}

.dashboard-title {
    font-size: clamp(1.45rem, 3vw, 2.125rem);
    line-height: 1.15;
    overflow-wrap: anywhere;
}

.dashboard-subtitle,
.small-note,
.kpi-label,
.kpi-state,
.rule-row,
.status-pill {
    overflow-wrap: anywhere;
    word-break: normal;
}

.kpi-value {
    font-size: clamp(1.25rem, 2.6vw, 1.8125rem);
    line-height: 1.12;
    overflow-wrap: anywhere;
}

[data-testid="stMetricValue"] {
    font-size: clamp(1.1rem, 2.4vw, 1.75rem) !important;
    overflow-wrap: anywhere;
}

[data-testid="stMetricLabel"] {
    font-size: clamp(.68rem, 1.25vw, .82rem) !important;
}

[data-testid="stPlotlyChart"],
[data-testid="stPlotlyChart"] > div,
.js-plotly-plot,
.plot-container,
.svg-container,
iframe,
img,
svg,
canvas {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box;
}

[data-testid="stDataFrame"],
[data-testid="stTable"] {
    max-width: 100%;
    overflow-x: auto;
}

div.stButton > button,
[data-testid="stDownloadButton"] button {
    width: 100%;
    white-space: normal;
    min-height: 2.6rem;
}



/* Main-area expander repair: keep titles horizontal and readable. */
main [data-testid="stExpander"] summary,
[data-testid="stMain"] [data-testid="stExpander"] summary {
    width: 100% !important;
    min-width: 0 !important;
    display: flex !important;
    align-items: center !important;
    gap: .4rem !important;
    box-sizing: border-box !important;
}

main [data-testid="stExpander"] summary p,
main [data-testid="stExpander"] summary span,
main [data-testid="stExpander"] summary div,
[data-testid="stMain"] [data-testid="stExpander"] summary p,
[data-testid="stMain"] [data-testid="stExpander"] summary span,
[data-testid="stMain"] [data-testid="stExpander"] summary div {
    white-space: normal !important;
    word-break: normal !important;
    overflow-wrap: break-word !important;
    writing-mode: horizontal-tb !important;
    text-orientation: mixed !important;
    line-height: 1.4 !important;
}

/* Sidebar expander repair: prevent headings from breaking letter-by-letter. */
section[data-testid="stSidebar"] [data-testid="stExpander"] {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}

section[data-testid="stSidebar"] [data-testid="stExpander"] details {
    width: 100% !important;
    max-width: 100% !important;
}

section[data-testid="stSidebar"] [data-testid="stExpander"] summary {
    width: 100% !important;
    min-width: 0 !important;
    display: flex !important;
    align-items: center !important;
    gap: .35rem !important;
    padding-left: .65rem !important;
    padding-right: .65rem !important;
    box-sizing: border-box !important;
}

section[data-testid="stSidebar"] [data-testid="stExpander"] summary p,
section[data-testid="stSidebar"] [data-testid="stExpander"] summary span,
section[data-testid="stSidebar"] [data-testid="stExpander"] summary div {
    display: block !important;
    min-width: 0 !important;
    max-width: calc(100% - 1.5rem) !important;
    white-space: nowrap !important;
    word-break: keep-all !important;
    overflow-wrap: normal !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    line-height: 1.35 !important;
    font-size: .82rem !important;
}

section[data-testid="stSidebar"] [data-testid="stExpander"] summary svg {
    width: 1rem !important;
    min-width: 1rem !important;
    height: 1rem !important;
    flex: 0 0 1rem !important;
}

section[data-testid="stSidebar"] [data-testid="stExpander"] label,
section[data-testid="stSidebar"] [data-testid="stExpander"] p {
    word-break: normal !important;
    overflow-wrap: break-word !important;
}

/* Tablet landscape: 9 KPI cards become 3 per row. */
@media screen and (max-width: 1180px) {
    .block-container {
        padding-left: .8rem;
        padding-right: .8rem;
    }

    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: .6rem;
    }

    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        flex: 1 1 calc(33.333% - .6rem) !important;
        width: calc(33.333% - .6rem) !important;
    }

    .kpi-card {
        min-height: 132px;
        padding: 13px;
    }

    section[data-testid="stSidebar"] {
        min-width: 245px !important;
        max-width: 285px !important;
    }
}

/* Tablet portrait: two cards/columns per row. */
@media screen and (max-width: 820px) {
    .block-container {
        padding-top: .75rem;
        padding-left: .55rem;
        padding-right: .55rem;
    }

    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        flex: 1 1 calc(50% - .55rem) !important;
        width: calc(50% - .55rem) !important;
    }

    .dashboard-title,
    .dashboard-subtitle {
        text-align: center;
    }

    .kpi-card,
    .panel,
    [data-testid="stMetric"] {
        padding: 12px;
    }

    .status-pill {
        max-width: 100%;
        white-space: normal;
    }

    section[data-testid="stSidebar"] {
        min-width: 235px !important;
        max-width: 88vw !important;
    }

    h1 { font-size: 1.55rem !important; }
    h2 { font-size: 1.28rem !important; }
    h3 { font-size: 1.08rem !important; }
}

/* Phones: every Streamlit column stacks vertically. */
@media screen and (max-width: 560px) {
    .block-container {
        padding-left: .4rem;
        padding-right: .4rem;
    }

    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: column !important;
        gap: .45rem;
    }

    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        flex: 1 1 100% !important;
        width: 100% !important;
        max-width: 100% !important;
    }

    .kpi-card {
        min-height: auto;
    }

    .rule-row {
        align-items: flex-start;
    }

    .rule-row > span,
    .rule-row > b {
        max-width: 52%;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# ========================= DATABASE LOGIN & USER ROLES =========================
# Feature 1:
# - SQLite user database
# - Secure PBKDF2 password hashing with a unique salt
# - Admin, Lecturer and Judge roles
# - Admin user-management panel
# - Login-attempt lockout
#
# Default accounts created automatically on first run:
# admin     / admin123     / Admin
# lecturer  / lecturer123 / Lecturer
# judge     / judge123     / Judge
#
# IMPORTANT:
# Change or delete the default accounts before real deployment.

DATABASE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "smart_kitchen_hood_users.db",
)

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 30
PBKDF2_ITERATIONS = 310_000
VALID_ROLES = ("Admin", "Lecturer", "Judge")


def get_db_connection():
    """Open SQLite using row objects and a safe timeout."""
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def hash_password(password, salt=None):
    """Return a PBKDF2-SHA256 password hash and its random salt."""
    if salt is None:
        salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return salt.hex(), password_hash.hex()


def verify_password(password, stored_salt, stored_hash):
    """Verify password using constant-time comparison."""
    try:
        salt = bytes.fromhex(stored_salt)
        expected_hash = bytes.fromhex(stored_hash)
    except (TypeError, ValueError):
        return False

    supplied_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return hmac.compare_digest(supplied_hash, expected_hash)


def initialize_user_database():
    """Create tables and default accounts only when they do not exist."""
    with get_db_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                display_name TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('Admin', 'Lecturer', 'Judge')),
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                last_login TEXT
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS login_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                success INTEGER NOT NULL,
                event_time TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS monitoring_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL UNIQUE,
                mode TEXT NOT NULL,
                mq2 INTEGER NOT NULL,
                mq135 INTEGER NOT NULL,
                temperature REAL NOT NULL,
                pwm INTEGER NOT NULL,
                fan_speed INTEGER NOT NULL,
                voltage REAL NOT NULL,
                current REAL NOT NULL,
                power REAL NOT NULL,
                motor_status TEXT,
                buzzer_status TEXT,
                led_status TEXT,
                alarm_value INTEGER NOT NULL,
                ai_risk REAL NOT NULL,
                system_health REAL NOT NULL,
                system_status TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_monitoring_timestamp
            ON monitoring_records(timestamp)
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS password_reset_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                request_time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending'
                    CHECK(status IN ('Pending', 'Completed', 'Rejected')),
                completed_time TEXT,
                admin_note TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )

        default_users = [
            ("admin", "System Administrator", "admin123", "Admin"),
            ("lecturer", "Lecturer", "lecturer123", "Lecturer"),
            ("judge", "Competition Judge", "judge123", "Judge"),
        ]

        for username, display_name, password, role in default_users:
            exists = connection.execute(
                "SELECT 1 FROM users WHERE username = ?",
                (username,),
            ).fetchone()

            if exists is None:
                salt, password_hash = hash_password(password)
                connection.execute(
                    """
                    INSERT INTO users (
                        username, display_name, password_salt,
                        password_hash, role, active, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, 1, ?)
                    """,
                    (
                        username,
                        display_name,
                        salt,
                        password_hash,
                        role,
                        datetime.now().isoformat(timespec="seconds"),
                    ),
                )


def authenticate_user(username, password):
    """Return a user dictionary when credentials are valid."""
    clean_username = username.strip()

    with get_db_connection() as connection:
        row = connection.execute(
            """
            SELECT id, username, display_name, password_salt,
                   password_hash, role, active
            FROM users
            WHERE username = ?
            """,
            (clean_username,),
        ).fetchone()

        success = bool(
            row
            and int(row["active"]) == 1
            and verify_password(
                password,
                row["password_salt"],
                row["password_hash"],
            )
        )

        connection.execute(
            """
            INSERT INTO login_audit (username, success, event_time)
            VALUES (?, ?, ?)
            """,
            (
                clean_username,
                int(success),
                datetime.now().isoformat(timespec="seconds"),
            ),
        )

        if not success:
            return None

        connection.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.now().isoformat(timespec="seconds"), row["id"]),
        )

        return {
            "id": int(row["id"]),
            "username": str(row["username"]),
            "display_name": str(row["display_name"]),
            "role": str(row["role"]),
        }


def list_users():
    with get_db_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, username, display_name, role, active,
                   created_at, COALESCE(last_login, 'Never') AS last_login
            FROM users
            ORDER BY
                CASE role
                    WHEN 'Admin' THEN 1
                    WHEN 'Lecturer' THEN 2
                    ELSE 3
                END,
                username
            """
        ).fetchall()
    return [dict(row) for row in rows]


def create_user(username, display_name, password, role):
    clean_username = username.strip()
    clean_name = display_name.strip()

    if not clean_username or not clean_name:
        return False, "Username dan display name mesti diisi."

    if len(clean_username) < 3:
        return False, "Username mesti sekurang-kurangnya 3 aksara."

    if not re.fullmatch(r"[A-Za-z0-9_.-]+", clean_username):
        return False, "Username hanya boleh mengandungi huruf, nombor, _, - dan titik."

    if len(password) < 8:
        return False, "Password mesti sekurang-kurangnya 8 aksara."

    if role not in VALID_ROLES:
        return False, "Role tidak sah."

    salt, password_hash = hash_password(password)

    try:
        with get_db_connection() as connection:
            connection.execute(
                """
                INSERT INTO users (
                    username, display_name, password_salt,
                    password_hash, role, active, created_at
                )
                VALUES (?, ?, ?, ?, ?, 1, ?)
                """,
                (
                    clean_username,
                    clean_name,
                    salt,
                    password_hash,
                    role,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
        return True, f"Akaun {clean_username} berjaya dicipta."
    except sqlite3.IntegrityError:
        return False, "Username tersebut sudah digunakan."


def update_user_account(user_id, role, active):
    """Update role/status while protecting the final active administrator."""
    with get_db_connection() as connection:
        current = connection.execute(
            "SELECT role, active FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

        if current is None:
            return False, "Akaun tidak ditemui."

        removes_active_admin = (
            current["role"] == "Admin"
            and int(current["active"]) == 1
            and (role != "Admin" or not active)
        )

        if removes_active_admin:
            active_admins = connection.execute(
                """
                SELECT COUNT(*) AS total
                FROM users
                WHERE role = 'Admin' AND active = 1
                """
            ).fetchone()["total"]

            if int(active_admins) <= 1:
                return False, "Sekurang-kurangnya satu Admin aktif mesti dikekalkan."

        connection.execute(
            "UPDATE users SET role = ?, active = ? WHERE id = ?",
            (role, int(active), user_id),
        )

    return True, "Maklumat akaun berjaya dikemas kini."


def reset_user_password(user_id, new_password):
    if len(new_password) < 8:
        return False, "Password baharu mesti sekurang-kurangnya 8 aksara."

    salt, password_hash = hash_password(new_password)

    with get_db_connection() as connection:
        connection.execute(
            """
            UPDATE users
            SET password_salt = ?, password_hash = ?
            WHERE id = ?
            """,
            (salt, password_hash, user_id),
        )

    return True, "Password berjaya ditukar."


def change_own_password(user_id, current_password, new_password, confirm_password):
    """Allow an authenticated user to securely change their own password."""
    if not current_password:
        return False, "Masukkan password semasa."

    if len(new_password) < 8:
        return False, "Password baharu mesti sekurang-kurangnya 8 aksara."

    if new_password != confirm_password:
        return False, "Password baharu dan pengesahan tidak sama."

    with get_db_connection() as connection:
        row = connection.execute(
            """
            SELECT password_salt, password_hash
            FROM users
            WHERE id = ? AND active = 1
            """,
            (user_id,),
        ).fetchone()

    if row is None:
        return False, "Akaun tidak ditemui atau tidak aktif."

    if not verify_password(
        current_password,
        row["password_salt"],
        row["password_hash"],
    ):
        return False, "Password semasa tidak betul."

    return reset_user_password(user_id, new_password)


def create_password_reset_request(username):
    """Create one pending password reset request for an existing active user."""
    clean_username = username.strip()

    if not clean_username:
        return False, "Masukkan username anda."

    with get_db_connection() as connection:
        user = connection.execute(
            """
            SELECT id, username, active
            FROM users
            WHERE username = ?
            """,
            (clean_username,),
        ).fetchone()

        # Neutral message avoids exposing whether an account exists.
        if user is None or int(user["active"]) != 1:
            return True, (
                "Jika akaun tersebut wujud dan aktif, permintaan reset "
                "akan dihantar kepada Admin."
            )

        pending = connection.execute(
            """
            SELECT id
            FROM password_reset_requests
            WHERE user_id = ? AND status = 'Pending'
            """,
            (user["id"],),
        ).fetchone()

        if pending is None:
            connection.execute(
                """
                INSERT INTO password_reset_requests (
                    user_id, username, request_time, status
                )
                VALUES (?, ?, ?, 'Pending')
                """,
                (
                    user["id"],
                    user["username"],
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )

    return True, (
        "Permintaan reset password telah dihantar kepada Admin. "
        "Admin akan menetapkan password sementara untuk anda."
    )


def list_password_reset_requests():
    with get_db_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, user_id, username, request_time,
                   status, COALESCE(completed_time, '-') AS completed_time,
                   COALESCE(admin_note, '') AS admin_note
            FROM password_reset_requests
            ORDER BY
                CASE status WHEN 'Pending' THEN 1 ELSE 2 END,
                request_time DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def complete_password_reset_request(request_id, new_password, admin_note=""):
    if len(new_password) < 8:
        return False, "Password sementara mesti sekurang-kurangnya 8 aksara."

    with get_db_connection() as connection:
        request_row = connection.execute(
            """
            SELECT user_id, status
            FROM password_reset_requests
            WHERE id = ?
            """,
            (request_id,),
        ).fetchone()

        if request_row is None:
            return False, "Permintaan tidak ditemui."

        if request_row["status"] != "Pending":
            return False, "Permintaan ini sudah diproses."

    success, message = reset_user_password(
        request_row["user_id"],
        new_password,
    )

    if not success:
        return False, message

    with get_db_connection() as connection:
        connection.execute(
            """
            UPDATE password_reset_requests
            SET status = 'Completed',
                completed_time = ?,
                admin_note = ?
            WHERE id = ?
            """,
            (
                datetime.now().isoformat(timespec="seconds"),
                admin_note.strip(),
                request_id,
            ),
        )

    return True, "Password sementara berjaya ditetapkan."


def reject_password_reset_request(request_id, admin_note=""):
    with get_db_connection() as connection:
        connection.execute(
            """
            UPDATE password_reset_requests
            SET status = 'Rejected',
                completed_time = ?,
                admin_note = ?
            WHERE id = ? AND status = 'Pending'
            """,
            (
                datetime.now().isoformat(timespec="seconds"),
                admin_note.strip(),
                request_id,
            ),
        )

    return True, "Permintaan reset telah ditolak."


def save_monitoring_record(record):
    """Persist one sensor record per second to SQLite."""
    timestamp_value = record.get("Timestamp")

    if isinstance(timestamp_value, pd.Timestamp):
        timestamp_value = timestamp_value.to_pydatetime()

    if isinstance(timestamp_value, datetime):
        timestamp_text = timestamp_value.replace(microsecond=0).isoformat()
    else:
        timestamp_text = str(timestamp_value)

    with get_db_connection() as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO monitoring_records (
                timestamp, mode, mq2, mq135, temperature, pwm,
                fan_speed, voltage, current, power, motor_status,
                buzzer_status, led_status, alarm_value, ai_risk,
                system_health, system_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp_text,
                str(record.get("Mode", "")),
                int(record.get("MQ2", 0)),
                int(record.get("MQ135", 0)),
                float(record.get("Temperature", 0.0)),
                int(record.get("PWM", 0)),
                int(record.get("Fan Speed (%)", 0)),
                float(record.get("Voltage (V)", 0.0)),
                float(record.get("Current (A)", 0.0)),
                float(record.get("Power (W)", 0.0)),
                str(record.get("Motor Status", "")),
                str(record.get("Buzzer Status", "")),
                str(record.get("LED Status", "")),
                int(record.get("Alarm Value", 0)),
                float(record.get("AI Risk (%)", 0.0)),
                float(record.get("System Health (%)", 0.0)),
                str(record.get("System Status", "")),
            ),
        )


def load_historical_records(days):
    """Load persisted monitoring records for the selected reporting period."""
    start_time = datetime.now() - timedelta(days=int(days))

    with get_db_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                timestamp AS Timestamp,
                mode AS Mode,
                mq2 AS MQ2,
                mq135 AS MQ135,
                temperature AS Temperature,
                pwm AS PWM,
                fan_speed AS "Fan Speed (%)",
                voltage AS "Voltage (V)",
                current AS "Current (A)",
                power AS "Power (W)",
                motor_status AS "Motor Status",
                buzzer_status AS "Buzzer Status",
                led_status AS "LED Status",
                alarm_value AS "Alarm Value",
                ai_risk AS "AI Risk (%)",
                system_health AS "System Health (%)",
                system_status AS "System Status"
            FROM monitoring_records
            WHERE timestamp >= ?
            ORDER BY timestamp ASC
            """,
            (start_time.replace(microsecond=0).isoformat(),),
        ).fetchall()

    if not rows:
        return pd.DataFrame()

    historical_df = pd.DataFrame([dict(row) for row in rows])
    historical_df["Timestamp"] = pd.to_datetime(
        historical_df["Timestamp"],
        errors="coerce",
    )
    historical_df = historical_df.dropna(subset=["Timestamp"])
    historical_df["Time"] = historical_df["Timestamp"].dt.strftime("%H:%M:%S")
    return historical_df


def aggregate_for_report(records_df, days, max_points=450):
    """Downsample long histories while preserving the overall trend."""
    if records_df.empty or len(records_df) <= max_points:
        return records_df.copy()

    working = records_df.copy().set_index("Timestamp").sort_index()
    interval_minutes = max(1, int((days * 24 * 60) / max_points))

    numeric_columns = [
        "MQ2", "MQ135", "Temperature", "PWM", "Fan Speed (%)",
        "Voltage (V)", "Current (A)", "Power (W)", "Alarm Value",
        "AI Risk (%)", "System Health (%)",
    ]
    existing_numeric = [column for column in numeric_columns if column in working.columns]

    aggregated_numeric = working[existing_numeric].resample(
        f"{interval_minutes}min"
    ).mean()

    text_columns = [
        "Mode", "Motor Status", "Buzzer Status",
        "LED Status", "System Status",
    ]
    existing_text = [column for column in text_columns if column in working.columns]
    aggregated_text = working[existing_text].resample(
        f"{interval_minutes}min"
    ).last()

    combined = pd.concat([aggregated_numeric, aggregated_text], axis=1)
    combined = combined.dropna(how="all").reset_index()
    combined["Time"] = combined["Timestamp"].dt.strftime("%H:%M:%S")
    return combined


def calculate_period_summary(records_df, days):
    """Create a period-level analytics summary from historical records."""
    if records_df.empty:
        return {
            "sample_count": 0,
            "alarm_count": 0,
            "alarm_percent": 0.0,
            "avg_mq2": 0.0,
            "max_mq2": 0.0,
            "avg_mq135": 0.0,
            "max_mq135": 0.0,
            "avg_temp": 0.0,
            "max_temp": 0.0,
            "avg_fan": 0.0,
            "max_fan": 0.0,
            "avg_current": 0.0,
            "max_current": 0.0,
            "avg_power": 0.0,
            "max_power": 0.0,
            "estimated_energy_kwh": 0.0,
            "dominant_status": "NO DATA",
            "risk_trend": "insufficient data",
        }

    df_period = records_df.sort_values("Timestamp").copy()
    sample_count = len(df_period)
    alarm_count = int((df_period["Alarm Value"].fillna(0) >= 0.5).sum())
    alarm_percent = (alarm_count / sample_count * 100) if sample_count else 0.0

    if sample_count >= 4:
        split = max(1, sample_count // 3)
        early_risk = df_period["AI Risk (%)"].head(split).mean()
        late_risk = df_period["AI Risk (%)"].tail(split).mean()
        risk_change = late_risk - early_risk

        if risk_change > 5:
            risk_trend = "increasing"
        elif risk_change < -5:
            risk_trend = "decreasing"
        else:
            risk_trend = "stable"
    else:
        risk_trend = "insufficient data"

    if sample_count >= 2:
        elapsed_seconds = (
            df_period["Timestamp"].iloc[-1] - df_period["Timestamp"].iloc[0]
        ).total_seconds()
        mean_interval_h = max(
            elapsed_seconds / max(sample_count - 1, 1) / 3600,
            0,
        )
        estimated_energy_kwh = (
            df_period["Power (W)"].fillna(0).sum() * mean_interval_h / 1000
        )
    else:
        estimated_energy_kwh = 0.0

    status_series = df_period["System Status"].dropna().astype(str)
    dominant_status = (
        status_series.mode().iloc[0] if not status_series.empty else "UNKNOWN"
    )

    return {
        "sample_count": sample_count,
        "alarm_count": alarm_count,
        "alarm_percent": alarm_percent,
        "avg_mq2": float(df_period["MQ2"].mean()),
        "max_mq2": float(df_period["MQ2"].max()),
        "avg_mq135": float(df_period["MQ135"].mean()),
        "max_mq135": float(df_period["MQ135"].max()),
        "avg_temp": float(df_period["Temperature"].mean()),
        "max_temp": float(df_period["Temperature"].max()),
        "avg_fan": float(df_period["Fan Speed (%)"].mean()),
        "max_fan": float(df_period["Fan Speed (%)"].max()),
        "avg_current": float(df_period["Current (A)"].mean()),
        "max_current": float(df_period["Current (A)"].max()),
        "avg_power": float(df_period["Power (W)"].mean()),
        "max_power": float(df_period["Power (W)"].max()),
        "estimated_energy_kwh": float(estimated_energy_kwh),
        "dominant_status": dominant_status,
        "risk_trend": risk_trend,
    }


def build_period_ai_summary(records_df, days):
    """Generate an explainable AI-style summary for the selected period."""
    summary = calculate_period_summary(records_df, days)

    if summary["sample_count"] == 0:
        return (
            f"No historical monitoring data is available for the selected "
            f"{days}-day period. Keep the dashboard running so readings can "
            f"be stored in the SQLite monitoring database."
        )

    observations = []

    if summary["max_mq2"] > MQ2_WARNING:
        observations.append(
            f"LPG reached a dangerous peak of {summary['max_mq2']:.0f}"
        )
    elif summary["max_mq2"] >= MQ2_SAFE:
        observations.append(
            f"LPG entered the warning range, peaking at {summary['max_mq2']:.0f}"
        )
    else:
        observations.append(
            f"LPG remained within the safe range, with a peak of "
            f"{summary['max_mq2']:.0f}"
        )

    if summary["max_mq135"] > MQ135_WARNING:
        observations.append(
            f"air quality reached a poor level of {summary['max_mq135']:.0f}"
        )
    elif summary["max_mq135"] >= MQ135_GOOD:
        observations.append(
            f"air quality was occasionally moderate, peaking at "
            f"{summary['max_mq135']:.0f}"
        )
    else:
        observations.append("air quality remained generally good")

    if summary["max_temp"] >= TEMP_HOT:
        observations.append(
            f"temperature reached a very hot peak of {summary['max_temp']:.1f} C"
        )
    elif summary["max_temp"] >= TEMP_NORMAL:
        observations.append(
            f"temperature became hot, with a peak of {summary['max_temp']:.1f} C"
        )
    else:
        observations.append("temperature remained within the normal range")

    if summary["alarm_count"] == 0:
        alarm_statement = "No alarm-active samples were recorded."
    else:
        alarm_statement = (
            f"The alarm was active in {summary['alarm_count']} samples "
            f"({summary['alarm_percent']:.1f}% of recorded samples)."
        )

    if summary["risk_trend"] == "increasing":
        trend_statement = (
            "The AI risk trend increased toward the end of the reporting period, "
            "so inspection of gas connections, ventilation and sensor calibration "
            "is recommended."
        )
    elif summary["risk_trend"] == "decreasing":
        trend_statement = (
            "The AI risk trend decreased toward the end of the reporting period, "
            "indicating that ventilation or operating conditions improved."
        )
    elif summary["risk_trend"] == "stable":
        trend_statement = (
            "The AI risk trend remained broadly stable across the reporting period."
        )
    else:
        trend_statement = (
            "There are not yet enough records to determine a reliable risk trend."
        )

    return (
        f"AI period analysis for the last {days} days used "
        f"{summary['sample_count']} stored readings. "
        + "; ".join(observations)
        + ". "
        + alarm_statement
        + f" Average fan speed was {summary['avg_fan']:.1f}% and average power "
          f"consumption was {summary['avg_power']:.2f} W. Estimated recorded "
          f"energy consumption was {summary['estimated_energy_kwh']:.4f} kWh. "
        + trend_statement
    )


def create_report_chart(records_df, chart_type, title):
    """Return a PNG chart in memory for use inside the PDF report."""
    if not MATPLOTLIB_AVAILABLE or records_df.empty:
        return None

    chart_df = records_df.sort_values("Timestamp").copy()
    fig, axis = plt.subplots(figsize=(9.2, 3.2))

    if chart_type == "sensors":
        axis.plot(chart_df["Timestamp"], chart_df["MQ2"], label="MQ2 LPG")
        axis.plot(chart_df["Timestamp"], chart_df["MQ135"], label="MQ135 Air Quality")
        axis.plot(
            chart_df["Timestamp"],
            chart_df["Temperature"],
            label="Temperature (C)",
        )
        axis.set_ylabel("Sensor value")

    elif chart_type == "electrical":
        axis.plot(
            chart_df["Timestamp"],
            chart_df["Current (A)"],
            label="Current (A)",
        )
        axis.plot(
            chart_df["Timestamp"],
            chart_df["Power (W)"],
            label="Power (W)",
        )
        axis.set_ylabel("Current / Power")

    elif chart_type == "fan":
        axis.plot(
            chart_df["Timestamp"],
            chart_df["Fan Speed (%)"],
            label="Fan Speed (%)",
        )
        axis.set_ylim(0, 105)
        axis.set_ylabel("Fan speed (%)")

    elif chart_type == "alarm":
        alarm_values = chart_df["Alarm Value"].fillna(0).astype(float)
        axis.step(
            chart_df["Timestamp"],
            alarm_values,
            where="post",
            label="Alarm status",
        )
        axis.set_ylim(-0.1, 1.1)
        axis.set_yticks([0, 1])
        axis.set_yticklabels(["OFF", "ON"])
        axis.set_ylabel("Alarm")

    axis.set_title(title)
    axis.set_xlabel("Date and time")
    axis.grid(True, alpha=0.25)
    axis.legend(loc="upper left", fontsize=8, ncol=3)
    fig.autofmt_xdate()
    fig.tight_layout()

    image_buffer = BytesIO()
    fig.savefig(image_buffer, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    image_buffer.seek(0)
    return image_buffer



def delete_user_account(user_id, current_user_id):
    if int(user_id) == int(current_user_id):
        return False, "Anda tidak boleh memadam akaun yang sedang digunakan."

    with get_db_connection() as connection:
        row = connection.execute(
            "SELECT role, active FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

        if row is None:
            return False, "Akaun tidak ditemui."

        if row["role"] == "Admin" and int(row["active"]) == 1:
            active_admins = connection.execute(
                """
                SELECT COUNT(*) AS total
                FROM users
                WHERE role = 'Admin' AND active = 1
                """
            ).fetchone()["total"]

            if int(active_admins) <= 1:
                return False, "Admin aktif terakhir tidak boleh dipadam."

        connection.execute("DELETE FROM users WHERE id = ?", (user_id,))

    return True, "Akaun berjaya dipadam."


initialize_user_database()

session_defaults = {
    "authenticated": False,
    "login_user_id": None,
    "login_username": "",
    "login_display_name": "",
    "login_role": "",
    "failed_login_attempts": 0,
    "lockout_until": 0.0,
}

for key, value in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def logout():
    """End the authenticated session without deleting dashboard records."""
    st.session_state.authenticated = False
    st.session_state.login_user_id = None
    st.session_state.login_username = ""
    st.session_state.login_display_name = ""
    st.session_state.login_role = ""
    st.session_state.failed_login_attempts = 0
    st.session_state.lockout_until = 0.0
    st.rerun()


def render_login():
    """Display a clean database-backed login page with reset request support."""
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {display:none;}

        .login-wrap {
            max-width: 520px;
            margin: 6vh auto 0 auto;
        }

        .login-card {
            width: 100%;
            box-sizing: border-box;
            padding: clamp(22px, 4vw, 34px);
            background: linear-gradient(145deg, rgba(16,29,45,.99), rgba(8,18,30,.99));
            border: 1px solid #2A4966;
            border-radius: 20px;
            box-shadow: 0 18px 55px rgba(0,0,0,.35);
            text-align: center;
        }

        .login-icon {
            font-size: 52px;
            margin-bottom: 8px;
        }

        .login-heading {
            color: #F5FAFF;
            font-size: clamp(24px, 5vw, 30px);
            font-weight: 900;
            line-height: 1.2;
        }

        .login-caption {
            color: #8EA2B7;
            font-size: 13px;
            margin-top: 8px;
            line-height: 1.5;
        }

        .login-security {
            margin-top: 16px;
            padding: 10px 12px;
            border-radius: 10px;
            background: rgba(32,197,255,.06);
            border: 1px solid rgba(32,197,255,.20);
            color: #9DB4C8;
            font-size: 12px;
            line-height: 1.5;
        }

        div[data-testid="stExpander"] {
            width: 100% !important;
            max-width: 520px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            box-sizing: border-box !important;
        }

        div[data-testid="stExpander"] * {
            word-break: normal !important;
            overflow-wrap: normal !important;
            white-space: normal !important;
        }

        @media screen and (max-width: 620px) {
            .login-wrap {
                margin-top: 2vh;
            }
        }
        </style>

        <div class="login-wrap">
            <div class="login-card">
                <div class="login-icon">🍳</div>
                <div class="login-heading">Smart Kitchen Hood</div>
                <div class="login-caption">
                    AI Safety, Ventilation and Energy Monitoring System
                </div>
                <div class="login-security">
                    Secure database login with role-based access control
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    now = time.time()
    remaining = max(0, int(st.session_state.lockout_until - now))

    if remaining > 0:
        st.error(
            f"Terlalu banyak percubaan gagal. Cuba semula selepas {remaining} saat."
        )
        st.stop()

    with st.form("database_login_form", clear_on_submit=False):
        username = st.text_input(
            "Username",
            placeholder="Masukkan username",
            autocomplete="username",
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Masukkan password",
            autocomplete="current-password",
        )
        submitted = st.form_submit_button(
            "Login",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        user = authenticate_user(username, password)

        if user:
            st.session_state.authenticated = True
            st.session_state.login_user_id = user["id"]
            st.session_state.login_username = user["username"]
            st.session_state.login_display_name = user["display_name"]
            st.session_state.login_role = user["role"]
            st.session_state.failed_login_attempts = 0
            st.session_state.lockout_until = 0.0
            st.rerun()

        st.session_state.failed_login_attempts += 1
        attempts_left = MAX_LOGIN_ATTEMPTS - st.session_state.failed_login_attempts

        if st.session_state.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
            st.session_state.lockout_until = time.time() + LOCKOUT_SECONDS
            st.session_state.failed_login_attempts = 0
            st.error(
                "Akses dikunci selama 30 saat kerana terlalu banyak percubaan gagal."
            )
        else:
            st.error(
                "Username, password atau status akaun tidak sah. "
                f"Baki percubaan: {attempts_left}."
            )

    with st.expander("Forgot Password?"):
        st.caption(
            "Masukkan username. Permintaan akan muncul dalam panel Admin "
            "tanpa memaparkan password anda."
        )

        with st.form("forgot_password_form", clear_on_submit=True):
            reset_username = st.text_input(
                "Username for reset request",
                placeholder="Masukkan username",
            )
            reset_submitted = st.form_submit_button(
                "Send Reset Request",
                use_container_width=True,
            )

        if reset_submitted:
            success, message = create_password_reset_request(reset_username)
            if success:
                st.success(message)
            else:
                st.error(message)


if not st.session_state.authenticated:
    render_login()
    st.stop()


def user_can_control():
    return st.session_state.login_role == "Admin"


def user_can_download():
    return st.session_state.login_role in VALID_ROLES


# ========================= CONSTANTS =========================

MAX_RECORDS = 45
GRAPH_POINTS = 30

MQ2_SAFE = 300
MQ2_WARNING = 600

MQ135_GOOD = 300
MQ135_WARNING = 600

TEMP_NORMAL = 28.0
TEMP_HOT = 36.0

PWM_LOW = 85
PWM_MEDIUM = 170
PWM_HIGH = 255

COLORS = {
    "green": "#43D668",
    "yellow": "#FFC928",
    "red": "#FF4D57",
    "blue": "#20C5FF",
    "gray": "#8FA4B8",
    "purple": "#8A5CFF",
}

# ========================= SESSION STATE =========================

if "records" not in st.session_state:
    st.session_state.records = pd.DataFrame()

if "event_log" not in st.session_state:
    st.session_state.event_log = []

if "last_event_signature" not in st.session_state:
    st.session_state.last_event_signature = ""

if "total_energy_kwh" not in st.session_state:
    st.session_state.total_energy_kwh = 0.0

if "last_energy_time" not in st.session_state:
    st.session_state.last_energy_time = time.time()

if "sim_mq2" not in st.session_state:
    st.session_state.sim_mq2 = 220

if "sim_mq135" not in st.session_state:
    st.session_state.sim_mq135 = 330

if "sim_temp" not in st.session_state:
    st.session_state.sim_temp = 29.5

if "sensor_health" not in st.session_state:
    st.session_state.sensor_health = 100.0

if "motor_health" not in st.session_state:
    st.session_state.motor_health = 98.0

if "fan_health" not in st.session_state:
    st.session_state.fan_health = 95.0


if "generated_historical_pdf" not in st.session_state:
    st.session_state.generated_historical_pdf = None

if "generated_historical_pdf_days" not in st.session_state:
    st.session_state.generated_historical_pdf_days = None


# ========================= STATUS FUNCTIONS =========================

def mq2_status(value):
    if value < MQ2_SAFE:
        return "SAFE", "green"
    if value <= MQ2_WARNING:
        return "WARNING", "yellow"
    return "DANGEROUS", "red"


def mq135_status(value):
    if value < MQ135_GOOD:
        return "GOOD", "green"
    if value <= MQ135_WARNING:
        return "MODERATE", "yellow"
    return "BAD", "red"


def temp_status(value):
    if value < TEMP_NORMAL:
        return "NORMAL", "green"
    if value < TEMP_HOT:
        return "HOT", "yellow"
    return "VERY HOT", "red"


def control_logic(mq2, mq135, temp):
    mq2_state, _ = mq2_status(mq2)
    air_state, _ = mq135_status(mq135)
    temp_state, _ = temp_status(temp)

    severity = 0
    severity += {"SAFE": 0, "WARNING": 2, "DANGEROUS": 3}[mq2_state]
    severity += {"GOOD": 0, "MODERATE": 1, "BAD": 3}[air_state]
    severity += {"NORMAL": 0, "HOT": 1, "VERY HOT": 3}[temp_state]

    critical_count = sum([
        mq2_state == "DANGEROUS",
        air_state == "BAD",
        temp_state == "VERY HOT",
    ])

    warning_count = sum([
        mq2_state == "WARNING",
        air_state == "MODERATE",
        temp_state == "HOT",
    ])

    if critical_count >= 1 or severity >= 5:
        pwm = PWM_HIGH
    elif warning_count >= 2 or severity >= 2:
        pwm = PWM_MEDIUM
    elif warning_count == 1:
        pwm = PWM_LOW
    else:
        pwm = 0

    fan_speed = round((pwm / 255) * 100)

    alarm_required = (
        mq2_state in ["WARNING", "DANGEROUS"]
        or air_state == "BAD"
        or temp_state == "VERY HOT"
    )

    if critical_count >= 2:
        system_status = "MULTIPLE HAZARD WARNING"
        status_color = "red"
    elif mq2_state == "DANGEROUS":
        system_status = "LPG GAS DANGER"
        status_color = "red"
    elif air_state == "BAD":
        system_status = "AIR QUALITY WARNING"
        status_color = "red"
    elif temp_state == "VERY HOT":
        system_status = "HIGH TEMPERATURE"
        status_color = "red"
    elif severity > 0:
        system_status = "CAUTION"
        status_color = "yellow"
    else:
        system_status = "SYSTEM SAFE"
        status_color = "green"

    if fan_speed == 100:
        motor_status = "MAXIMUM SPEED"
    elif fan_speed >= 60:
        motor_status = "MEDIUM SPEED"
    elif fan_speed > 0:
        motor_status = "LOW SPEED"
    else:
        motor_status = "OFF"

    return {
        "mq2_state": mq2_state,
        "air_state": air_state,
        "temp_state": temp_state,
        "pwm": pwm,
        "fan_speed": fan_speed,
        "alarm_required": alarm_required,
        "system_status": system_status,
        "system_color": status_color,
        "motor_status": motor_status,
    }


def energy_calculation(fan_speed):
    voltage = 12.0
    if fan_speed == 0:
        current = 0.02
    else:
        current = 0.18 + (fan_speed / 100) * 0.82
    power = voltage * current
    return round(voltage, 2), round(current, 2), round(power, 2)


def update_energy(power_w):
    now = time.time()
    elapsed_h = max(0, now - st.session_state.last_energy_time) / 3600
    st.session_state.total_energy_kwh += (power_w / 1000) * elapsed_h
    st.session_state.last_energy_time = now


def add_event(control, led_status, buzzer_status):
    signature = "|".join(map(str, [
        control["system_status"],
        control["fan_speed"],
        led_status,
        buzzer_status,
    ]))

    if signature != st.session_state.last_event_signature:
        st.session_state.event_log.insert(0, {
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Event": control["system_status"],
            "Level": control["system_color"].upper(),
            "Fan": f'{control["fan_speed"]}%',
            "LED": led_status,
            "Buzzer": buzzer_status,
        })
        st.session_state.event_log = st.session_state.event_log[:25]
        st.session_state.last_event_signature = signature



def calculate_ai_risk(mq2, mq135, temp):
    gas = np.clip((mq2 - 150) / 700, 0, 1)
    air = np.clip((mq135 - 150) / 700, 0, 1)
    heat = np.clip((temp - 24) / 21, 0, 1)
    score = (0.45 * gas + 0.30 * air + 0.25 * heat) * 100
    return round(float(np.clip(score, 0, 100)), 1)


def risk_status(score):
    if score < 25:
        return "LOW RISK", "green"
    if score < 50:
        return "MODERATE RISK", "yellow"
    if score < 75:
        return "HIGH RISK", "yellow"
    return "VERY HIGH RISK", "red"


def predict_next_30_seconds(df, current_mq2, current_mq135, current_temp):
    if len(df) < 4:
        return int(current_mq2), int(current_mq135), float(current_temp)

    sample = df.tail(8)
    x = np.arange(len(sample))
    future_x = len(sample) + 2
    predictions = []

    for column in ["MQ2", "MQ135", "Temperature"]:
        y = sample[column].astype(float).to_numpy()
        slope, intercept = np.polyfit(x, y, 1)
        predictions.append(intercept + slope * future_x)

    return (
        int(np.clip(predictions[0], 0, 1023)),
        int(np.clip(predictions[1], 0, 1023)),
        round(float(np.clip(predictions[2], 0, 60)), 1),
    )


def ai_recommendation(control, mq2, mq135, temp):
    if mq2 > 600:
        return (
            "Check LPG leakage immediately",
            "Turn off the gas source and ventilate the kitchen.",
            "red",
        )
    if mq135 > 600:
        return (
            "Increase ventilation",
            "Poor air quality detected. Keep the fan at high speed.",
            "red",
        )
    if temp >= 36:
        return (
            "Reduce kitchen heat",
            "Very high temperature detected near the cooking area.",
            "red",
        )
    if control["system_color"] == "yellow":
        return (
            "Continue monitoring",
            "A moderate condition is present and ventilation has increased.",
            "yellow",
        )

    return (
        "System operating normally",
        "All monitored parameters are within the safe range.",
        "green",
    )


def health_status(score):
    if score >= 95:
        return "EXCELLENT", "green"
    if score >= 85:
        return "GOOD", "green"
    if score >= 70:
        return "WARNING", "yellow"
    return "CRITICAL", "red"


def make_line_chart(df, columns, title, y_title):
    """
    Lightweight real-time chart with fixed, meaningful Y-axis ranges.
    """
    chart_df = df.tail(GRAPH_POINTS).copy()

    x_values = (
        chart_df["Timestamp"]
        if "Timestamp" in chart_df.columns
        else chart_df["Time"]
    )

    fig = go.Figure()

    for col in columns:
        fig.add_trace(go.Scatter(
            x=x_values,
            y=chart_df[col],
            mode="lines",
            name=col,
            line=dict(width=2),
            hovertemplate="%{y}<extra>" + col + "</extra>",
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=13)),
        template="plotly_dark",
        height=315,
        margin=dict(l=15, r=12, t=48, b=48),
        xaxis_title="Time",
        yaxis_title=y_title,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0A1522",
        legend=dict(
            orientation="h",
            y=1.14,
            x=0,
            font=dict(size=10),
        ),
        hovermode="x unified",
        showlegend=True,
        uirevision="live-chart",
    )

    fig.update_xaxes(
        tickformat="%H:%M:%S",
        nticks=7,
        tickangle=0,
        tickfont=dict(size=9),
        automargin=True,
        showgrid=True,
        gridcolor="rgba(120,150,180,.12)",
        fixedrange=True,
    )

    if columns == ["Fan Speed (%)"]:
        fig.update_yaxes(
            range=[0, 100],
            tickmode="array",
            tickvals=[0, 20, 40, 60, 80, 100],
            ticksuffix="%",
            automargin=True,
            gridcolor="rgba(120,150,180,.14)",
            fixedrange=True,
        )

    elif columns == ["Alarm Value"]:
        fig.update_yaxes(
            range=[0, 1],
            tickmode="array",
            tickvals=[0, 1],
            ticktext=["OFF", "ON"],
            automargin=True,
            gridcolor="rgba(120,150,180,.14)",
            fixedrange=True,
        )

    elif columns == ["Current (A)", "Power (W)"]:
        fig.update_yaxes(
            range=[0, 15],
            tickmode="array",
            tickvals=[0, 3, 6, 9, 12, 15],
            automargin=True,
            gridcolor="rgba(120,150,180,.14)",
            fixedrange=True,
        )

    else:
        fig.update_yaxes(
            rangemode="tozero",
            automargin=True,
            gridcolor="rgba(120,150,180,.14)",
            fixedrange=True,
        )

    return fig


def make_gauge(value, title, suffix, max_value, threshold_1, threshold_2):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title},
        number={"suffix": suffix},
        gauge={
            "axis": {"range": [0, max_value]},
            "bar": {"color": "#20C5FF"},
            "bgcolor": "#0D1117",
            "borderwidth": 1,
            "bordercolor": "#30363D",
            "steps": [
                {"range": [0, threshold_1], "color": "rgba(67,214,104,.22)"},
                {"range": [threshold_1, threshold_2], "color": "rgba(255,201,40,.22)"},
                {"range": [threshold_2, max_value], "color": "rgba(255,77,87,.22)"},
            ],
        },
    ))

    fig.update_layout(
        template="plotly_dark",
        height=255,
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=15, r=15, t=45, b=10),
    )
    return fig


def ai_analysis(control, mq2, mq135, temp, power):
    findings = []

    if control["mq2_state"] == "DANGEROUS":
        findings.append("High LPG gas concentration detected.")
    elif control["mq2_state"] == "WARNING":
        findings.append("LPG gas level is above the safe range.")

    if control["air_state"] == "BAD":
        findings.append("Indoor air quality is poor.")
    elif control["air_state"] == "MODERATE":
        findings.append("Indoor air quality is moderate.")

    if control["temp_state"] == "VERY HOT":
        findings.append("Kitchen temperature is very high.")
    elif control["temp_state"] == "HOT":
        findings.append("Kitchen temperature is above the normal range.")

    if not findings:
        findings.append("All monitored parameters are within safe operating limits.")

    action = (
        f'The controller sets the BLDC fan to {control["fan_speed"]}% '
        f'using PWM {control["pwm"]}. Estimated power consumption is {power:.2f} W.'
    )

    if control["alarm_required"]:
        action += " The warning LED and buzzer are activated."
    else:
        action += " The warning LED and buzzer remain off."

    return " ".join(findings) + " " + action


def download_link(data_bytes, filename, label):
    """
    HTML download link that avoids Streamlit MediaFileHandler.
    This prevents 'Missing file ...csv' warnings during 1-second reruns.
    """
    encoded = base64.b64encode(data_bytes).decode("utf-8")
    return f"""
    <a href="data:text/csv;base64,{encoded}"
       download="{filename}"
       style="
           display:block;
           width:100%;
           box-sizing:border-box;
           padding:10px 14px;
           margin:7px 0;
           border-radius:10px;
           border:1px solid #2D5876;
           background:#10243A;
           color:#EAF4FF;
           text-align:center;
           text-decoration:none;
           font-weight:800;
       ">
       {label}
    </a>
    """


def generic_download_link(data_bytes, mime_type, filename, label):
    """Create a stable base64 download link without Streamlit media files."""
    encoded = base64.b64encode(data_bytes).decode("utf-8")
    return f"""
    <a href="data:{mime_type};base64,{encoded}"
       download="{filename}"
       style="
           display:block;
           width:100%;
           box-sizing:border-box;
           padding:10px 14px;
           margin:7px 0;
           border-radius:10px;
           border:1px solid #2D5876;
           background:#10243A;
           color:#EAF4FF;
           text-align:center;
           text-decoration:none;
           font-weight:800;
       ">
       {label}
    </a>
    """


def build_pdf_report(
    records_df,
    report_days,
    control,
    mq2,
    mq135,
    temp,
    voltage,
    current,
    power,
    risk_score,
    risk_text,
    health_score,
    led_status,
    buzzer_status,
):
    """Generate a historical 7-day or 30-day PDF report with charts."""
    if not REPORTLAB_AVAILABLE:
        return None

    historical_df = records_df.copy()
    report_summary = calculate_period_summary(historical_df, report_days)
    period_ai_text = build_period_ai_summary(historical_df, report_days)
    chart_df = aggregate_for_report(historical_df, report_days)

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=13 * mm,
        leftMargin=13 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title=f"Smart Kitchen Hood {report_days}-Day AI Report",
        author="Smart Kitchen Hood AI Dashboard",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        leading=22,
        textColor=pdf_colors.HexColor("#12324A"),
        spaceAfter=4 * mm,
    )
    heading = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
        textColor=pdf_colors.HexColor("#147EAD"),
        spaceBefore=3 * mm,
        spaceAfter=2 * mm,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=9,
        leading=13,
        textColor=pdf_colors.HexColor("#263746"),
    )
    small = ParagraphStyle(
        "Small",
        parent=body,
        fontSize=7.5,
        leading=10,
    )

    period_start = datetime.now() - timedelta(days=report_days)
    story = [
        Paragraph(
            f"Smart Kitchen Hood AI - {report_days}-Day Monitoring Report",
            title_style,
        ),
        Paragraph(
            f"Reporting period: {period_start.strftime('%d %B %Y')} to "
            f"{datetime.now().strftime('%d %B %Y')}<br/>"
            f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M:%S')} | "
            f"User role: {st.session_state.login_role}",
            body,
        ),
        Spacer(1, 4 * mm),
    ]

    if historical_df.empty:
        story += [
            Paragraph("Historical Data Status", heading),
            Paragraph(
                f"No stored monitoring records were found for the last "
                f"{report_days} days. Keep the dashboard running so records "
                f"can be saved in the SQLite database.",
                body,
            ),
        ]
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    period_data = [
        ["Period Metric", "Average", "Maximum / Total"],
        ["MQ2 LPG", f"{report_summary['avg_mq2']:.1f}", f"{report_summary['max_mq2']:.0f}"],
        ["MQ135 Air Quality", f"{report_summary['avg_mq135']:.1f}", f"{report_summary['max_mq135']:.0f}"],
        ["Temperature", f"{report_summary['avg_temp']:.1f} C", f"{report_summary['max_temp']:.1f} C"],
        ["Fan Speed", f"{report_summary['avg_fan']:.1f}%", f"{report_summary['max_fan']:.0f}%"],
        ["Current", f"{report_summary['avg_current']:.2f} A", f"{report_summary['max_current']:.2f} A"],
        ["Power", f"{report_summary['avg_power']:.2f} W", f"{report_summary['max_power']:.2f} W"],
        ["Alarm", f"{report_summary['alarm_percent']:.1f}% active", f"{report_summary['alarm_count']} samples"],
        ["Stored Records", "-", str(report_summary["sample_count"])],
        ["Estimated Energy", "-", f"{report_summary['estimated_energy_kwh']:.4f} kWh"],
        ["Dominant Status", "-", report_summary["dominant_status"]],
        ["AI Risk Trend", "-", report_summary["risk_trend"].upper()],
    ]

    period_table = Table(period_data, colWidths=[62 * mm, 48 * mm, 62 * mm])
    period_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), pdf_colors.HexColor("#12324A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), pdf_colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.35, pdf_colors.HexColor("#A9BAC8")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            pdf_colors.white,
            pdf_colors.HexColor("#F2F6F9"),
        ]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))

    story += [
        Paragraph("1. Reporting Period Performance", heading),
        period_table,
        Paragraph("2. AI Summary for the Selected Period", heading),
        Paragraph(period_ai_text, body),
        Spacer(1, 2 * mm),
    ]

    current_data = [
        ["Current Parameter", "Value", "Status"],
        ["MQ2 LPG", str(mq2), control["mq2_state"]],
        ["MQ135 Air Quality", str(mq135), control["air_state"]],
        ["Temperature", f"{temp:.1f} C", control["temp_state"]],
        ["Fan Speed", f'{control["fan_speed"]}%', control["motor_status"]],
        ["Current / Power", f"{current:.2f} A / {power:.2f} W", "LIVE"],
        ["LED / Buzzer", f"{led_status} / {buzzer_status}", "Alarm Output"],
        ["AI Risk", f"{risk_score:.1f}%", risk_text],
        ["System Health", f"{health_score:.1f}%", "Overall"],
    ]
    current_table = Table(current_data, colWidths=[58 * mm, 53 * mm, 61 * mm])
    current_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), pdf_colors.HexColor("#147EAD")),
        ("TEXTCOLOR", (0, 0), (-1, 0), pdf_colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.35, pdf_colors.HexColor("#A9BAC8")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            pdf_colors.white,
            pdf_colors.HexColor("#F2F6F9"),
        ]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story += [Paragraph("3. Current System Snapshot", heading), current_table]

    if MATPLOTLIB_AVAILABLE:
        chart_specs = [
            ("sensors", "4. Sensor Value Trend"),
            ("electrical", "5. Current and Power Trend"),
            ("fan", "6. Fan Speed Trend"),
            ("alarm", "7. Alarm ON/OFF Timeline"),
        ]

        for chart_type, chart_title in chart_specs:
            chart_buffer = create_report_chart(chart_df, chart_type, chart_title)
            if chart_buffer:
                story += [
                    PageBreak(),
                    Paragraph(chart_title, heading),
                    Image(chart_buffer, width=180 * mm, height=63 * mm),
                    Paragraph(
                        f"The graph uses stored records from the selected "
                        f"{report_days}-day reporting period. Long datasets are "
                        f"downsampled for readability without changing the main trend.",
                        small,
                    ),
                ]
    else:
        story += [
            Paragraph("4. Historical Graphs", heading),
            Paragraph(
                "Matplotlib is not installed, so graphs could not be embedded. "
                "Install it using: pip install matplotlib",
                body,
            ),
        ]

    story += [
        PageBreak(),
        Paragraph("8. Daily Summary", heading),
    ]

    daily = historical_df.copy().set_index("Timestamp")
    daily_summary = daily.resample("1D").agg({
        "MQ2": ["mean", "max"],
        "MQ135": ["mean", "max"],
        "Temperature": ["mean", "max"],
        "Fan Speed (%)": "mean",
        "Power (W)": "mean",
        "Alarm Value": "sum",
    }).dropna(how="all")

    daily_rows = [[
        "Date", "MQ2 Avg/Max", "MQ135 Avg/Max", "Temp Avg/Max",
        "Fan Avg", "Power Avg", "Alarm Samples",
    ]]

    for index, row in daily_summary.tail(report_days).iterrows():
        daily_rows.append([
            index.strftime("%d %b"),
            f"{row[('MQ2', 'mean')]:.0f}/{row[('MQ2', 'max')]:.0f}",
            f"{row[('MQ135', 'mean')]:.0f}/{row[('MQ135', 'max')]:.0f}",
            f"{row[('Temperature', 'mean')]:.1f}/{row[('Temperature', 'max')]:.1f}",
            f"{row[('Fan Speed (%)', 'mean')]:.1f}%",
            f"{row[('Power (W)', 'mean')]:.2f} W",
            f"{row[('Alarm Value', 'sum')]:.0f}",
        ])

    daily_table = Table(
        daily_rows,
        colWidths=[
            20 * mm, 26 * mm, 29 * mm, 28 * mm,
            22 * mm, 24 * mm, 25 * mm,
        ],
        repeatRows=1,
    )
    daily_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), pdf_colors.HexColor("#12324A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), pdf_colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 6.8),
        ("GRID", (0, 0), (-1, -1), 0.25, pdf_colors.HexColor("#A9BAC8")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            pdf_colors.white,
            pdf_colors.HexColor("#F2F6F9"),
        ]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(daily_table)

    story += [
        Spacer(1, 5 * mm),
        Paragraph(
            "Note: This report supports monitoring and decision-making. It does "
            "not replace certified gas detectors, fire-suppression equipment, "
            "scheduled inspection or emergency procedures.",
            small,
        ),
    ]

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def render_kpi(title, value, state, color_key, note):
    color = COLORS[color_key]
    st.markdown(
        f"""
<div class="kpi-card">
    <div class="kpi-label">{title}</div>
    <div class="kpi-value" style="color:{color};">{value}</div>
    <div class="kpi-state" style="color:{color};">{state}</div>
    <div class="small-note" style="margin-top:8px;">{note}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_hood_figure(mq2, mq135, temp, control, led_status, buzzer_status):
    mq2_state, mq2_color_key = mq2_status(mq2)
    air_state, air_color_key = mq135_status(mq135)
    temp_state_name, temp_color_key = temp_status(temp)

    mq2_color = COLORS[mq2_color_key]
    air_color = COLORS[air_color_key]
    temp_color = COLORS[temp_color_key]
    fan_color = COLORS["green"] if control["fan_speed"] > 0 else COLORS["gray"]
    led_color = COLORS["red"] if led_status == "ON" else COLORS["green"]
    buzzer_color = COLORS["red"] if buzzer_status == "ON" else COLORS["green"]

    smoke_opacity = min(0.9, 0.2 + ((mq2 + mq135) / 2046) * 0.7)
    fan_duration = max(0.35, 2.2 - (control["fan_speed"] / 100) * 1.8)

    html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
body {{
    margin:0;
    background:transparent;
    color:#EAF4FF;
    font-family:Arial, sans-serif;
}}
.wrap {{
    position:relative;
    height:470px;
    background:
        radial-gradient(circle at 50% 45%, rgba(32,197,255,.10), transparent 34%),
        linear-gradient(180deg, rgba(7,17,29,.98), rgba(6,14,24,.98));
    border:1px solid #2A4966;
    border-radius:16px;
    overflow:hidden;
}}
.title {{
    position:absolute;
    left:16px;
    top:14px;
    color:#58CBFF;
    font-size:13px;
    font-weight:900;
    letter-spacing:.04em;
    z-index:5;
}}
.sensor {{
    position:absolute;
    width:165px;
    padding:11px;
    border-radius:12px;
    background:rgba(10,23,38,.96);
    z-index:5;
}}
.name {{
    color:#B6C9DA;
    font-size:11px;
    font-weight:800;
}}
.value {{
    font-size:23px;
    font-weight:900;
    margin-top:4px;
}}
.state {{
    font-size:12px;
    font-weight:900;
    margin-top:4px;
}}
.mq2 {{left:16px; top:60px; border:1px solid {mq2_color};}}
.mq135 {{left:16px; top:205px; border:1px solid {air_color};}}
.temp {{right:16px; top:60px; border:1px solid {temp_color};}}

.stack {{
    position:absolute;
    right:16px;
    bottom:15px;
    width:260px;
    z-index:6;
}}
.device {{
    display:flex;
    align-items:center;
    gap:12px;
    background:rgba(10,23,38,.96);
    border-radius:12px;
    padding:11px;
    margin-top:8px;
}}
.icon {{
    font-size:29px;
}}
.device-name {{
    color:#B6C9DA;
    font-size:11px;
    font-weight:800;
}}
.device-state {{
    font-size:17px;
    font-weight:900;
    margin-top:2px;
}}
.small {{
    color:#92A7BA;
    font-size:11px;
    margin-top:3px;
}}
@keyframes spin {{
    from {{ transform:rotate(0deg); }}
    to {{ transform:rotate(360deg); }}
}}
@keyframes smoke {{
    0% {{ transform:translateY(14px) scale(.92); opacity:.15; }}
    45% {{ opacity:{smoke_opacity}; }}
    100% {{ transform:translateY(-60px) scale(1.1); opacity:0; }}
}}
@keyframes pulse {{
    0%,100% {{opacity:.35;}}
    50% {{opacity:1;}}
}}

@media (max-width: 760px) {{
    .wrap {{ height: 620px; }}
    .title {{ left: 12px; top: 10px; font-size: 11px; }}
    .sensor {{
        position: absolute;
        width: calc(33.333% - 14px);
        min-width: 0;
        padding: 8px;
        box-sizing: border-box;
    }}
    .sensor .value {{ font-size: 17px; }}
    .sensor .name, .sensor .state {{ font-size: 9px; }}
    .mq2 {{ left: 7px; top: 42px; }}
    .mq135 {{ left: calc(33.333% + 2px); top: 42px; }}
    .temp {{ right: 7px; top: 42px; }}
    .stack {{
        left: 10px;
        right: 10px;
        bottom: 10px;
        width: auto;
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 6px;
    }}
    .device {{
        margin-top: 0;
        padding: 8px;
        gap: 7px;
        min-width: 0;
    }}
    .icon {{ font-size: 21px; }}
    .device-name, .small {{ font-size: 8px; }}
    .device-state {{ font-size: 12px; }}
    svg {{ top: 84px !important; height: 420px !important; }}
}}

@media (max-width: 430px) {{
    .wrap {{ height: 720px; }}
    .sensor {{
        width: calc(100% - 14px);
        position: relative;
        left: 7px !important;
        right: auto !important;
        top: auto !important;
        margin-top: 7px;
    }}
    .title {{ position: relative; margin-bottom: 10px; }}
    svg {{ top: 215px !important; height: 340px !important; }}
    .stack {{
        display: grid;
        grid-template-columns: 1fr;
        bottom: 8px;
    }}
    .device {{ padding: 7px 9px; }}
}}

</style>
</head>

<body>
<div class="wrap">
    <div class="title">KITCHEN HOOD DIGITAL TWIN</div>

    <div class="sensor mq2">
        <div class="name">MQ2 LPG SENSOR</div>
        <div class="value" style="color:{mq2_color};">{mq2}</div>
        <div class="state" style="color:{mq2_color};">{mq2_state}</div>
    </div>

    <div class="sensor mq135">
        <div class="name">MQ135 AIR QUALITY</div>
        <div class="value" style="color:{air_color};">{mq135}</div>
        <div class="state" style="color:{air_color};">{air_state}</div>
    </div>

    <div class="sensor temp">
        <div class="name">DHT22 TEMPERATURE</div>
        <div class="value" style="color:{temp_color};">{temp:.1f}°C</div>
        <div class="state" style="color:{temp_color};">{temp_state_name}</div>
    </div>

    <svg viewBox="0 0 900 520" width="100%" height="470"
         style="position:absolute;left:0;bottom:0;z-index:2;">
        <defs>
            <linearGradient id="steel" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#8296AA"/>
                <stop offset="45%" stop-color="#344A60"/>
                <stop offset="100%" stop-color="#192A3B"/>
            </linearGradient>
            <radialGradient id="glow">
                <stop offset="0%" stop-color="{fan_color}" stop-opacity=".55"/>
                <stop offset="100%" stop-color="{fan_color}" stop-opacity="0"/>
            </radialGradient>
        </defs>

        <polyline points="182,98 315,98 315,190"
                  fill="none" stroke="{mq2_color}" stroke-width="2"/>
        <circle cx="182" cy="98" r="7" fill="{mq2_color}"/>

        <polyline points="182,242 305,242 305,285"
                  fill="none" stroke="{air_color}" stroke-width="2"/>
        <circle cx="182" cy="242" r="7" fill="{air_color}"/>

        <polyline points="718,98 640,98 640,188"
                  fill="none" stroke="{temp_color}" stroke-width="2"/>
        <circle cx="718" cy="98" r="7" fill="{temp_color}"/>

        <rect x="410" y="48" width="80" height="92" rx="4"
              fill="#41566A" stroke="#8DA2B4"/>
        <path d="M395 140 L505 140 L568 285 L332 285 Z"
              fill="url(#steel)" stroke="#8DA2B4" stroke-width="3"/>
        <path d="M310 285 L590 285 L624 320 L276 320 Z"
              fill="#23394D" stroke="#8DA2B4" stroke-width="3"/>
        <rect x="340" y="312" width="220" height="14" rx="7"
              fill="{fan_color}" opacity=".65"/>

        <circle cx="640" cy="306" r="80" fill="url(#glow)"/>
        <g transform="translate(640 306)">
            <circle cx="0" cy="0" r="58" fill="#16283A"
                    stroke="{fan_color}" stroke-width="4"/>
            <g style="transform-origin:0px 0px; animation: spin {fan_duration}s linear infinite;">
                <ellipse cx="0" cy="-28" rx="15" ry="31" fill="{fan_color}" opacity=".9"/>
                <ellipse cx="28" cy="0" rx="31" ry="15" fill="{fan_color}" opacity=".9"/>
                <ellipse cx="0" cy="28" rx="15" ry="31" fill="{fan_color}" opacity=".9"/>
                <ellipse cx="-28" cy="0" rx="31" ry="15" fill="{fan_color}" opacity=".9"/>
            </g>
            <circle cx="0" cy="0" r="13" fill="#A8B7C5"/>
        </g>

        <g fill="none" stroke="{fan_color}" stroke-width="8" stroke-linecap="round">
            <path d="M704 270 C758 255, 790 255, 825 245"/>
            <path d="M708 306 C758 306, 792 306, 825 306"/>
            <path d="M704 342 C758 357, 790 357, 825 367"/>
        </g>
        <g fill="{fan_color}">
            <polygon points="825,245 805,234 809,256"/>
            <polygon points="825,306 805,295 805,317"/>
            <polygon points="825,367 809,356 805,378"/>
        </g>

        <rect x="245" y="452" width="410" height="22" rx="5"
              fill="#192A3C" stroke="#52687B"/>
        <ellipse cx="450" cy="431" rx="100" ry="25"
                 fill="#101D29" stroke="#566C80"/>
        <rect x="390" y="386" width="120" height="56" rx="12"
              fill="#202F3E" stroke="#7A8C9E"/>
        <ellipse cx="450" cy="386" rx="60" ry="13"
                 fill="#45596B" stroke="#9AA9B5"/>
        <path d="M390 404 L350 395" stroke="#65798A"
              stroke-width="10" stroke-linecap="round"/>
        <path d="M510 404 L550 395" stroke="#65798A"
              stroke-width="10" stroke-linecap="round"/>

        <g fill="none" stroke="#D2DCE4" stroke-width="10"
           stroke-linecap="round" opacity="{smoke_opacity}">
            <path d="M420 383 C385 342, 455 318, 420 278"
                  style="animation:smoke 2.4s ease-in-out infinite;"/>
            <path d="M452 381 C418 344, 486 318, 455 275"
                  style="animation:smoke 2.7s ease-in-out .4s infinite;"/>
            <path d="M486 383 C454 342, 520 315, 488 278"
                  style="animation:smoke 2.2s ease-in-out .8s infinite;"/>
        </g>
    </svg>

    <div class="stack">
        <div class="device" style="border:1px solid {fan_color};">
            <div class="icon" style="color:{fan_color};">✣</div>
            <div>
                <div class="device-name">BLDC FAN</div>
                <div class="device-state" style="color:{fan_color};">
                    {"ON" if control["fan_speed"] > 0 else "OFF"}
                </div>
                <div class="small">{control["fan_speed"]}% SPEED | PWM {control["pwm"]}</div>
            </div>
        </div>

        <div class="device" style="border:1px solid {led_color};">
            <div class="icon" style="color:{led_color}; animation:{'pulse 1s infinite' if led_status == 'ON' else 'none'};">🚨</div>
            <div>
                <div class="device-name">LED WARNING LIGHT</div>
                <div class="device-state" style="color:{led_color};">{led_status}</div>
                <div class="small">{"WARNING ACTIVE" if led_status == "ON" else "NORMAL"}</div>
            </div>
        </div>

        <div class="device" style="border:1px solid {buzzer_color};">
            <div class="icon" style="color:{buzzer_color}; animation:{'pulse .75s infinite' if buzzer_status == 'ON' else 'none'};">🔊</div>
            <div>
                <div class="device-name">BUZZER</div>
                <div class="device-state" style="color:{buzzer_color};">{buzzer_status}</div>
                <div class="small">{"ALARM ACTIVE" if buzzer_status == "ON" else "STANDBY"}</div>
            </div>
        </div>
    </div>
</div>
</body>
</html>
"""
    components.html(html, height=720, scrolling=False)


# ========================= SIDEBAR =========================

role_icons = {
    "Admin": "🛡️",
    "Lecturer": "🎓",
    "Judge": "⚖️",
}

st.sidebar.success(
    f'{role_icons.get(st.session_state.login_role, "👤")} '
    f'{st.session_state.login_display_name}\n\n'
    f'Role: {st.session_state.login_role}'
)

if st.sidebar.button("🚪 Logout", use_container_width=True):
    logout()

with st.sidebar.expander("🔑 Change Password"):
    with st.form("change_own_password_form", clear_on_submit=True):
        current_password = st.text_input(
            "Current password",
            type="password",
        )
        own_new_password = st.text_input(
            "New password",
            type="password",
        )
        own_confirm_password = st.text_input(
            "Confirm new password",
            type="password",
        )
        own_change_submitted = st.form_submit_button(
            "Change Password",
            use_container_width=True,
        )

    if own_change_submitted:
        success, message = change_own_password(
            st.session_state.login_user_id,
            current_password,
            own_new_password,
            own_confirm_password,
        )
        if success:
            st.success(message)
        else:
            st.error(message)

st.sidebar.markdown("---")

st.sidebar.markdown(
    """
<div style="text-align:center;padding:6px 0 18px;">
    <div style="font-size:48px;">♨️</div>
    <div style="font-size:22px;font-weight:900;">SMART</div>
    <div style="font-size:22px;font-weight:900;">KITCHEN HOOD</div>
    <div style="font-size:11px;color:#20C5FF;margin-top:8px;">AI FUZZY CONTROL SYSTEM</div>
</div>
""",
    unsafe_allow_html=True,
)

is_admin = user_can_control()

if is_admin:
    st.sidebar.title("🎛️ Simulation Control")

    mode = st.sidebar.radio(
        "Control Mode",
        ["Auto AI Control", "Manual Calibration"],
    )

    st.sidebar.markdown("---")

    if mode == "Auto AI Control":
        st.sidebar.subheader("Sensor Simulation")

        random_mode = st.sidebar.toggle("Auto Random Simulation", value=False)
        live_refresh = st.sidebar.toggle("Live Update Every 1 Second", value=True)

        if random_mode:
            st.session_state.sim_mq2 = int(np.clip(
                st.session_state.sim_mq2 + np.random.randint(-55, 56), 80, 950
            ))
            st.session_state.sim_mq135 = int(np.clip(
                st.session_state.sim_mq135 + np.random.randint(-60, 61), 80, 950
            ))
            st.session_state.sim_temp = round(float(np.clip(
                st.session_state.sim_temp + np.random.uniform(-1.5, 1.5), 20, 50
            )), 1)

            mq2 = st.session_state.sim_mq2
            mq135 = st.session_state.sim_mq135
            temp = st.session_state.sim_temp
        else:
            mq2 = st.sidebar.slider("MQ2 LPG Sensor", 0, 1023, 192)
            mq135 = st.sidebar.slider("MQ135 Air Quality Sensor", 0, 1023, 250)
            temp = st.sidebar.slider(
                "DHT22 Temperature (°C)", 20.0, 50.0, 25.2, 0.1
            )

        manual_fan_speed = None
        manual_buzzer_test = False
        manual_led_test = False

    else:
        random_mode = False
        live_refresh = False

        st.sidebar.subheader("Manual Sensor Calibration")

        mq2 = st.sidebar.slider("MQ2 LPG Sensor", 0, 1023, 200)
        mq135 = st.sidebar.slider("MQ135 Air Quality Sensor", 0, 1023, 250)
        temp = st.sidebar.slider(
            "DHT22 Temperature (°C)", 20.0, 50.0, 27.0, 0.1
        )

        st.sidebar.markdown("---")
        st.sidebar.subheader("Manual Output Test")

        manual_fan_speed = st.sidebar.slider(
            "Manual Fan Speed (%)", 0, 100, 50
        )
        manual_buzzer_test = st.sidebar.toggle("Test Buzzer", value=False)
        manual_led_test = st.sidebar.toggle("Test LED", value=False)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Alarm Hardware Condition")

    buzzer_function = st.sidebar.toggle("Buzzer Function OK", value=True)
    led_function = st.sidebar.toggle("LED Function OK", value=True)

    st.sidebar.markdown("---")

    if st.sidebar.button("Reset Record Data", use_container_width=True):
        st.session_state.records = pd.DataFrame()
        st.session_state.event_log = []
        st.session_state.last_event_signature = ""
        st.session_state.total_energy_kwh = 0.0
        st.rerun()

else:
    # Lecturer and Judge accounts are intentionally read-only.
    mode = "Auto AI Control"
    random_mode = True
    live_refresh = True
    manual_fan_speed = None
    manual_buzzer_test = False
    manual_led_test = False
    buzzer_function = True
    led_function = True

    st.sidebar.info(
        "Read-only access: viewing and downloading are allowed. "
        "Control, calibration and reset functions are restricted to Admin."
    )

    # Viewer sessions display an automatically changing demonstration.
    st.session_state.sim_mq2 = int(np.clip(
        st.session_state.sim_mq2 + np.random.randint(-28, 29), 80, 850
    ))
    st.session_state.sim_mq135 = int(np.clip(
        st.session_state.sim_mq135 + np.random.randint(-32, 33), 80, 850
    ))
    st.session_state.sim_temp = round(float(np.clip(
        st.session_state.sim_temp + np.random.uniform(-0.7, 0.7), 20, 46
    )), 1)

    mq2 = st.session_state.sim_mq2
    mq135 = st.session_state.sim_mq135
    temp = st.session_state.sim_temp


# ========================= ADMIN USER MANAGEMENT =========================

if is_admin:
    with st.sidebar.expander("👥 User Management"):
        admin_tab_create, admin_tab_manage, admin_tab_reset = st.tabs(["Create", "Manage", "Reset Requests"])

        with admin_tab_create:
            with st.form("create_database_user", clear_on_submit=True):
                new_username = st.text_input("New username")
                new_display_name = st.text_input("Display name")
                new_password = st.text_input("Temporary password", type="password")
                new_role = st.selectbox("Role", VALID_ROLES)
                create_submitted = st.form_submit_button(
                    "Create User",
                    use_container_width=True,
                )

            if create_submitted:
                success, message = create_user(
                    new_username,
                    new_display_name,
                    new_password,
                    new_role,
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)

        with admin_tab_manage:
            users = list_users()
            user_labels = {
                f'{user["username"]} — {user["role"]}': user
                for user in users
            }

            selected_label = st.selectbox(
                "Select account",
                list(user_labels.keys()),
            )
            selected_user = user_labels[selected_label]

            selected_role = st.selectbox(
                "Account role",
                VALID_ROLES,
                index=VALID_ROLES.index(selected_user["role"]),
                key=f'role_{selected_user["id"]}',
            )
            selected_active = st.toggle(
                "Account active",
                value=bool(selected_user["active"]),
                key=f'active_{selected_user["id"]}',
            )

            if st.button(
                "Update Account",
                use_container_width=True,
                key=f'update_{selected_user["id"]}',
            ):
                success, message = update_user_account(
                    selected_user["id"],
                    selected_role,
                    selected_active,
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

            reset_password_value = st.text_input(
                "New password",
                type="password",
                key=f'password_{selected_user["id"]}',
            )

            if st.button(
                "Reset Password",
                use_container_width=True,
                key=f'reset_password_{selected_user["id"]}',
            ):
                success, message = reset_user_password(
                    selected_user["id"],
                    reset_password_value,
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)

            if st.button(
                "Delete Account",
                use_container_width=True,
                type="secondary",
                key=f'delete_{selected_user["id"]}',
            ):
                success, message = delete_user_account(
                    selected_user["id"],
                    st.session_state.login_user_id,
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

            st.caption(
                f'Created: {selected_user["created_at"]}\n\n'
                f'Last login: {selected_user["last_login"]}'
            )


        with admin_tab_reset:
            reset_requests = list_password_reset_requests()
            pending_requests = [
                request for request in reset_requests
                if request["status"] == "Pending"
            ]

            if not pending_requests:
                st.info("Tiada permintaan reset password yang menunggu.")
            else:
                request_labels = {
                    (
                        f'{request["username"]} — '
                        f'{request["request_time"]}'
                    ): request
                    for request in pending_requests
                }

                selected_request_label = st.selectbox(
                    "Pending request",
                    list(request_labels.keys()),
                )
                selected_request = request_labels[selected_request_label]

                temporary_password = st.text_input(
                    "Temporary password",
                    type="password",
                    key=f'temp_password_{selected_request["id"]}',
                )
                reset_admin_note = st.text_area(
                    "Admin note",
                    key=f'reset_note_{selected_request["id"]}',
                    placeholder="Contoh: Sila tukar password selepas login.",
                )

                if st.button(
                    "Complete Reset",
                    use_container_width=True,
                    key=f'complete_reset_{selected_request["id"]}',
                ):
                    success, message = complete_password_reset_request(
                        selected_request["id"],
                        temporary_password,
                        reset_admin_note,
                    )
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

                if st.button(
                    "Reject Request",
                    use_container_width=True,
                    key=f'reject_reset_{selected_request["id"]}',
                ):
                    success, message = reject_password_reset_request(
                        selected_request["id"],
                        reset_admin_note,
                    )
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

            st.markdown("---")
            st.markdown("#### Reset Request History")

            show_reset_history = st.toggle(
                "Show reset request history",
                value=False,
                key="show_reset_request_history",
            )

            if show_reset_history:
                history_rows = list_password_reset_requests()

                if history_rows:
                    history_df = pd.DataFrame(history_rows)
                    st.dataframe(
                        history_df[
                            [
                                "username",
                                "request_time",
                                "status",
                                "completed_time",
                                "admin_note",
                            ]
                        ],
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.caption("No reset request history.")


# ========================= CONTROL OUTPUT =========================

control = control_logic(mq2, mq135, temp)

if mode == "Manual Calibration":
    control["fan_speed"] = manual_fan_speed
    control["pwm"] = round((manual_fan_speed / 100) * 255)
    control["motor_status"] = (
        "MAXIMUM SPEED" if manual_fan_speed == 100
        else "MEDIUM SPEED" if manual_fan_speed >= 60
        else "LOW SPEED" if manual_fan_speed > 0
        else "OFF"
    )
    control["system_status"] = "MANUAL CALIBRATION"
    control["system_color"] = "blue"
    control["alarm_required"] = manual_buzzer_test or manual_led_test

if mode == "Manual Calibration":
    if manual_buzzer_test and buzzer_function:
        buzzer_status = "ON"
    elif manual_buzzer_test and not buzzer_function:
        buzzer_status = "FAULT"
    else:
        buzzer_status = "OFF"

    if manual_led_test and led_function:
        led_status = "ON"
    elif manual_led_test and not led_function:
        led_status = "FAULT"
    else:
        led_status = "OFF"
else:
    if control["alarm_required"] and buzzer_function:
        buzzer_status = "ON"
    elif control["alarm_required"] and not buzzer_function:
        buzzer_status = "FAULT"
    else:
        buzzer_status = "OFF"

    if control["alarm_required"] and led_function:
        led_status = "ON"
    elif control["alarm_required"] and not led_function:
        led_status = "FAULT"
    else:
        led_status = "OFF"

voltage, current, power = energy_calculation(control["fan_speed"])
update_energy(power)
add_event(control, led_status, buzzer_status)

alarm_value = 1 if led_status == "ON" or buzzer_status == "ON" else 0


# ========================= RECORD DATA =========================

new_row = pd.DataFrame([{
    "Timestamp": datetime.now(),
    "Time": datetime.now().strftime("%H:%M:%S"),
    "Mode": mode,
    "MQ2": int(mq2),
    "MQ135": int(mq135),
    "Temperature": float(temp),
    "PWM": int(control["pwm"]),
    "Fan Speed (%)": int(control["fan_speed"]),
    "Voltage (V)": float(voltage),
    "Current (A)": float(current),
    "Power (W)": float(power),
    "Motor Status": control["motor_status"],
    "Buzzer Status": buzzer_status,
    "LED Status": led_status,
    "Alarm Value": alarm_value,
    "AI Risk (%)": calculate_ai_risk(mq2, mq135, temp),
    "System Health (%)": round(
        (
            st.session_state.sensor_health
            + st.session_state.motor_health
            + st.session_state.fan_health
        ) / 3,
        1,
    ),
    "System Status": control["system_status"],
}])

if st.session_state.records.empty:
    st.session_state.records = new_row.copy()
else:
    last_time = str(st.session_state.records.iloc[-1]["Time"])
    current_time = str(new_row.iloc[0]["Time"])

    if last_time == current_time:
        st.session_state.records.iloc[-1] = new_row.iloc[0]
    else:
        st.session_state.records = pd.concat(
            [st.session_state.records, new_row],
            ignore_index=True,
        ).tail(MAX_RECORDS).reset_index(drop=True)

df = st.session_state.records.copy()

# Persist the latest reading for 7-day and 30-day historical reports.
try:
    save_monitoring_record(new_row.iloc[0].to_dict())
except sqlite3.Error as database_error:
    st.sidebar.warning(f"Historical database warning: {database_error}")


# ========================= HEADER =========================

left, right = st.columns([4.5, 1.2])

with left:
    st.markdown(
        '<div class="dashboard-title">Smart Kitchen Hood AI Dashboard</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="dashboard-subtitle">Real-Time Monitoring | AI Analysis | Fuzzy Logic Control | Alarm & Energy Management | Access: {st.session_state.login_role}</div>',
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        f"""
<div class="panel" style="padding:13px;">
    <div class="small-note">Mode</div>
    <div style="font-weight:900;color:{COLORS['green'] if mode == 'Auto AI Control' else COLORS['blue']};">
        {mode.upper()}
    </div>
    <div class="small-note" style="margin-top:7px;">Last Updated</div>
    <div style="font-weight:900;">{datetime.now().strftime('%H:%M:%S')}</div>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown("---")



# ========================= KPI CARDS =========================

mq2_state, mq2_color_key = mq2_status(mq2)
air_state, air_color_key = mq135_status(mq135)
temp_state_name, temp_color_key = temp_status(temp)

risk_score = calculate_ai_risk(mq2, mq135, temp)
risk_text, risk_color_key = risk_status(risk_score)

health_score_value = round(
    (
        st.session_state.sensor_health
        + st.session_state.motor_health
        + st.session_state.fan_health
    ) / 3,
    1,
)
health_text, health_color_key = health_status(health_score_value)

k1, k2, k3, k4, k5, k6, k7, k8, k9 = st.columns(9)

with k1:
    render_kpi("MQ2 (LPG)", mq2, mq2_state, mq2_color_key, "Gas concentration")

with k2:
    render_kpi("MQ135", mq135, air_state, air_color_key, "Air quality")

with k3:
    render_kpi(
        "Temperature",
        f"{temp:.1f}°C",
        temp_state_name,
        temp_color_key,
        "DHT22",
    )

with k4:
    render_kpi(
        "Fan Speed",
        f'{control["fan_speed"]}%',
        control["motor_status"],
        "blue",
        f'PWM {control["pwm"]}',
    )

with k5:
    render_kpi("Power", f"{power:.2f} W", "12 V DC", "purple", "Motor power")

with k6:
    render_kpi("Current", f"{current:.2f} A", "LIVE", "blue", "Motor current")

with k7:
    render_kpi(
        "Energy",
        f"{st.session_state.total_energy_kwh:.4f}",
        "kWh",
        "yellow",
        "Accumulated",
    )

with k8:
    render_kpi(
        "AI Risk Score",
        f"{risk_score:.0f}%",
        risk_text,
        risk_color_key,
        "Weighted sensor risk",
    )

with k9:
    render_kpi(
        "AI Health Score",
        f"{health_score_value:.0f}%",
        health_text,
        health_color_key,
        "System condition",
    )

st.write("")


# ========================= KITCHEN HOOD + RULE LOGIC =========================

overview_col, rule_col = st.columns([3.4, 1.15])

with overview_col:
    render_hood_figure(mq2, mq135, temp, control, led_status, buzzer_status)

with rule_col:
    rule_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
body {{
    margin: 0;
    background: transparent;
    color: #EAF4FF;
    font-family: Arial, sans-serif;
}}
.panel {{
    min-height: 438px;
    background: linear-gradient(145deg, rgba(15,28,44,.98), rgba(8,18,30,.98));
    border: 1px solid #263A52;
    padding: 16px;
    border-radius: 14px;
    box-sizing: border-box;
}}
.section-title {{
    color: #58CBFF;
    font-weight: 900;
    font-size: 14px;
    letter-spacing: .03em;
    margin-bottom: 16px;
}}
.small-note {{
    color: #93A7BA;
    font-size: 12px;
    line-height: 1.5;
}}
.rule-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    padding: 9px 0;
    border-bottom: 1px solid rgba(150,180,210,.10);
    font-size: 13px;
}}
.summary {{
    margin-top: 15px;
    padding: 11px;
    border-radius: 10px;
    border: 1px solid #29435F;
    background: #0A1928;
}}

@media (max-width: 620px) {{
    .panel {{ min-height: auto; padding: 12px; }}
    .rule-row {{ font-size: 11px; align-items: flex-start; }}
    .rule-row span, .rule-row b {{ max-width: 52%; overflow-wrap: anywhere; }}
    .section-title {{ font-size: 12px; }}
}}

</style>
</head>
<body>
<div class="panel">
    <div class="section-title">RULE LOGIC (FUZZY SYSTEM)</div>

    <div class="small-note">Current Rule Status</div>

    <div class="rule-row">
        <span>MQ2 LPG level</span>
        <b style="color:{COLORS[mq2_color_key]};">{mq2_state}</b>
    </div>

    <div class="rule-row">
        <span>Air quality</span>
        <b style="color:{COLORS[air_color_key]};">{air_state}</b>
    </div>

    <div class="rule-row">
        <span>Temperature</span>
        <b style="color:{COLORS[temp_color_key]};">{temp_state_name}</b>
    </div>

    <div style="text-align:center;color:#20C5FF;font-size:29px;margin:8px 0;">↓</div>

    <div class="small-note">System Action</div>

    <div class="rule-row">
        <span>Fan speed</span>
        <b style="color:{COLORS['green'] if control['fan_speed'] > 0 else COLORS['gray']};">
            {control["fan_speed"]}%
        </b>
    </div>

    <div class="rule-row">
        <span>LED light</span>
        <b style="color:{COLORS['red'] if led_status == 'ON' else COLORS['green']};">
            {led_status}
        </b>
    </div>

    <div class="rule-row">
        <span>Buzzer</span>
        <b style="color:{COLORS['red'] if buzzer_status == 'ON' else COLORS['green']};">
            {buzzer_status}
        </b>
    </div>

    <div class="rule-row">
        <span>PWM output</span>
        <b>{control["pwm"]}</b>
    </div>

    <div style="margin-top:14px;color:{COLORS[control['system_color']]};font-weight:900;">
        Result: {control["system_status"]}
    </div>

    <div class="summary">
        <div class="small-note">
            Green = safe or normal<br>
            Yellow = warning or moderate<br>
            Red = dangerous or active alarm
        </div>
    </div>
</div>
</body>
</html>
"""
    components.html(rule_html, height=520, scrolling=False)



# ========================= AI RECOMMENDATION, PREDICTION & HEALTH =========================

pred_mq2, pred_mq135, pred_temp = predict_next_30_seconds(
    df, mq2, mq135, temp
)
pred_risk = calculate_ai_risk(pred_mq2, pred_mq135, pred_temp)
pred_risk_text, pred_risk_color = risk_status(pred_risk)

rec_title, rec_text, rec_color = ai_recommendation(
    control, mq2, mq135, temp
)

ai1, ai2, ai3 = st.columns([1.2, 1.2, 1])

with ai1:
    st.markdown(
        f"""
<div class="panel">
    <div class="section-title">AI RECOMMENDATION</div>
    <div style="border:1px solid {COLORS[rec_color]};
                border-radius:12px;padding:14px;">
        <div style="font-size:18px;font-weight:900;
                    color:{COLORS[rec_color]};">
            {rec_title}
        </div>
        <div class="small-note" style="margin-top:8px;">
            {rec_text}
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with ai2:
    st.markdown(
        f"""
<div class="panel">
    <div class="section-title">AI PREDICTION (NEXT 30 SECONDS)</div>
    <div class="rule-row"><span>MQ2 LPG</span><b>{pred_mq2}</b></div>
    <div class="rule-row"><span>MQ135 Air Quality</span><b>{pred_mq135}</b></div>
    <div class="rule-row"><span>Temperature</span><b>{pred_temp:.1f}°C</b></div>
    <div class="rule-row">
        <span>Predicted Risk</span>
        <b style="color:{COLORS[pred_risk_color]};">
            {pred_risk:.0f}% — {pred_risk_text}
        </b>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with ai3:
    st.markdown(
        f"""
<div class="panel">
    <div class="section-title">SYSTEM HEALTH</div>
    <div class="rule-row"><span>Sensors</span><b>{st.session_state.sensor_health:.0f}%</b></div>
    <div class="rule-row"><span>Motor</span><b>{st.session_state.motor_health:.0f}%</b></div>
    <div class="rule-row"><span>Fan</span><b>{st.session_state.fan_health:.0f}%</b></div>
    <div class="rule-row">
        <span>Overall</span>
        <b style="color:{COLORS[health_color_key]};">
            {health_score_value:.0f}%
        </b>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


# ========================= MOTOR & ALARM INDICATORS =========================

st.subheader("Motor and Alarm Indicator")

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(
        f"""
<div class="panel">
    <div class="section-title">BLDC FAN STATUS</div>
    <div class="status-pill" style="color:{COLORS['green'] if control['fan_speed'] > 0 else COLORS['gray']};">
        {control["motor_status"]}
    </div>
    <div class="small-note" style="margin-top:10px;">
        {control["fan_speed"]}% speed | PWM {control["pwm"]}
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with m2:
    led_color = COLORS["red"] if led_status == "ON" else COLORS["green"]
    st.markdown(
        f"""
<div class="panel">
    <div class="section-title">LED WARNING LIGHT</div>
    <div class="status-pill" style="color:{led_color};">{led_status}</div>
    <div class="small-note" style="margin-top:10px;">
        {"Warning active" if led_status == "ON" else "Normal condition"}
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with m3:
    buzzer_color = COLORS["red"] if buzzer_status == "ON" else COLORS["green"]
    st.markdown(
        f"""
<div class="panel">
    <div class="section-title">BUZZER</div>
    <div class="status-pill" style="color:{buzzer_color};">{buzzer_status}</div>
    <div class="small-note" style="margin-top:10px;">
        {"Alarm active" if buzzer_status == "ON" else "Standby"}
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with m4:
    st.markdown(
        f"""
<div class="panel">
    <div class="section-title">SYSTEM PROTECTION</div>
    <div class="status-pill" style="color:{COLORS[control['system_color']]};">
        ACTIVE
    </div>
    <div class="small-note" style="margin-top:10px;">
        {control["system_status"]}
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


# ========================= STATUS MESSAGE =========================

if control["system_color"] == "green":
    st.success("System is safe. Fan, LED and buzzer are operating according to the normal rule.")
elif control["system_color"] == "yellow":
    st.warning("Caution condition detected. Fan speed has been increased for ventilation.")
elif control["system_color"] == "red":
    st.error("Dangerous condition detected. Fan is at maximum speed and the alarm system is active.")
else:
    st.info("Manual calibration mode is active.")


# ========================= GAUGES =========================

st.subheader("Real-Time Gauges")

g1, g2, g3, g4 = st.columns(4)

with g1:
    st.plotly_chart(
        make_gauge(control["fan_speed"], "Fan Speed", "%", 100, 35, 70),
        use_container_width=True,
        config={"displayModeBar": False, "responsive": True},
    )

with g2:
    st.plotly_chart(
        make_gauge(temp, "Temperature", "°C", 50, 28, 36),
        use_container_width=True,
        config={"displayModeBar": False, "responsive": True},
    )

with g3:
    st.plotly_chart(
        make_gauge(current, "Current", " A", 1.2, 0.45, 0.85),
        use_container_width=True,
        config={"displayModeBar": False, "responsive": True},
    )

with g4:
    st.plotly_chart(
        make_gauge(power, "Power", " W", 15, 5, 10),
        use_container_width=True,
        config={"displayModeBar": False, "responsive": True},
    )


PLOTLY_CONFIG = {
    "displayModeBar": False,
    "scrollZoom": False,
    "doubleClick": False,
    "responsive": True,
}

# ========================= LIVE GRAPHS =========================

st.subheader("Live Record Graphs")

c1, c2 = st.columns(2)

with c1:
    st.plotly_chart(
        make_line_chart(
            df,
            ["MQ2", "MQ135", "Temperature"],
            "Sensor Reading Trend Over Time",
            "Sensor Reading",
        ),
        use_container_width=True,
        config=PLOTLY_CONFIG,
    )

with c2:
    st.plotly_chart(
        make_line_chart(
            df,
            ["Fan Speed (%)"],
            "Fan Speed Record Over Time",
            "Fan Speed (%)",
        ),
        use_container_width=True,
        config=PLOTLY_CONFIG,
    )

c3, c4 = st.columns(2)

with c3:
    st.plotly_chart(
        make_line_chart(
            df,
            ["Current (A)", "Power (W)"],
            "Current and Power Usage Over Time",
            "Current / Power",
        ),
        use_container_width=True,
        config=PLOTLY_CONFIG,
    )

with c4:
    st.plotly_chart(
        make_line_chart(
            df,
            ["Alarm Value"],
            "Alarm Event Timeline",
            "0 = OFF, 1 = ON",
        ),
        use_container_width=True,
        config=PLOTLY_CONFIG,
    )


# ========================= ENERGY SUMMARY =========================

st.subheader("Energy Monitoring")

e1, e2, e3, e4 = st.columns(4)

e1.metric("Voltage", f"{voltage:.1f} V")
e2.metric("Current", f"{current:.2f} A")
e3.metric("Power", f"{power:.2f} W")
e4.metric("Accumulated Energy", f"{st.session_state.total_energy_kwh:.5f} kWh")


# ========================= EVENT LOG + AI =========================

log_col, ai_col = st.columns([1.7, 1])

with log_col:
    st.markdown('<div class="section-title">ALARM HISTORY</div>', unsafe_allow_html=True)

    if st.session_state.event_log:
        log_df = pd.DataFrame(st.session_state.event_log)
        st.dataframe(log_df, use_container_width=True, hide_index=True)
    else:
        st.info("No alarm event recorded yet.")

with ai_col:
    st.markdown('<div class="section-title">AI SYSTEM ANALYSIS</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
<div class="panel">
    <div style="display:flex;gap:12px;align-items:flex-start;">
        <div style="font-size:42px;">🧠</div>
        <div>
            <div style="font-weight:900;color:{COLORS[control['system_color']]};">
                {control["system_status"]}
            </div>
            <div class="small-note" style="margin-top:8px;">
                {ai_analysis(control, mq2, mq135, temp, power)}
            </div>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )



# ========================= FUZZY INFERENCE PROCESS =========================

st.subheader("Fuzzy Logic Inference Process")

p1, p2, p3, p4, p5 = st.columns(5)

steps = [
    (
        "1",
        "Fuzzification",
        "Convert MQ2, MQ135 and temperature into fuzzy membership values.",
    ),
    (
        "2",
        "Rule Evaluation",
        "Evaluate the 27 IF-THEN fuzzy rules.",
    ),
    (
        "3",
        "Aggregation",
        "Combine the strength of all active rules.",
    ),
    (
        "4",
        "Defuzzification",
        "Convert fuzzy output into one numerical PWM value.",
    ),
    (
        "5",
        "Output",
        f'PWM {control["pwm"]} → Fan {control["fan_speed"]}%',
    ),
]

for col, (number, title, description) in zip(
    [p1, p2, p3, p4, p5],
    steps,
):
    with col:
        st.markdown(
            f"""
<div class="panel" style="min-height:145px;">
    <div style="font-size:20px;color:#43D668;font-weight:900;">
        {number}
    </div>
    <div style="font-weight:900;margin-top:5px;">{title}</div>
    <div class="small-note" style="margin-top:7px;">
        {description}
    </div>
</div>
""",
            unsafe_allow_html=True,
        )


# ========================= LCD PREVIEW =========================

st.subheader("LCD Preview")

lcd1, lcd2 = st.columns(2)

with lcd1:
    st.code(f"MQ2:{mq2} AQ:{mq135}")
    st.code(f"T:{temp:.1f}C FAN:{control['fan_speed']}%")

with lcd2:
    st.code(f"BUZ:{buzzer_status} LED:{led_status}")
    st.code(f"PWM:{control['pwm']} {control['system_status']}")


# ========================= RULE TABLE =========================

st.subheader("Control Rule Table")

rule_table = pd.DataFrame({
    "Condition": [
        "All sensors safe",
        "One moderate parameter",
        "Two moderate parameters",
        "Any dangerous parameter",
        "Multiple dangerous parameters",
    ],
    "Fan Speed": [
        "OFF",
        "Low speed",
        "Medium speed",
        "Maximum speed",
        "Maximum speed",
    ],
    "PWM": [0, 85, 170, 255, 255],
    "LED": ["OFF", "OFF", "OFF", "ON", "ON"],
    "Buzzer": ["OFF", "OFF", "OFF", "ON", "ON"],
})

st.dataframe(rule_table, use_container_width=True, hide_index=True)


# ========================= ROLE ACCESS NOTICE =========================

if not is_admin:
    st.info(
        f'{st.session_state.login_role} access is read-only. '
        "Dashboard records may be viewed and downloaded, but system controls "
        "and user settings cannot be changed."
    )


# ========================= DATA DOWNLOAD & HISTORICAL REPORT =========================

st.subheader("Record Data")

st.dataframe(df, use_container_width=True, hide_index=True)

csv_data = df.to_csv(index=False).encode("utf-8")

st.markdown(
    download_link(
        csv_data,
        "smart_kitchen_hood_full_record.csv",
        "Download Current Session Record CSV",
    ),
    unsafe_allow_html=True,
)

graph_csv = df[[
    "Time",
    "MQ2",
    "MQ135",
    "Temperature",
    "Fan Speed (%)",
    "Current (A)",
    "Power (W)",
    "Alarm Value",
]].to_csv(index=False).encode("utf-8")

st.markdown(
    download_link(
        graph_csv,
        "smart_kitchen_hood_graph_record.csv",
        "Download Current Session Graph CSV",
    ),
    unsafe_allow_html=True,
)

if st.session_state.login_role in ["Admin", "Lecturer"]:
    st.markdown("---")
    st.markdown("### Historical AI PDF Report")

    report_period_label = st.radio(
        "Select report period",
        ["Last 7 Days", "Last 30 Days"],
        horizontal=True,
        key="historical_report_period",
    )
    report_days = 7 if report_period_label == "Last 7 Days" else 30

    historical_report_df = load_historical_records(report_days)
    report_summary_preview = calculate_period_summary(
        historical_report_df,
        report_days,
    )

    rp1, rp2, rp3, rp4 = st.columns(4)
    rp1.metric("Stored Records", report_summary_preview["sample_count"])
    rp2.metric("Alarm Samples", report_summary_preview["alarm_count"])
    rp3.metric("Average Fan", f'{report_summary_preview["avg_fan"]:.1f}%')
    rp4.metric("Average Power", f'{report_summary_preview["avg_power"]:.2f} W')

    st.markdown("#### 🤖 AI Period Summary")

    show_period_summary = st.toggle(
        "Show AI period summary",
        value=True,
        key=f"show_ai_period_summary_{report_days}",
    )

    if show_period_summary:
        period_summary_text = build_period_ai_summary(
            historical_report_df,
            report_days,
        )

        st.markdown(
            f"""
            <div class="panel ai-period-summary-card">
                <div class="section-title">
                    LAST {report_days} DAYS ANALYSIS
                </div>
                <div class="small-note ai-period-summary-text">
                    {period_summary_text}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if historical_report_df.empty:
        st.warning(
            f"No stored records are available for the last {report_days} days. "
            "New records will be stored automatically while the dashboard runs."
        )

    if REPORTLAB_AVAILABLE:
        if st.button(
            f"Prepare {report_days}-Day PDF Report",
            use_container_width=True,
            key=f"prepare_pdf_{report_days}",
        ):
            with st.spinner(
                f"Generating {report_days}-day report, graphs and AI summary..."
            ):
                pdf_bytes = build_pdf_report(
                    historical_report_df,
                    report_days,
                    control,
                    mq2,
                    mq135,
                    temp,
                    voltage,
                    current,
                    power,
                    risk_score,
                    risk_text,
                    health_score_value,
                    led_status,
                    buzzer_status,
                )
                st.session_state.generated_historical_pdf = pdf_bytes
                st.session_state.generated_historical_pdf_days = report_days

        generated_pdf = st.session_state.get("generated_historical_pdf")
        generated_days = st.session_state.get(
            "generated_historical_pdf_days"
        )

        if generated_pdf and generated_days == report_days:
            pdf_filename = (
                f"smart_kitchen_hood_{report_days}_day_ai_report_"
                + datetime.now().strftime("%Y%m%d_%H%M%S")
                + ".pdf"
            )
            st.markdown(
                generic_download_link(
                    generated_pdf,
                    "application/pdf",
                    pdf_filename,
                    f"Download {report_days}-Day PDF Report",
                ),
                unsafe_allow_html=True,
            )
    else:
        st.warning(
            "PDF report requires ReportLab. Install: pip install reportlab"
        )

    if not MATPLOTLIB_AVAILABLE:
        st.warning(
            "PDF graphs require Matplotlib. Install: pip install matplotlib"
        )
else:
    st.caption(
        "Historical PDF reports are available to Admin and Lecturer accounts."
    )


# ========================= AUTO REFRESH =========================

# Refresh only while a changing live simulation is active. A slower interval
# reduces WebSocketClosedError messages when a tab is reloaded or disconnected.
refresh_required = (
    mode == "Auto AI Control"
    and live_refresh
    and (random_mode or not is_admin)
)

if refresh_required:
    if AUTOREFRESH_AVAILABLE:
        st_autorefresh(
            interval=2500,
            key="kitchen_hood_live_refresh_v3",
        )
    else:
        st.warning(
            "For live automatic updates, install: pip install streamlit-autorefresh"
        )
