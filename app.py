import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Interstellar-AI | Space Mission Console",
    page_icon="🚀",
    layout="wide",
)

# =========================================================
# CSS — SPACE THEME + FLOATING STARS + EDGEYENTRA-STYLE HERO
# =========================================================
st.markdown(
    """
<style>
/* ---- App Background ---- */
.stApp {
    background: radial-gradient(1200px 700px at 50% -10%, #0c1f52 0%, #050915 45%, #000 100%);
    color: #e5e7eb;
}

/* Hide Streamlit default header spacing (removes that blank bar look) */
header[data-testid="stHeader"] {visibility: hidden; height: 0px;}
div.block-container {padding-top: 1.2rem; padding-bottom: 2.2rem;}

/* ---- Floating Stars (Pure CSS, no external image) ---- */
@keyframes starFloat {
  0%   {transform: translateY(0px);}
  100% {transform: translateY(-1200px);}
}

.stars, .stars2, .stars3 {
  position: fixed;
  top: 0; left: 0;
  width: 200%;
  height: 200%;
  z-index: -10;
  background-repeat: repeat;
  opacity: 0.7;
}

.stars {
  background-image:
    radial-gradient(2px 2px at 20px 30px, #ffffffaa 50%, transparent 51%),
    radial-gradient(1px 1px at 100px 150px, #ffffff66 50%, transparent 51%),
    radial-gradient(2px 2px at 300px 220px, #ffffff88 50%, transparent 51%),
    radial-gradient(1px 1px at 400px 90px, #ffffff55 50%, transparent 51%),
    radial-gradient(2px 2px at 520px 310px, #ffffffaa 50%, transparent 51%),
    radial-gradient(1px 1px at 650px 170px, #ffffff66 50%, transparent 51%),
    radial-gradient(2px 2px at 780px 260px, #ffffff99 50%, transparent 51%);
  animation: starFloat 140s linear infinite;
}

.stars2 {
  opacity: 0.45;
  background-image:
    radial-gradient(1px 1px at 40px 60px, #ffffff66 50%, transparent 51%),
    radial-gradient(2px 2px at 220px 120px, #ffffff88 50%, transparent 51%),
    radial-gradient(1px 1px at 360px 240px, #ffffff55 50%, transparent 51%),
    radial-gradient(2px 2px at 560px 80px,  #ffffff99 50%, transparent 51%),
    radial-gradient(1px 1px at 740px 300px, #ffffff66 50%, transparent 51%);
  animation: starFloat 220s linear infinite;
}

.stars3 {
  opacity: 0.25;
  background-image:
    radial-gradient(1px 1px at 90px 100px, #ffffff55 50%, transparent 51%),
    radial-gradient(1px 1px at 280px 200px, #ffffff44 50%, transparent 51%),
    radial-gradient(1px 1px at 470px 140px, #ffffff55 50%, transparent 51%),
    radial-gradient(1px 1px at 690px 260px, #ffffff44 50%, transparent 51%);
  animation: starFloat 320s linear infinite;
}

/* ---- Glass Panels ---- */
.panel {
  background: rgba(6, 10, 25, 0.55);
  border: 1px solid rgba(90, 170, 255, 0.20);
  box-shadow: 0 0 28px rgba(0, 178, 255, 0.12);
  border-radius: 18px;
  padding: 18px 18px;
}

/* ---- HERO (EdgeYentra-like) ---- */
.hero-wrap {
  padding: 22px 18px;
  border-radius: 22px;
  background: linear-gradient(135deg, rgba(12,31,82,0.55), rgba(0,0,0,0.35));
  border: 1px solid rgba(120, 200, 255, 0.18);
  box-shadow: 0 0 38px rgba(0, 178, 255, 0.16);
}

.hero-title {
  font-size: 44px;
  font-weight: 900;
  line-height: 1.05;
  color: #f8fafc;
  text-shadow: 0 0 26px rgba(0, 200, 255, 0.35);
}

.hero-sub {
  margin-top: 10px;
  font-size: 16px;
  color: #cfe6ff;
  max-width: 780px;
}

.hero-pill {
  display: inline-block;
  margin-top: 10px;
  padding: 6px 12px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 12px;
  color: #bfe8ff;
  background: rgba(0, 120, 255, 0.18);
  border: 1px solid rgba(0, 160, 255, 0.28);
}

/* ---- Tags ---- */
.tag {
  padding: 7px 14px;
  border-radius: 999px;
  font-weight: 800;
  font-size: 13px;
  display: inline-block;
  border: 1px solid transparent;
}

.normal { background:#123821; color:#6bff9c; border-color:#2db45c;}
.warn   { background:#33270c; color:#ffd65c; border-color:#ffb200;}
.crit   { background:#3a0a0a; color:#ff8080; border-color:#ff2222;}
.mode   { background:#020617; color:#e5e7eb; border-color:#4b5563;}

/* ---- Telemetry Cards ---- */
.telemetry {
  padding: 18px;
  border-radius: 18px;
  background: rgba(2, 6, 23, 0.55);
  border: 1px solid rgba(0, 190, 255, 0.22);
  box-shadow: 0 0 22px rgba(0, 178, 255, 0.10);
  min-height: 110px;
}

.telemetry .label { color: #bfe8ff; font-weight: 800; }
.telemetry .value { font-size: 34px; font-weight: 900; color: #ffffff; margin-top: 8px; }

/* Make charts/dataframes blend */
[data-testid="stDataFrame"] {border-radius: 14px; overflow: hidden;}
</style>

<div class="stars"></div><div class="stars2"></div><div class="stars3"></div>
""",
    unsafe_allow_html=True,
)

# =========================================================
# SESSION STATE
# =========================================================
if "running" not in st.session_state:
    st.session_state.running = True

if "history" not in st.session_state:
    st.session_state.history = []

if "log" not in st.session_state:
    st.session_state.log = []

if "last_values" not in st.session_state:
    st.session_state.last_values = {"time": datetime.now().strftime("%H:%M:%S"), "Vbus": 50.0, "Temp": 28.0, "Wheel": 30.0}

# =========================================================
# SIDEBAR CONTROLS (Showcase friendly)
# =========================================================
st.sidebar.title("⚙️ Demo Controls")
st.sidebar.caption("Use these controls during expo to show anomalies.")

st.session_state.running = st.sidebar.toggle("Run Live Demo", value=st.session_state.running)
refresh_ms = st.sidebar.slider("Refresh speed (ms)", 300, 3000, 900, 100)

anomaly_prob = st.sidebar.slider("Anomaly probability", 0.00, 0.40, 0.12, 0.01)
force_anomaly = st.sidebar.button("🚨 Force Anomaly Now")

st.sidebar.markdown("---")
st.sidebar.caption("If Raspberry Pi payload is connected later, replace simulated values with sensor reads.")

# Auto refresh (NO while True)
st_autorefresh = st.experimental_data_editor if False else None  # dummy to keep lint calm
count = st.autorefresh(interval=refresh_ms, key="autorefresh")

# =========================================================
# HERO SECTION (Edgeyentra style)
# =========================================================
left, right = st.columns([0.22, 0.78], vertical_alignment="center")

with left:
    # Fit logo neatly (avoid huge image)
    st.image("logo.png", width=220)

with right:
    st.markdown('<div class="hero-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Interstellar-AI Space Mission Health Console</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-sub">AI-powered anomaly detection & predictive health monitoring for satellite / HAB payload subsystems — enabling faster, safer, and more autonomous missions.</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<span class="hero-pill">🧪 DEMO MODE • Simulated telemetry mapped to HAB-like ranges</span>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("")
st.markdown(
    '<div style="color:#9ca3af;font-size:13px;">'
    'Mission: <b>VSAT-01</b> · Orbit: <b>LEO 500 km</b> · Ground Station: <b>SVECW</b> '
    '· Platform: <b>Interstellar-AI</b>'
    "</div>",
    unsafe_allow_html=True,
)
st.markdown("")

# =========================================================
# TOP KPIs
# =========================================================
k1, k2, k3, k4 = st.columns([1.2, 1, 1, 1])

with k1:
    st.markdown('<div class="tag mode">🧪 DEMO MODE (Simulated Telemetry)</div>', unsafe_allow_html=True)

with k2:
    snr = 17.0 + np.random.randn() * 0.6
    st.metric("Downlink SNR", f"{snr:.1f} dB")

with k3:
    st.metric("Link Status", "LOCKED")

with k4:
    st.metric("AI Monitor", "ACTIVE")

st.markdown("")

# =========================================================
# TELEMETRY UPDATE (Simulated)
# =========================================================
vals = st.session_state.last_values.copy()

if st.session_state.running:
    timestamp = datetime.now().strftime("%H:%M:%S")

    # “HAB-like” ranges (safe for demo): you can tune
    # Voltage stable around 50V
    Vbus = float(np.random.normal(50.0, 0.8))
    # Temp around 25–35 baseline; occasional spikes
    Temp = float(np.random.normal(28.0, 1.0))
    # Wheel around 30 rpm
    Wheel = float(np.random.normal(30.0, 0.9))

    vals = {"time": timestamp, "Vbus": Vbus, "Temp": Temp, "Wheel": Wheel}
    st.session_state.last_values = vals
    st.session_state.history.append(vals)
    st.session_state.history = st.session_state.history[-40:]  # keep last N points

# =========================================================
# ANOMALY LOGIC (Demo)
# =========================================================
anomaly = False
severity = None
faulty = None

if st.session_state.running:
    if force_anomaly or (random.random() < anomaly_prob):
        anomaly = True
        faulty = random.choice(["Power Bus", "Thermal Control", "Reaction Wheel", "Comms Link"])
        severity = random.choice(["Moderate", "Critical"])

        st.session_state.log.append(
            {"Time": vals["time"], "Subsystem": faulty, "Severity": severity, "Status": "Anomaly"}
        )
        st.session_state.log = st.session_state.log[-100:]  # cap log size

# =========================================================
# MISSION STATUS
# =========================================================
st.subheader("🚀 Mission Status")

if anomaly and severity == "Critical":
    st.markdown('<div class="tag crit">🔴 EMERGENCY MODE: CRITICAL ANOMALY</div>', unsafe_allow_html=True)
elif anomaly:
    st.markdown('<div class="tag warn">🟡 DEGRADED MODE: ANOMALY UNDER INVESTIGATION</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="tag normal">🟢 NOMINAL MODE: ALL SUBSYSTEMS HEALTHY</div>', unsafe_allow_html=True)

st.markdown("")

# =========================================================
# LIVE TELEMETRY CARDS
# =========================================================
st.subheader("📡 Live Telemetry Feed")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        f"""
        <div class="telemetry">
          <div class="label">🔌 Power Bus Voltage</div>
          <div class="value">{vals["Vbus"]:.2f} V</div>
          <div style="color:#94a3b8;font-size:12px;">Nominal window: 48–52 V</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""
        <div class="telemetry">
          <div class="label">🌡 Battery / Payload Temperature</div>
          <div class="value">{vals["Temp"]:.2f} °C</div>
          <div style="color:#94a3b8;font-size:12px;">Nominal window: 20–40 °C</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f"""
        <div class="telemetry">
          <div class="label">🌀 Reaction Wheel Speed</div>
          <div class="value">{vals["Wheel"]:.2f} rpm</div>
          <div style="color:#94a3b8;font-size:12px;">Nominal window: 25–35 rpm</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("")

# =========================================================
# TREND CHART
# =========================================================
st.subheader("📈 Recent Telemetry Trend (last samples)")

if len(st.session_state.history) > 2:
    hist_df = pd.DataFrame(st.session_state.history)
    hist_df = hist_df.set_index("time")
    st.line_chart(hist_df, height=260, use_container_width=True)
else:
    st.info("Trend will appear as telemetry accumulates...")

st.markdown("")

# =========================================================
# EVENT LOG (ONLY ONCE)
# =========================================================
st.subheader("📜 Anomaly Event Log")

if len(st.session_state.log) > 0:
    df_log = pd.DataFrame(st.session_state.log)[::-1]
    st.dataframe(df_log, use_container_width=True, height=280)
else:
    st.info("No anomalies detected yet. Use 'Force Anomaly Now' from sidebar for demo.")
