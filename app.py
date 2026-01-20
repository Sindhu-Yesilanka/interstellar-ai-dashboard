import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import base64
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Interstellar-AI | Space Mission Console",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# CSS — STARFIELD + HERO + CONSOLE THEME
# =========================================================
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #030b25, #000000); }

@keyframes moveStars { from {transform: translateY(0px);} to {transform: translateY(-1000px);} }
.stars, .stars2, .stars3 {
  position: fixed; top:0; left:0; width:200%; height:200%;
  z-index:-1; background: transparent url("https://i.ibb.co/7WZRJgC/stars.png") repeat top center;
}
.stars  { animation: moveStars 120s linear infinite; opacity: 0.9; }
.stars2 { animation: moveStars 240s linear infinite; opacity: 0.5; }
.stars3 { animation: moveStars 360s linear infinite; opacity: 0.25; }

.hero {
  background: radial-gradient(circle at top, #0b1a3a, #000000);
  padding: 38px 28px 32px 28px;
  border-radius: 16px;
  box-shadow: 0 0 26px rgba(0,178,255,0.25);
  margin-bottom: 18px;
}
.hero-inner {
  max-width: 1100px; margin: 0 auto;
  display:flex; gap:28px; align-items:center; justify-content:center; flex-wrap:wrap;
}
.hero-logo { width: 160px; max-width: 40vw; border-radius: 10px; }
.hero-text { max-width: 700px; text-align: left; }
.hero-title {
  font-size: 34px; color:white; font-weight: 900; line-height: 1.2;
  text-shadow: 0 0 22px rgba(0,200,255,0.7);
}
.hero-subtitle { margin-top: 10px; font-size: 16px; color: #dbeafe; }

.badges { margin-top: 14px; display:flex; gap:10px; flex-wrap:wrap; }
.badge {
  padding: 7px 14px; border-radius: 999px; font-size: 13px; font-weight: 700;
  background: rgba(15,23,42,0.9); color: #e5e7eb; border:1px solid #4b5563;
}
.badge.primary { background: linear-gradient(90deg,#6366f1,#3b82f6); border: none; color: white; box-shadow: 0 0 16px rgba(99,102,241,0.6); }

.subtitle-line { color: #9ca3af; font-size: 14px; margin-bottom: 0.9rem; }

.tag {
  padding: 6px 14px; border-radius: 999px; font-weight: 800; font-size: 13px; display:inline-block;
}
.normal { background:#173a22; color:#6bff9c; border:1px solid #2db45c;}
.warn   { background:#33270c; color:#ffd65c; border:1px solid #ffb200;}
.crit   { background:#3a0a0a; color:#ff8080; border:1px solid #ff2222;}
.mode   { background:#020617; color:#e5e7eb; border:1px solid #4b5563;}

.telemetry-box {
  padding:18px; border-radius:18px;
  background:#030b18; border:1px solid #123359;
  box-shadow: 0 0 22px rgba(4,189,255,.14);
  min-height: 110px;
}
.alert-box {
  padding:18px; border-radius:18px;
  background:#2b0b0b; border:1px solid #ff4040;
  margin-bottom: 0.8rem;
}
</style>
""", unsafe_allow_html=True)

# Starfield layers
st.markdown("""
<div class="stars"></div>
<div class="stars2"></div>
<div class="stars3"></div>
""", unsafe_allow_html=True)

# =========================================================
# HERO (single HTML block with embedded logo)
# =========================================================
def get_logo_base64(path="logo.png"):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return None

logo_b64 = get_logo_base64()
logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="hero-logo"/>' if logo_b64 else ""

st.markdown(f"""
<div class="hero">
  <div class="hero-inner">
    {logo_html}
    <div class="hero-text">
      <div class="hero-title">Interstellar-AI Space Mission Health Console</div>
      <div class="hero-subtitle">
        AI-powered anomaly detection and predictive health monitoring for satellite and payload telemetry —
        enabling faster, safer and autonomous missions.
      </div>
      <div class="badges">
        <span class="badge primary">Live Demo Dashboard</span>
        <span class="badge">AI Overlay Monitoring</span>
        <span class="badge">Ground-Station Console</span>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE
# =========================================================
if "log" not in st.session_state:
    st.session_state.log = []
if "history" not in st.session_state:
    st.session_state.history = []
if "running" not in st.session_state:
    st.session_state.running = True
if "force_fault" not in st.session_state:
    st.session_state.force_fault = False

# =========================================================
# TOP BAR
# =========================================================
st.markdown(
    '<div class="subtitle-line">'
    'Mission: <b>VSAT-01</b> · Orbit: <b>LEO 500 km</b> · Ground Station: <b>SVECW</b><br>'
    'Prototype: <b>Raspberry Pi + Payload Hardware</b> · Demo: <b>Simulated telemetry (replaceable with live UART/I2C)</b>'
    '</div>',
    unsafe_allow_html=True
)

cA, cB, cC, cD = st.columns([1.35, 1.0, 1.0, 1.0])

with cA:
    mode = st.selectbox("Mode", ["🧪 Demo Mode (Simulated Telemetry)", "🔌 Payload Mode (Coming Soon)"])
    if st.button("⏯ Pause / Resume"):
        st.session_state.running = not st.session_state.running
    if st.button("⚡ Trigger Fault (Demo)"):
        st.session_state.force_fault = True

with cB:
    st.metric("Link Status", "LOCKED")

with cC:
    st.metric("AI Monitor", "ACTIVE")

with cD:
    refresh_s = st.slider("Refresh (seconds)", min_value=1, max_value=5, value=2)

st.markdown("---")

# =========================================================
# TELEMETRY SIMULATOR (realistic drift + noise)
# =========================================================
def simulated_payload_telemetry(t, inject_fault=False):
    # Smooth signals (looks real)
    vbat = 12.2 + 0.18*np.sin(t/18) + np.random.normal(0, 0.03)
    temp = 32.0 + 1.8*np.sin(t/22) + np.random.normal(0, 0.20)
    wheel = 3100 + 60*np.sin(t/14) + np.random.normal(0, 10)
    snr = 16.5 + 0.6*np.sin(t/20) + np.random.normal(0, 0.18)

    anomaly = False
    subsystem = None
    severity = None

    # Auto anomaly occasionally (only when running)
    if random.random() < 0.08:
        anomaly = True
        subsystem = random.choice(["Power Bus", "Thermal Control", "Reaction Wheel", "RF Link"])
        severity = random.choice(["Moderate", "Critical"])

    # Manual fault trigger (for jury demo)
    if inject_fault:
        anomaly = True
        subsystem = random.choice(["Power Bus", "Thermal Control", "Reaction Wheel"])
        severity = "Critical"

    # Apply fault effects
    if anomaly:
        if subsystem == "Power Bus":
            vbat -= random.choice([0.7, 1.1])  # drop
        elif subsystem == "Thermal Control":
            temp += random.choice([6, 10])     # spike
        elif subsystem == "Reaction Wheel":
            wheel += random.choice([350, 600]) # surge
        elif subsystem == "RF Link":
            snr -= random.choice([2.5, 4.0])   # degrade

    return {
        "time": datetime.now().strftime("%H:%M:%S"),
        "VBAT": float(vbat),
        "TEMP": float(temp),
        "WHEEL": float(wheel),
        "SNR": float(snr),
        "anomaly": anomaly,
        "subsystem": subsystem,
        "severity": severity
    }

# =========================================================
# LIVE AREA
# =========================================================
placeholder = st.empty()
tick = 0

while True:
    with placeholder.container():

        # Telemetry generation only if running
        if st.session_state.running:
            inject = st.session_state.force_fault
            tele = simulated_payload_telemetry(tick, inject_fault=inject)
            st.session_state.force_fault = False
            tick += 1
        else:
            # when paused, keep last values if available
            if len(st.session_state.history) > 0:
                tele = st.session_state.history[-1].copy()
                tele["anomaly"] = False
                tele["subsystem"] = None
                tele["severity"] = None
            else:
                tele = simulated_payload_telemetry(tick, inject_fault=False)

        # If payload mode, show note (still simulated for expo)
        if "Payload Mode" in mode:
            st.info("Payload Mode selected. For expo demo, telemetry is simulated. In real use, replace this with UART/I2C read from payload.")

        # Save history (for trend)
        st.session_state.history.append({
            "time": tele["time"],
            "VBAT": tele["VBAT"],
            "TEMP": tele["TEMP"],
            "WHEEL": tele["WHEEL"],
            "SNR": tele["SNR"],
        })
        st.session_state.history = st.session_state.history[-30:]

        # Event log
        if tele["anomaly"] and st.session_state.running:
            st.session_state.log.append({
                "Time": tele["time"],
                "Subsystem": tele["subsystem"],
                "Severity": tele["severity"],
                "Status": "Anomaly"
            })
            st.session_state.log = st.session_state.log[-80:]

        # ================= STATUS =================
        st.subheader("🚀 Mission Status")

        if tele["anomaly"] and tele["severity"] == "Critical":
            st.markdown(
                f'<div class="alert-box">🚨 <b>{tele["subsystem"]} anomaly detected</b> — Severity: 🔴 <b>CRITICAL</b></div>',
                unsafe_allow_html=True
            )
            st.markdown('<div class="tag crit">EMERGENCY MODE: CRITICAL ANOMALY</div>', unsafe_allow_html=True)

        elif tele["anomaly"]:
            st.markdown(
                f'<div class="alert-box" style="border-color:#ffc441;background:#33270c;">'
                f'⚠️ <b>{tele["subsystem"]} anomaly detected</b> — Severity: 🟡 <b>MODERATE</b></div>',
                unsafe_allow_html=True
            )
            st.markdown('<div class="tag warn">DEGRADED MODE: ANOMALY UNDER INVESTIGATION</div>', unsafe_allow_html=True)

        else:
            st.markdown('<div class="tag normal">🟢 NOMINAL MODE: ALL SUBSYSTEMS HEALTHY</div>', unsafe_allow_html=True)

        # ================= TELEMETRY =================
        st.subheader("📡 Live Telemetry Feed")

        t1, t2, t3, t4 = st.columns(4)

        with t1:
            st.markdown(
                '<div class="telemetry-box">🔋 <b>Battery Voltage</b><br><br>'
                f'<span style="font-size:30px;">{tele["VBAT"]:.2f} V</span></div>',
                unsafe_allow_html=True
            )

        with t2:
            st.markdown(
                '<div class="telemetry-box">🌡 <b>Payload Temperature</b><br><br>'
                f'<span style="font-size:30px;">{tele["TEMP"]:.2f} °C</span></div>',
                unsafe_allow_html=True
            )

        with t3:
            st.markdown(
                '<div class="telemetry-box">🌀 <b>Reaction Wheel Speed</b><br><br>'
                f'<span style="font-size:30px;">{tele["WHEEL"]:.0f} rpm</span></div>',
                unsafe_allow_html=True
            )

        with t4:
            st.markdown(
                '<div class="telemetry-box">📶 <b>Downlink SNR</b><br><br>'
                f'<span style="font-size:30px;">{tele["SNR"]:.1f} dB</span></div>',
                unsafe_allow_html=True
            )

        # ================= TREND =================
        st.subheader("📈 Recent Telemetry Trend (last 30 samples)")
        hist_df = pd.DataFrame(st.session_state.history)
        st.line_chart(hist_df.set_index("time"))

        # ================= EVENT LOG =================
        st.subheader("📜 Anomaly Event Log")
        if len(st.session_state.log) > 0:
            df_log = pd.DataFrame(st.session_state.log)
            st.dataframe(df_log[::-1], use_container_width=True, height=260)
        else:
            st.info("No anomalies detected yet.")

        time.sleep(refresh_s)
