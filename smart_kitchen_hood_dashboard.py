
import time
import textwrap
import base64
import hashlib
import hmac
from datetime import datetime

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

# ============================================================
# SMART KITCHEN HOOD AI DASHBOARD - FINAL VERSION
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
</style>
""",
    unsafe_allow_html=True,
)


# ========================= LOGIN SECURITY =========================
# Default login for local testing:
# Username: admin
# Password: admin123
#
# For deployment, create .streamlit/secrets.toml:
# APP_USERNAME = "your_username"
# APP_PASSWORD = "your_strong_password"

def get_secret(name, default):
    """Read Streamlit secret safely and use a local fallback."""
    try:
        return str(st.secrets.get(name, default))
    except Exception:
        return default


APP_USERNAME = get_secret("APP_USERNAME", "admin")
APP_PASSWORD_HASH = hashlib.sha256(
    get_secret("APP_PASSWORD", "admin123").encode("utf-8")
).hexdigest()

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 30

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "login_username" not in st.session_state:
    st.session_state.login_username = ""

if "failed_login_attempts" not in st.session_state:
    st.session_state.failed_login_attempts = 0

if "lockout_until" not in st.session_state:
    st.session_state.lockout_until = 0.0


def verify_login(username, password):
    """Use constant-time comparison for username and password hash."""
    supplied_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    username_ok = hmac.compare_digest(username.strip(), APP_USERNAME)
    password_ok = hmac.compare_digest(supplied_hash, APP_PASSWORD_HASH)
    return username_ok and password_ok


def logout():
    """End the current authenticated session."""
    st.session_state.authenticated = False
    st.session_state.login_username = ""
    st.session_state.failed_login_attempts = 0
    st.session_state.lockout_until = 0.0
    st.rerun()


def render_login():
    """Display the login page and stop access to the dashboard."""
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {display:none;}
        .login-shell {
            max-width: 480px;
            margin: 8vh auto 0 auto;
            padding: 32px;
            background: linear-gradient(145deg, rgba(16,29,45,.99), rgba(8,18,30,.99));
            border: 1px solid #2A4966;
            border-radius: 18px;
            box-shadow: 0 18px 55px rgba(0,0,0,.35);
        }
        .login-icon {
            text-align:center;
            font-size:52px;
            margin-bottom:8px;
        }
        .login-heading {
            text-align:center;
            color:#F5FAFF;
            font-size:29px;
            font-weight:900;
        }
        .login-caption {
            text-align:center;
            color:#8EA2B7;
            font-size:13px;
            margin:8px 0 24px 0;
        }
        </style>
        <div class="login-shell">
            <div class="login-icon">🔐</div>
            <div class="login-heading">Secure System Login</div>
            <div class="login-caption">
                Smart Kitchen Hood AI Monitoring Dashboard
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

    with st.form("secure_login_form", clear_on_submit=False):
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
        if verify_login(username, password):
            st.session_state.authenticated = True
            st.session_state.login_username = username.strip()
            st.session_state.failed_login_attempts = 0
            st.session_state.lockout_until = 0.0
            st.rerun()
        else:
            st.session_state.failed_login_attempts += 1
            attempts_left = (
                MAX_LOGIN_ATTEMPTS
                - st.session_state.failed_login_attempts
            )

            if st.session_state.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
                st.session_state.lockout_until = time.time() + LOCKOUT_SECONDS
                st.session_state.failed_login_attempts = 0
                st.error(
                    "Akses dikunci selama 30 saat kerana terlalu banyak "
                    "percubaan login gagal."
                )
            else:
                st.error(
                    "Username atau password tidak betul. "
                    f"Baki percubaan: {attempts_left}."
                )

    st.caption("Login asal untuk ujian tempatan: admin / admin123")


if not st.session_state.authenticated:
    render_login()
    st.stop()


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
    components.html(html, height=470, scrolling=False)


# ========================= SIDEBAR =========================

st.sidebar.success(
    f"🔐 Logged in as: {st.session_state.login_username}"
)

if st.sidebar.button("🚪 Logout", use_container_width=True):
    logout()

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
        temp = st.sidebar.slider("DHT22 Temperature (°C)", 20.0, 50.0, 25.2, 0.1)

    manual_fan_speed = None
    manual_buzzer_test = False
    manual_led_test = False

else:
    random_mode = False
    live_refresh = False

    st.sidebar.subheader("Manual Sensor Calibration")

    mq2 = st.sidebar.slider("MQ2 LPG Sensor", 0, 1023, 200)
    mq135 = st.sidebar.slider("MQ135 Air Quality Sensor", 0, 1023, 250)
    temp = st.sidebar.slider("DHT22 Temperature (°C)", 20.0, 50.0, 27.0, 0.1)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Manual Output Test")

    manual_fan_speed = st.sidebar.slider("Manual Fan Speed (%)", 0, 100, 50)
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


# ========================= HEADER =========================

left, right = st.columns([4.5, 1.2])

with left:
    st.markdown(
        '<div class="dashboard-title">Smart Kitchen Hood AI Dashboard</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="dashboard-subtitle">Real-Time Monitoring | AI Analysis | Fuzzy Logic Control | Alarm & Energy Management</div>',
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
    components.html(rule_html, height=470, scrolling=False)



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


# ========================= DATA DOWNLOAD =========================

st.subheader("Record Data")

st.dataframe(df, use_container_width=True, hide_index=True)

csv_data = df.to_csv(index=False).encode("utf-8")

st.markdown(
    download_link(
        csv_data,
        "smart_kitchen_hood_full_record.csv",
        "Download Full Record CSV",
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
        "Download Graph Record CSV",
    ),
    unsafe_allow_html=True,
)


# ========================= AUTO REFRESH =========================

if mode == "Auto AI Control" and live_refresh:
    if AUTOREFRESH_AVAILABLE:
        st_autorefresh(interval=1000, limit=None, key="kitchen_hood_live_refresh")
    else:
        st.warning(
            "For smoother 1-second updates, install: "
            "pip install streamlit-autorefresh"
        )
