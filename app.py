# app.py — Interstellar-AI Space Mission Health Console (Cloud-safe)
# ✅ No while True loop
# ✅ No st.autorefresh
# ✅ Session-state safe (no AttributeError)
# ✅ HAB-style telemetry: Altitude, Temp, Pressure, Humidity + SNR/Link
# ✅ Floating star background + hero layout + single event log

import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Interstellar-AI | Space Mission Console",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# CSS — SPACE THEME + FLOATING STARS
# =========================================================
STAR_CSS = """
<style>
.stApp{
  background: radial-gradient(1200px 600px at 50% 0%, rgba(40,90,255,.18), rgba(0,0,0,0) 65%),
              linear-gradient(180deg, #020617 0%, #000000 70%);
  color: #e5e7eb;
}
.block-container{ padding-top: 1.2rem; }

@keyframes drift1 { from {transform: translateY(0);} to {transform: translateY(-1200px);} }
@keyframes drift2 { from {transform: translateY(0);} to {transform: translateY(-900px);} }

.starwrap{ position: fixed; inset: 0; z-index: -1; overflow: hidden; }
.stars, .stars2{
  position: absolute; inset: -200% -50% -200% -50%;
  background-repeat: repeat;
  animation-timing-function: linear;
  animation-iteration-count: infinite;
  filter: drop-shadow(0 0 2px rgba(120,220,255,.35));
}
.stars{
  background-image:
    radial-gradient(1px 1px at 20px 30px, rgba(255,255,255,.85) 50%, transparent 55%),
    radial-gradient(1px 1px at 80px 120px, rgba(180,240,255,.85) 50%, transparent 55%),
    radial-gradient(1px 1px at 160px 60px, rgba(255,255,255,.75) 50%, transparent 55%),
    radial-gradient(1px 1px at 220px 180px, rgba(200,230,255,.70) 50%, transparent 55%),
    radial-gradient(1px 1px at 300px 90px, rgba(255,255,255,.80) 50%, transparent 55%);
  background-size: 320px 220px;
  animation-name: drift1;
  animation-duration: 140s;
  opacity: .9;
}
.stars2{
  background-image:
    radial-gradient(1px 1px at 40px 50px, rgba(255,255,255,.55) 50%, transparent 55%),
    radial-gradient(1px 1px at 140px 180px, rgba(180,240,255,.55) 50%, transparent 55%),
    radial-gradient(1px 1px at 240px 110px, rgba(255,255,255,.45) 50%, transparent 55%),
    radial-gradient(1px 1px at 320px 200px, rgba(200,230,255,.45) 50%, transparent 55%),
    radial-gradient(1px 1px at 420px 140px, rgba(255,255,255,.50) 50%, transparent 55%);
  background-size: 460px 260px;
  animation-name: drift2;
  animation-duration: 220s;
  opacity: .55;
}

.hero{
  border-radius: 18px;
  padding: 26px 28px;
  background: linear-gradient(180deg, rgba(10,20,50,.80), rgba(0,0,0,.55));
  border: 1px solid rgba(90,160,255,.18);
  box-shadow: 0 0 35px rgba(0,180,255,.12);
  margin-bottom: 18px;
}
.hero-title{
  font-size: 40px;
  font-weight: 900;
  letter-spacing: .2px;
  color: #ffffff;
  text-shadow: 0 0 22px rgba(0,200,255,.40);
  margin: 0;
}
.hero-subtitle{
  font-size: 15.5px;
  color: rgba(220,240,255,.88);
  margin-top: 8px;
  line-height: 1.45;
}
.mini{
  font-size: 12.5px;
  color: rgba(220,240,255,.65);
}

.pill{
  display:inline-flex;
  align-items:center;
  gap:8px;
  padding: 7px 14px;
  border-radius: 999px;
  font-weight: 800;
  font-size: 12.5px;
  letter-spacing: .2px;
  border: 1px solid rgba(255,255,255,.10);
}
.pill-ok{ background: rgba(16,185,129,.16); color: #7CFFCB; border-color: rgba(16,185,129,.45); }
.pill-warn{ background: rgba(245,158,11,.16); color: #FFE2A8; border-color: rgba(245,158,11,.45); }
.pill-crit{ background: rgba(239,68,68,.16); color: #FFC0C0; border-color: rgba(239,68,68,.55); }
.pill-mode{ background: rgba(148,163,184,.12); color: rgba(255,255,255,.86); border-color: rgba(148,163,184,.35); }

.card{
  border-radius: 18px;
  padding: 16px 18px;
  background: rgba(2,6,23,.55);
  border: 1px solid rgba(90,160,255,.18);
  box-shadow: 0 0 22px rgba(0,180,255,.10);
  min-height: 110px;
}
.card-k{
  font-size: 12.5px;
  color: rgba(220,240,255,.70);
  margin-bottom: 6px;
  font-weight: 700;
}
.card-v{
  font-size: 32px;
  font-weight: 900;
  color: #ffffff;
  line-height: 1.1;
}
.card-u{
  font-size: 12.5px;
  color: rgba(220,240,255,.62);
  margin-top: 6px;
}

[data-testid="stMetric"]{
  background: rgba(2,6,23,.35);
  border: 1px solid rgba(90,160,255,.14);
  border-radius: 14px;
  padding: 10px 12px;
}
</style>
"""
st.markdown(STAR_CSS, unsafe_allow_html=True)
st.markdown('<div class="starwrap"><div class="stars"></div><div class="stars2"></div></div>', unsafe_allow_html=True)

# =========================================================
# SESSION STATE (SAFE INIT)
# =========================================================
st.session_state.setdefault("running", True)
st.session_state.setdefault("tick", 0)
st.session_state.setdefault("history", [])
st.session_state.setdefault("log", [])
st.session_state.setdefault(
    "last",
    {
        "time": datetime.now().strftime("%H:%M:%S"),
        "Altitude_m": 0.0,
        "Temp_C": 28.0,
        "Pressure_hPa": 1013.0,
        "Humidity_pct": 60.0,
        "SNR_dB": 18.0,
    },
)

# =========================================================
# SIDEBAR CONTROLS
# =========================================================
with st.sidebar:
    st.header("⚙️ Demo Controls")
    refresh_s = st.slider("Refresh interval (seconds)", 0.5, 5.0, 1.5, 0.5)
    demo_mode = st.selectbox("Telemetry source", ["Simulated (for expo)", "Hold last values"], index=0)
    anomaly_rate = st.slider("Anomaly probability", 0.0, 0.30, 0.12, 0.01)
    show_trend = st.checkbox("Show trend chart", value=True)
    max_hist = st.slider("History window (samples)", 20, 120, 60, 10)

# =========================================================
# HELPERS
# =========================================================
def hab_profile(t: int) -> float:
    ascend = 90
    floatp = 20
    descend = 90

    if t <= ascend:
        return (t / ascend) * 30000.0
    if t <= ascend + floatp:
        return 30000.0
    td = t - (ascend + floatp)
    if td <= descend:
        return max(0.0, 30000.0 * (1 - td / descend))
    return 0.0

def simulate_telemetry(tick: int) -> dict:
    alt = hab_profile(tick) + np.random.randn() * 120.0
    alt = max(0.0, alt)

    temp = 28.0 - (alt / 1000.0) * 2.0 + np.random.randn() * 0.6
    pressure = 1013.25 * np.exp(-alt / 7500.0) + np.random.randn() * 2.0
    humidity = max(0.0, 65.0 - (alt / 1000.0) * 1.2 + np.random.randn() * 1.0)
    snr = 18.0 + np.random.randn() * 0.8

    return {
        "time": datetime.now().strftime("%H:%M:%S"),
        "Altitude_m": float(alt),
        "Temp_C": float(temp),
        "Pressure_hPa": float(pressure),
        "Humidity_pct": float(humidity),
        "SNR_dB": float(snr),
    }

def detect_anomaly(sample: dict) -> tuple[bool, str, str, str]:
    alt = sample["Altitude_m"]
    temp = sample["Temp_C"]
    pres = sample["Pressure_hPa"]
    hum = sample["Humidity_pct"]
    snr = sample["SNR_dB"]

    issues = []

    if temp > 35 or temp < -60:
        issues.append(("Thermal", "Critical", f"Temperature out-of-range: {temp:.1f} °C"))
    elif temp > 32 or temp < -45:
        issues.append(("Thermal", "Moderate", f"Temperature drift: {temp:.1f} °C"))

    if pres < 3 and alt < 1000:
        issues.append(("Pressure Sensor", "Critical", f"Pressure invalid at low altitude: {pres:.1f} hPa"))
    elif pres < 20 and alt < 5000:
        issues.append(("Pressure Sensor", "Moderate", f"Pressure lower than expected: {pres:.1f} hPa"))

    if hum > 95 or hum < 0.5:
        issues.append(("Humidity Sensor", "Moderate", f"Humidity abnormal: {hum:.1f} %"))

    if snr < 8.0:
        issues.append(("Comms Link", "Critical", f"Downlink SNR drop: {snr:.1f} dB"))
    elif snr < 12.0:
        issues.append(("Comms Link", "Moderate", f"Downlink SNR degraded: {snr:.1f} dB"))

    if not issues:
        return False, "", "", ""

    issues_sorted = sorted(issues, key=lambda x: 0 if x[1] == "Critical" else 1)
    subsystem, severity, msg = issues_sorted[0]
    return True, subsystem, severity, msg

# =========================================================
# HERO (LEFT LOGO + RIGHT TITLE LIKE EDGEYENTRA)
# =========================================================
hero_left, hero_right = st.columns([1.1, 2.4], vertical_alignment="center")
with hero_left:
    try:
        st.image("logo.png", width=210)
    except Exception:
        st.markdown('<div class="pill pill-mode">📷 logo.png not found</div>', unsafe_allow_html=True)

with hero_right:
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Interstellar-AI Space Mission Health Console</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">'
        'AI-powered anomaly detection & predictive health monitoring for payload/satellite subsystems — '
        'demo using HAB-style telemetry + Link SNR.'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="mini">'
        'Mission: <b>SVECW HAB / VSAT-01 Demo</b> · Ground Station: <b>SVECW</b> · '
        'Mode: <b>Expo Prototype</b>'
        '</div>',
        unsafe_allow_html=True,
    )

    b1, b2, b3 = st.columns([1.2, 1.1, 1.1])
    with b1:
        if st.button("⏯ Pause / Resume Demo", use_container_width=True):
            st.session_state["running"] = not st.session_state["running"]
    with b2:
        if st.button("🔁 Reset Demo", use_container_width=True):
            st.session_state["tick"] = 0
            st.session_state["history"] = []
            st.session_state["log"] = []
    with b3:
        st.markdown('<div class="pill pill-mode">🧪 DEMO MODE</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# UPDATE / HOLD SAMPLE
# =========================================================
if demo_mode == "Hold last values":
    sample = st.session_state.get("last")
else:
    if st.session_state.get("running", True):
        st.session_state["tick"] = int(st.session_state.get("tick", 0)) + 1
        sample = simulate_telemetry(st.session_state["tick"])
        st.session_state["last"] = sample
    else:
        sample = st.session_state.get("last")

# Link / Phase
snr = sample["SNR_dB"]
link_status = "LOCKED" if snr >= 10 else "DEGRADED" if snr >= 7 else "UNLOCKED"

alt = sample["Altitude_m"]
tick = int(st.session_state.get("tick", 0))
if alt < 500 and tick < 5:
    phase = "PRE-LAUNCH"
elif alt < 500 and tick > 160:
    phase = "RECOVERY"
elif alt >= 29000:
    phase = "PEAK ALTITUDE"
elif tick <= 90:
    phase = "ASCENT"
else:
    phase = "DESCENT"

# Top Metrics
m1, m2, m3, m4 = st.columns([1.1, 1.0, 1.0, 1.2])
with m1: st.metric("Mission Phase", phase)
with m2: st.metric("Downlink SNR", f"{snr:.1f} dB")
with m3: st.metric("Link Status", link_status)
with m4: st.metric("AI Monitor", "ACTIVE" if st.session_state.get("running", True) else "PAUSED")

# =========================================================
# ANOMALY
# =========================================================
is_anom, subsystem, severity, msg = detect_anomaly(sample)

# Optional: inject occasional anomaly for expo
if st.session_state.get("running", True) and np.random.rand() < anomaly_rate:
    forced = np.random.choice(["Thermal", "Comms Link", "Pressure Sensor", "Humidity Sensor"])
    if forced == "Thermal":
        severity = np.random.choice(["Moderate", "Critical"])
        msg = "Thermal drift detected (demo injection)"
    elif forced == "Comms Link":
        severity = np.random.choice(["Moderate", "Critical"])
        msg = "Downlink quality degraded (demo injection)"
    elif forced == "Pressure Sensor":
        severity = "Moderate"
        msg = "Pressure sensor spike (demo injection)"
    else:
        severity = "Moderate"
        msg = "Humidity sensor fluctuation (demo injection)"
    subsystem = forced
    is_anom = True

# Log anomaly once (avoid spamming duplicates)
if is_anom and st.session_state.get("running", True):
    log_list = st.session_state.get("log", [])
    last_msg = log_list[-1]["Message"] if len(log_list) else None
    if last_msg != msg:
        log_list.append({
            "Time": sample["time"],
            "Subsystem": subsystem,
            "Severity": severity,
            "Message": msg,
            "Status": "Anomaly"
        })
        st.session_state["log"] = log_list

# History
hist = st.session_state.get("history", [])
hist.append(sample)
st.session_state["history"] = hist[-max_hist:]

# =========================================================
# STATUS PILL
# =========================================================
st.subheader("🚀 Mission Status")
if is_anom and severity == "Critical":
    st.markdown(f'<div class="pill pill-crit">🔴 CRITICAL · {subsystem} · {msg}</div>', unsafe_allow_html=True)
elif is_anom:
    st.markdown(f'<div class="pill pill-warn">🟡 MODERATE · {subsystem} · {msg}</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="pill pill-ok">🟢 NOMINAL · All telemetry within expected bounds</div>', unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# LIVE TELEMETRY
# =========================================================
st.subheader("📡 Live Telemetry Feed (HAB-style)")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        f"""<div class="card"><div class="card-k">🛰️ Altitude</div>
        <div class="card-v">{sample["Altitude_m"]:.0f}</div><div class="card-u">meters (AGL approx.)</div></div>""",
        unsafe_allow_html=True
    )
with c2:
    st.markdown(
        f"""<div class="card"><div class="card-k">🌡️ Temperature</div>
        <div class="card-v">{sample["Temp_C"]:.1f} °C</div><div class="card-u">payload environment</div></div>""",
        unsafe_allow_html=True
    )
with c3:
    st.markdown(
        f"""<div class="card"><div class="card-k">🧭 Pressure</div>
        <div class="card-v">{sample["Pressure_hPa"]:.1f} hPa</div><div class="card-u">barometric sensor</div></div>""",
        unsafe_allow_html=True
    )
with c4:
    st.markdown(
        f"""<div class="card"><div class="card-k">💧 Humidity</div>
        <div class="card-v">{sample["Humidity_pct"]:.1f} %</div><div class="card-u">relative humidity</div></div>""",
        unsafe_allow_html=True
    )

# Trend
if show_trend:
    st.subheader(f"📈 Recent Telemetry Trend (last {len(st.session_state.get('history', []))} samples)")
    hist_df = pd.DataFrame(st.session_state.get("history", []))
    if len(hist_df) > 1:
        chart_df = hist_df[["Altitude_m", "Temp_C", "Pressure_hPa", "Humidity_pct", "SNR_dB"]].copy()
        st.line_chart(chart_df)
    else:
        st.info("Trend will appear after a few samples...")

# =========================================================
# EVENT LOG (ONLY ONCE)
# =========================================================
st.subheader("📜 Anomaly Event Log")
log_data = st.session_state.get("log", [])
if len(log_data) > 0:
    df_log = pd.DataFrame(log_data)[::-1].reset_index(drop=True)
    st.dataframe(df_log, use_container_width=True, height=280)
else:
    st.info("No anomalies detected yet (or demo is paused).")

# =========================================================
# AUTO REFRESH (CLOUD SAFE)
# =========================================================
if st.session_state.get("running", True) and demo_mode != "Hold last values":
    time.sleep(refresh_s)
    st.rerun()
