# KPC Energy Intensity Benchmarking Dashboard

**Capstone Project | Dorothy Lizz Odoyo | 221883**
MSc Sustainable Energy Transition · Strathmore University · 2026

---

## Overview

A Python-based energy intensity benchmarking tool for Kenya Pipeline Company (KPC) pumping stations. The dashboard visualises energy performance for **PS1, PS3, PS5, and PS7** along the Mombasa–Nairobi pipeline corridor.

**Energy Intensity** = kWh consumed ÷ m³ pumped

| Class | Threshold |
|---|---|
| 🟢 Efficient | < 5.5 kWh/m³ |
| 🟡 Moderate | 5.5 – 7.5 kWh/m³ |
| 🔴 Inefficient | > 7.5 kWh/m³ |

---

## Features

- **Tab 1 — June 2026 Case Study**: Uses actual KPLC billing data (Jan–Jun 2026) with sample throughput volumes
- **Tab 2 — 5-Year Anomaly Explorer**: Synthetic training dataset (2020–2024) with 5 labelled anomaly types for ML model development
- Interactive Plotly charts, traffic-light station status, period comparisons, heatmaps
- CSV upload to replace sample data with real SCADA readings

---

## Anomaly Types (Training Dataset)

| Type | EI Effect | Description |
|---|---|---|
| Equipment_Degradation | +28% | Bearing friction, pump curve shift |
| Off_BEP_Operation | +22% | Pump far from best efficiency point |
| Maintenance_Period | −5% | Planned shutdown, reduced throughput |
| Power_Quality_Issue | +18% | Low power factor, KPLC voltage sags |
| Pump_Failure_Indicator | +45% | Cavitation / seal failure signs |

---

## Getting Started

```bash
# 1. Clone the repo
git clone https://github.com/lizzieodoyo11-beep/kpc-energy-dashboard.git
cd kpc-energy-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the dashboard
streamlit run app.py
```

---

## Data

| File | Description |
|---|---|
| `data/kpc_case_study_data.csv` | June 2026 case study (real energy, sample volumes) |
| `data/kpc_5yr_training_data.csv` | 5-year training dataset with anomaly labels |
| `data/KPC_Energy_Intensity_Data.xlsx` | Styled Excel workbook with data dictionary |

> **Note**: Energy consumption (kWh) is sourced from actual KPLC billing records. Throughput volumes (m³) are sample estimates — replace with SCADA meter readings for precise EI values.

---

## Project Structure

```
kpc-energy-dashboard/
├── app.py                  # Main Streamlit dashboard
├── requirements.txt
├── .gitignore
├── README.md
└── data/
    ├── kpc_case_study_data.csv
    ├── kpc_5yr_training_data.csv
    └── KPC_Energy_Intensity_Data.xlsx
```

---

## References

- ISO 50001:2018 — Energy Management Systems
- ISO 50006:2014 — Energy Performance Indicators
- Karassik et al. (2008) — Pump Handbook, 4th ed.
- Mohitpour et al. (2007) — Pipeline Design & Construction
