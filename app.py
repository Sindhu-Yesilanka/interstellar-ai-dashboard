# app.py — Interstellar-AI Space Mission Health Console (Cloud-safe)
# ✅ No st.autorefresh
# ✅ No infinite while True loop
# ✅ Uses time.sleep + st.rerun (works on Streamlit Cloud)
# ✅ Space theme + floating stars
# ✅ Single Event Log (no duplicate)
# ✅ Clean hero like EdgeYentra style (logo left, title/subtitle right)
# ✅ Fixes deprecated use_column_width -> use_container_width

import streamlit as st
import pandas as pd
import numpy as np
import random
import time
from datetime import datetime

# =========================================================
# SETTINGS
# =========================================================
REFRESH_SECONDS = 2          # auto update speed
HISTORY_LEN = 40             # last N samples in chart
ANOMALY_PROB = 0.12          # chance per tick (demo)

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Interstellar-AI | Space Mission Console",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# CSS — STARFIELD + CONSOLE THEME
# (No external star image dependency)
# =========================================================
st.markdown("""
<style>
/* Full app background */
.stApp {
    background: radial-gradient(circle at 30% 10%, #06163a 0%, #020615 40%, #000 100%);
}

/* Remove extra top padding */
.block-container { padding-top: 1.25rem; }

/* Star layers using CSS radial gradients */
@keyframes drift {
  from { transform: translateY(0px); }
  to   { transform: translateY(-1200px); }
}

.starfield, .starfield2, .starfield3 {
  position: fixed;
  inset: -100% -100% -100% -100%;
  z-index: -1;
  background-repeat: repeat;
  opacity: 0.8;
}

.starfield {
  background-image:
    radial-gradient(1px 1px at 20px 30px, rgba(255,255,255,.9) 50%, transparent 60%),
    radial-gradient(1px 1px at 160px 80px, rgba(255,255,255,.8) 50%, transparent 60%),
    radial-gradient(1px 1px at 320px 140px, rgba(255,255,255,.7) 50%, transparent 60%),
    radial-gradient(1px 1px at 520px 260px, rgba(255,255,255,.7) 50%, transparent 60%),
    radial-gradient(1px 1px at 740px 380px, rgba(255,255,255,.8) 50%, transparent 60%);
  background-size: 900px 500px;
  animation: drift 180s linear infinite;
}

.starfield2 {
  opacity: 0.5;
  background-image:
    radial-gradient(1px 1px at 60px 40px, rgba(160,220,255,.8) 50%, transparent 60%),
    radial-gradient(1px 1px at 220px 120px, rgba(255,255,255,.6) 50%, transparent 60%),
    radial-gradient(1px 1px at 480px 220px, rgba(255,255,255,.6) 50%, transparent 60%),
    radial-gradient(1px 1px at 680px 340px, rgba(255,255,255,.7) 50%, transparent 60%);
  background-size: 800px 450px;
  animation: drift 260s linear infinite;
}

.starfield3 {
  opacity: 0.25;
  background-image:
    radial-gradient(2px 2px at 120px 90px, rgba(255,210,120,.6) 50%, transparent 60%),
    radial-gradient(2px 2px at 360px 210px, rgba(255,255,255,.5) 50%, transparent 60%),
    radial-gradient(2px 2px at 620px 330px, rgba(255,255,255,.5) 50%, transparent 60%);
  background-size: 900px 550px;
  animation: drift 340s linear infinite;
}

/* Hero container (EdgeYentra style) */
.hero-wrap{
  padding: 26px 26px;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(9,18,48,.65), rgba(0,0,0,.65));
  border: 1px solid rgba(80,160,255,.18);
  box-shadow: 0 0 26px rgba(0,160,255,.12);
  margin-bottom: 18px;
}

.hero-grid{
  display:flex;
  gap: 22px;
  align-items:center;
}

.hero-logo{
  width: 140px;
  height: 140px;
  border-radius: 16px;
  background: rgba(0,0,0,.35);
  border: 1px solid rgba(255,255,255,.08);
  box-shadow: 0 0 22px rgba(0,160,255,.10);
  display:flex;
  align-items:center;
  justify-content:center;
  overflow:hidden;
  flex: 0 0 140px;
}

.hero-title{
  font-size: 40px;
  line-height: 1.1;
  font-weight: 900;
  color: #ffffff;
  text-shadow: 0 0 18px rgba(0,180,255,.45);
  margin-bottom: 8px;
}

.hero-subtitle{
  font-size: 16px;
  color: #cfe8ff;
  margin-bottom: 14px;
  max-width: 900px;
}

.badge-row{
  display:flex;
  gap: 10px;
  flex-wrap: wrap;
}

.badge{
  display:inline-flex;
  align-items:center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid rgba(255,255,255,.14);
  background: rgba(2,6,23,.55);
  color: #e5e7eb;
}

.badge-green{ border-color: rgba(45,180,92,.45); background: rgba(23,58,34,.55); color:#7CFFB0; }
.badge-blue{ border-color: rgba(59,130,246,.45); background: rgba(7,25,55,.55); color:#BFD8FF; }

/* Cards */
.card{
  padding: 16px 18px;
  border-radius: 18px;
  background: rgba(3,11,24,.75);
  border: 1px solid rgba(18,51,89,.95);
  box-shadow: 0 0 22px rgba(4,189,255,.10);
}

.metric-big{
  font-size: 30px;
  font-weight: 900;
  color: white;
  margin-top: 4px;
}

.mini-label{
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 2px;
}

.status-pill{
  width: 100%;
  padding: 12px 14px;
  border-radius: 999px;
  font-weight: 900;
  text-align:center;
  letter-spacing: .3px;
  border: 1px solid rgba(255,255,255,.12);
  margin-top: 6px;
  margin-bottom: 8px;
}

.nominal{ background: rgba(23,58,34,.80); border-color: rgba(45,180,92,.50); color:#7CFFB0; }
.warn{ background: rgba(51,39,12,.80); border-color: rgba(255,178,0,.55); color:#FFD65C; }
.crit{ background: rgba(58,10,10,.80); border-color: rgba(255,64,64,.65); color:#FF8A8A; }

.alertbox{
  padding: 14px 16px;
  border-radius: 16px;
  border: 1px solid rgba(255,64,64,.65);
  background: rgba(40,10,10,.75);
  box-shadow: 0 0 18px rgba(255,64,64,.10);
  margin-top: 10px;
}

.small-note{
  color:#9ca3af;
  font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

# Starfield layers
st.markdown('<div class="starfield"></div><div class="starfield2"></div><div class="starfield3"></div>',
            unsafe_allow_html=True)

# =========================================================
# SESSION STATE INIT
# =========================================================
if "log" not in st.session_state:
    st.session_state.log = []

if "history" not in st.session_state:
    st.session_state.history = []

if "running" not in st.session_state:
    st.session_state.running = True

if "last_values" not in st.session_state:
    st.session_state.last_values = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "Vbus": 50.0,
        "Temp": 75.0,
        "Wheel": 30.0
    }

# =========================================================
# HERO (EdgeYentra-style)
# =========================================================
st.markdown('<div class="hero-wrap"><div class="hero-grid">', unsafe_allow_html=True)

# Left: logo
st.markdown('<div class="hero-logo">', unsafe_allow_html=True)
# Put your file in repo: logo.png
try:
    st.image("logo.png", width=140)
except Exception:
    st.markdown("<div class='small-note'>logo.png not found</div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Right: title/subtitle/badges
st.markdown("""
<div>
  <div class="hero-title">Interstellar-AI Space Mission Health Console</div>
  <div class="hero-subtitle">
    AI-powered anomaly detection and predictive health monitoring for critical satellite subsystems — enabling faster,
    safer, and more autonomous missions.
  </div>
  <div class="badge-row">
    <div class="badge badge-blue">🛰️ Telemetry Console</div>
    <div class="badge badge-green">🧠 AI Monitor ACTIVE</div>
    <div class="badge">🧪 Demo Mode (Simulated Stream)</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

# =========================================================
# TOP INFO + CONTROLS
# =========================================================
info_left, info_mid, info_right = st.columns([1.3, 1, 1])

with info_left:
    st.markdown(
        "<div class='small-note'>"
        "Mission: <b>VSAT-01</b> · Orbit: <b>LEO 500 km</b> · Ground Station: <b>SVECW</b><br>"
        "Platform: <b>Interstellar-AI</b> — Autonomous anomaly detection (demo telemetry)"
        "</div>",
        unsafe_allow_html=True
    )
    if st.button("⏯ Pause / Resume Demo"):
        st.session_state.running = not st.session_state.running

with info_mid:
    snr = 17.0 + np.random.randn() * 0.6
    st.markdown("<div class='mini-label'>Downlink SNR</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-big'>{snr:.1f} dB</div>", unsafe_allow_html=True)

with info_right:
    st.markdown("<div class='mini-label'>Link Status</div>", unsafe_allow_html=True)
    st.markdown("<div class='metric-big'>LOCKED</div>", unsafe_allow_html=True)
    st.markdown("<div class='mini-label' style='margin-top:10px;'>AI Monitor</div>", unsafe_allow_html=True)
    st.markdown("<div class='metric-big'>ACTIVE</div>", unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# TELEMETRY UPDATE OR HOLD
# =========================================================
if st.session_state.running:
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Demo telemetry (you can map to HAB payload values later)
    ch1 = np.random.normal(50, 1.0)   # Vbus
    ch2 = np.random.normal(75, 1.2)   # Temp
    ch3 = np.random.normal(30, 1.0)   # Wheel

    st.session_state.last_values = {"time": timestamp, "Vbus": float(ch1), "Temp": float(ch2), "Wheel": float(ch3)}
    st.session_state.history.append(st.session_state.last_values)
    st.session_state.history = st.session_state.history[-HISTORY_LEN:]
else:
    vals = st.session_state.last_values
    timestamp = vals["time"]
    ch1, ch2, ch3 = vals["Vbus"], vals["Temp"], vals["Wheel"]

# =========================================================
# SIMPLE ANOMALY LOGIC (DEMO)
# =========================================================
anomaly = False
severity = None
subsystem = None
message = None

if st.session_state.running and random.random() < ANOMALY_PROB:
    anomaly = True
    subsystem = random.choice(["Power Bus", "Thermal Control", "Reaction Wheel"])
    severity = random.choice(["Moderate", "Critical"])
    message = f"{subsystem} anomaly detected"

    st.session_state.log.append({
        "Time": timestamp,
        "Subsystem": subsystem,
        "Severity": severity,
        "Status": "Anomaly"
    })
    st.session_state.log = st.session_state.log[-200:]  # keep last 200

# =========================================================
# MISSION STATUS
# =========================================================
st.subheader("🚀 Mission Status")

if anomaly and severity == "Critical":
    st.markdown('<div class="status-pill crit">🔴 EMERGENCY MODE · CRITICAL ANOMALY</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="alertbox">🚨 <b>{message}</b> — Severity: <b>CRITICAL</b></div>',
                unsafe_allow_html=True)
elif anomaly:
    st.markdown('<div class="status-pill warn">🟡 DEGRADED MODE · ANOMALY UNDER INVESTIGATION</div>',
                unsafe_allow_html=True)
    st.markdown(
        f'<div class="alertbox" style="border-color:rgba(255,178,0,.7);background:rgba(51,39,12,.75);">'
        f'⚠️ <b>{message}</b> — Severity: <b>MODERATE</b></div>',
        unsafe_allow_html=True
    )
else:
    st.markdown('<div class="status-pill nominal">🟢 NOMINAL MODE · ALL SUBSYSTEMS HEALTHY</div>',
                unsafe_allow_html=True)

# =========================================================
# LIVE TELEMETRY CARDS
# =========================================================
st.subheader("📡 Live Telemetry Feed")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        f"""
        <div class="card">
          <div class="mini-label">🔌 Power Bus Voltage</div>
          <div class="metric-big">{ch1:.2f} V</div>
          <div class="small-note">Last update: {timestamp}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        f"""
        <div class="card">
          <div class="mini-label">🌡 Battery Temperature</div>
          <div class="metric-big">{ch2:.2f} °C</div>
          <div class="small-note">Thermal safety indicator</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        f"""
        <div class="card">
          <div class="mini-label">🌀 Reaction Wheel Speed</div>
          <div class="metric-big">{ch3:.2f} rpm</div>
          <div class="small-note">Attitude control health</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# TREND CHART
# =========================================================
st.subheader(f"📈 Recent Telemetry Trend (last {HISTORY_LEN} samples)")
if len(st.session_state.history) > 1:
    hist_df = pd.DataFrame(st.session_state.history).set_index("time")
    # Better labels for chart
    hist_df = hist_df.rename(columns={"Vbus": "Power Bus (V)", "Temp": "Battery Temp (°C)", "Wheel": "Wheel (rpm)"})
    st.line_chart(hist_df, height=260, use_container_width=True)
else:
    st.info("Trend will appear as telemetry accumulates...")

# =========================================================
# EVENT LOG (ONLY ONCE — fixes “why 2 times”)
# =========================================================
st.subheader("📜 Anomaly Event Log")
if len(st.session_state.log) > 0:
    df_log = pd.DataFrame(st.session_state.log)
    st.dataframe(df_log.iloc[::-1], use_container_width=True, height=280)
else:
    st.info("No anomalies detected yet.")

# =========================================================
# AUTO REFRESH (Cloud-safe)
# =========================================================
time.sleep(REFRESH_SECONDS)
st.rerun()
