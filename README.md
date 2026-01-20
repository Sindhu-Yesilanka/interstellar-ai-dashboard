# 🚀 Interstellar-AI Dashboard

An AI-powered **Space Mission Health Monitoring Console** for detecting anomalies in satellite / HAB payload telemetry.

This project demonstrates how onboard telemetry data can be monitored, analyzed, and visualized in real time using **AI models deployed at the edge**.

---

## 🔍 Problem

Space missions and high-altitude experiments generate continuous telemetry data.
Manual monitoring is error-prone and delayed, leading to:
- Missed anomalies
- Late responses
- Increased mission risk

---

## 💡 Solution

**Interstellar-AI** provides:
- Real-time telemetry visualization
- AI-based anomaly detection
- Predictive subsystem health monitoring
- Edge-deployable architecture (Raspberry Pi / payload computer)

---

## 📡 Telemetry Parameters (Demo)

| Parameter | Description |
|---------|------------|
| Power Bus Voltage | Power subsystem health |
| Temperature | Payload / battery thermal safety |
| Reaction Wheel Speed | Attitude control stability |
| Link SNR | Communication link quality |

> In this demo, values are simulated to match real HAB / satellite ranges.

---

## 🧪 Demo Mode

- Dashboard uses **synthetic telemetry**
- Anomalies are injected intentionally
- Designed for **project expo / prototype showcase**
- Can later be connected to real payload sensors

---

## 🧠 AI Model

- Trained on historical mission-style telemetry
- Detects abnormal patterns
- Model file included (`interstellar_svm_model.pkl`)
- Can be deployed on **Raspberry Pi**

---

## ⚙️ Tech Stack

- Python
- Streamlit
- NumPy, Pandas
- Scikit-learn
- Edge AI concepts

---

## 🚀 How to Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
