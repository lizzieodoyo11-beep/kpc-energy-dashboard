"""
Kenya Pipeline Company — Energy Intensity Benchmarking Dashboard
Pumping Stations: PS1, PS3, PS5, PS7 | Jul 2022 – Jun 2026
Capstone Project | Dorothy Lizz Odoyo | 221883 | MSc Sustainable Energy Transition | Strathmore University
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io, warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="KPC Energy Intensity Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .kpc-header {
    background: linear-gradient(90deg,#0a2342,#1a4a7a);
    padding:18px 24px; border-radius:10px; margin-bottom:14px;
    border-left:5px solid #f5a623;
  }
  .kpc-header h1 { color:#fff; font-size:1.4rem; margin:0; }
  .kpc-header p  { color:#b8d4f0; font-size:0.8rem; margin:4px 0 0; }
  .metric-card {
    background:linear-gradient(135deg,#1e2130,#252a3a);
    border-radius:10px; padding:14px; border-left:4px solid #4a9eff; margin-bottom:8px;
  }
  .metric-value { font-size:1.7rem; font-weight:700; color:#fff; }
  .metric-label { font-size:0.76rem; color:#9ca3af; margin-top:3px; }
  .tl-green  { background:linear-gradient(135deg,#064e3b,#065f46); border-left:4px solid #10b981; border-radius:10px; padding:14px; }
  .tl-yellow { background:linear-gradient(135deg,#451a03,#78350f); border-left:4px solid #f59e0b; border-radius:10px; padding:14px; }
  .tl-red    { background:linear-gradient(135deg,#450a0a,#7f1d1d); border-left:4px solid #ef4444; border-radius:10px; padding:14px; }
  .insight-box {
    background:#1a2540; border-left:3px solid #4a9eff;
    padding:12px 16px; border-radius:6px; font-size:0.83rem; color:#e2e8f0; margin:8px 0;
  }
  .anomaly-flag {
    background:#2d1515; border-left:3px solid #ef4444;
    padding:10px 14px; border-radius:6px; font-size:0.83rem; color:#fca5a5; margin:6px 0;
  }
  .cost-box {
    background:#1a2d1a; border-left:3px solid #10b981;
    padding:12px 16px; border-radius:6px; font-size:0.83rem; color:#bbf7d0; margin:8px 0;
  }
  .section-header {
    font-size:1rem; font-weight:600; color:#e2e8f0;
    margin:18px 0 8px; border-bottom:1px solid #374151; padding-bottom:5px;
  }
  .data-note {
    background:#1e2d45; border-left:3px solid #f5a623;
    padding:9px 13px; border-radius:6px; font-size:0.79rem; color:#b8d4f0;
  }
  .audit-pass { background:#064e3b; border-left:3px solid #10b981; border-radius:6px; padding:8px 12px; margin:4px 0; color:#bbf7d0; font-size:0.82rem; }
  .audit-warn { background:#451a03; border-left:3px solid #f59e0b; border-radius:6px; padding:8px 12px; margin:4px 0; color:#fde68a; font-size:0.82rem; }
  .audit-fail { background:#450a0a; border-left:3px solid #ef4444; border-radius:6px; padding:8px 12px; margin:4px 0; color:#fca5a5; font-size:0.82rem; }
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
EFFICIENT_T    = 3.0
INEFFICIENT_T  = 4.0
STATION_COLORS = {"PS1":"#4a9eff","PS3":"#f59e0b","PS5":"#10b981","PS7":"#c084fc"}
COLOR_MAP      = {"Efficient":"#10b981","Moderate":"#f59e0b","Inefficient":"#ef4444"}
MONTHS         = ['Jan','Feb','Mar','Apr','May','Jun']
KPLC_RATE      = 22.5
PUMP_CONFIG    = {"PS1":["Pump 1A","Pump 1B","Pump 1C"],
                  "PS3":["Pump 3A","Pump 3B"],
                  "PS5":["Pump 5A","Pump 5B","Pump 5C"],
                  "PS7":["Pump 7A","Pump 7B"]}

def classify(ei, eff=EFFICIENT_T, ineff=INEFFICIENT_T):
    if ei < eff:    return "Efficient"
    if ei <= ineff: return "Moderate"
    return "Inefficient"

# ── Data loaders ───────────────────────────────────────────────────────────────
@st.cache_data
def get_case_study_data():
    """Jan-Jun 2026: actual KPLC billing kWh (PS1A/PS3A/PS5A/PS7A) + real ML5 mainline throughput."""
    energy = {
        'PS1': [2281752, 2316759, 2682603, 2228373, 2138895, 2354868],
        'PS3': [1880916, 2207166, 1887042, 2098908, 1842234, 2021910],
        'PS5': [2176308, 2122656, 2484672, 2040162, 2011398, 2228940],
        'PS7': [2038182, 1977528, 2415570, 1949652, 1904724, 2136456],
    }
    # Real ML5 mainline throughput: MSP + AGO + JETA-1 (m3/month)
    volumes  = [790276.6, 737747.2, 859750.9, 725861.6, 756709.9, 771590.6]
    # Approximate runtimes — replace with SCADA actuals
    runtimes = {
        'PS1': [2820, 2640, 3060, 2580, 2700, 2760],
        'PS3': [2760, 2580, 3000, 2520, 2640, 2700],
        'PS5': [2790, 2610, 3030, 2550, 2670, 2730],
        'PS7': [2730, 2550, 2970, 2490, 2610, 2670],
    }
    rows = []
    for stn in ['PS1','PS3','PS5','PS7']:
        for i, mo in enumerate(MONTHS):
            kwh = energy[stn][i]
            vol = volumes[i]
            rt  = runtimes[stn][i]
            ei  = round(kwh / vol, 4)
            rows.append({
                'Date':   pd.to_datetime(f'2026-{i+1:02d}-01'),
                'Month':  mo, 'Year': 2026, 'Station': stn,
                'Energy_kWh': kwh, 'Volume_m3': vol, 'Runtime_hrs': rt,
                'Flow_Rate_m3hr': round(vol / rt, 1),
                'Avg_Power_kW':   round(kwh / rt, 1),
                'Energy_Intensity_kWh_m3': ei,
                'Efficiency_Class': classify(ei),
                'Cost_KShs': round(kwh * KPLC_RATE),
                'Data_Source': 'Actual KPLC Billing + ML5 Mainline Throughput',
            })
    return pd.DataFrame(rows)


@st.cache_data
def get_master_data():
    """Jul 2022 – Jun 2026: real ML5 throughput + real energy (2026) + synthetic energy (pre-2026)."""
    throughput = [
        ('2022-07',623606.9),('2022-08',619673.9),('2022-09',597854.0),
        ('2022-10',642873.2),('2022-11',588079.0),('2022-12',675400.5),
        ('2023-01',639435.4),('2023-02',639018.8),('2023-03',694056.7),
        ('2023-04',715776.1),('2023-05',689065.5),('2023-06',690370.7),
        ('2023-07',716025.5),('2023-08',692337.9),('2023-09',651346.0),
        ('2023-10',611759.2),('2023-11',657060.7),('2023-12',692224.8),
        ('2024-01',713826.7),('2024-02',675850.0),('2024-03',692388.1),
        ('2024-04',632251.5),('2024-05',692925.5),('2024-06',698275.0),
        ('2024-07',761458.9),('2024-08',734294.3),('2024-09',699492.1),
        ('2024-10',727407.3),('2024-11',695631.6),('2024-12',699021.9),
        ('2025-01',759657.1),('2025-02',676165.2),('2025-03',740304.3),
        ('2025-04',694546.1),('2025-05',753813.8),('2025-06',707144.4),
        ('2025-07',751134.0),('2025-08',781426.5),('2025-09',741159.1),
        ('2025-10',826477.9),('2025-11',839001.8),('2025-12',830325.5),
        ('2026-01',790276.6),('2026-02',737747.2),('2026-03',859750.9),
        ('2026-04',725861.6),('2026-05',756709.9),('2026-06',771590.6),
    ]
    energy_real_2026 = {
        'PS1': [2281752,2316759,2682603,2228373,2138895,2354868],
        'PS3': [1880916,2207166,1887042,2098908,1842234,2021910],
        'PS5': [2176308,2122656,2484672,2040162,2011398,2228940],
        'PS7': [2038182,1977528,2415570,1949652,1904724,2136456],
    }
    avg_ei_ref = {'PS1':3.016,'PS3':2.586,'PS5':2.813,'PS7':2.674}
    # Scheduled anomaly events (synthetic pre-2026 only)
    anomaly_sched = {
        ('PS1',2022,10):'Equipment_Degradation',('PS1',2023,4):'Off_BEP_Operation',
        ('PS1',2023,11):'Power_Quality_Issue',  ('PS1',2024,7):'Pump_Failure_Indicator',
        ('PS1',2025,2):'Maintenance_Period',
        ('PS3',2022,9):'Off_BEP_Operation',     ('PS3',2023,6):'Maintenance_Period',
        ('PS3',2024,3):'Equipment_Degradation', ('PS3',2024,10):'Power_Quality_Issue',
        ('PS3',2025,5):'Pump_Failure_Indicator',
        ('PS5',2022,11):'Equipment_Degradation',('PS5',2023,3):'Power_Quality_Issue',
        ('PS5',2024,8):'Maintenance_Period',    ('PS5',2025,1):'Off_BEP_Operation',
        ('PS5',2025,9):'Pump_Failure_Indicator',
        ('PS7',2022,8):'Pump_Failure_Indicator',('PS7',2023,2):'Equipment_Degradation',
        ('PS7',2024,6):'Power_Quality_Issue',   ('PS7',2025,4):'Off_BEP_Operation',
        ('PS7',2025,10):'Maintenance_Period',
    }
    fx = {
        'Equipment_Degradation':  dict(ei=1.28, vol=0.97, pf=-0.02),
        'Off_BEP_Operation':      dict(ei=1.22, vol=0.88, pf=-0.03),
        'Maintenance_Period':     dict(ei=0.95, vol=0.55, pf=0.00),
        'Power_Quality_Issue':    dict(ei=1.18, vol=1.00, pf=-0.08),
        'Pump_Failure_Indicator': dict(ei=1.45, vol=0.70, pf=-0.05),
        None:                     dict(ei=1.00, vol=1.00, pf=0.00),
    }
    np.random.seed(42)
    rows = []
    ref_2026 = [pd.Timestamp(f'2026-{m:02d}-01') for m in range(1,7)]

    for ym, base_vol in throughput:
        dt    = pd.Timestamp(ym + '-01')
        year  = dt.year; month = dt.month
        is_real = (year == 2026 and month <= 6)

        for stn in ['PS1','PS3','PS5','PS7']:
            at = anomaly_sched.get((stn, year, month), None)
            ef = fx[at]

            if is_real:
                idx    = ref_2026.index(dt)
                energy = energy_real_2026[stn][idx]
                vol    = base_vol
                pf     = round(np.random.uniform(0.93, 0.98), 3)
                is_anom = 0; anom_type = 'Normal'; data_src = 'Actual KPLC Billing'
            else:
                seasonal = 1.0 + 0.04 * np.sin((month - 3) * np.pi / 6)
                yr_factor = 1 + (2026 - year) * 0.005
                noise   = np.random.normal(1.0, 0.025)
                energy  = avg_ei_ref[stn] * base_vol * ef['ei'] * seasonal * yr_factor * noise
                vol     = base_vol * ef['vol'] * (1 + np.random.normal(0, 0.01))
                pf      = round(np.clip(0.955 + ef['pf'] + np.random.normal(0, 0.015), 0.70, 1.0), 3)
                is_anom = int(at is not None); anom_type = at if at else 'Normal'
                data_src = 'Synthetic (real throughput, modelled energy)'

            vol    = max(vol, 50000)
            energy = max(energy, 100000)
            ei     = energy / vol
            rt     = vol / (280 + np.random.normal(0, 8))
            rt     = max(rt, 100)
            rows.append({
                'Date':   dt, 'Year': year, 'Month': month,
                'Month_Name': dt.strftime('%b'),
                'Quarter': f"Q{(month-1)//3+1}",
                'Station': stn,
                'Energy_kWh': round(energy),
                'Volume_m3':  round(vol, 1),
                'Runtime_hrs': round(rt, 1),
                'Flow_Rate_m3hr': round(vol / rt, 1),
                'Avg_Power_kW':   round(energy / rt, 1),
                'Power_Factor':   pf,
                'Energy_Intensity_kWh_m3': round(ei, 4),
                'Efficiency_Class': classify(ei),
                'Cost_KShs': round(energy * KPLC_RATE),
                'Is_Anomaly': is_anom,
                'Anomaly_Type': anom_type,
                'Data_Source': data_src,
            })
    return pd.DataFrame(rows)


@st.cache_data
def get_pump_data():
    np.random.seed(99)
    rows = []
    avg_ei_ref = {'PS1':3.016,'PS3':2.586,'PS5':2.813,'PS7':2.674}
    vol_base   = 760000  # typical monthly mainline volume
    for stn, pumps in PUMP_CONFIG.items():
        n = len(pumps); base_ei = avg_ei_ref[stn]
        for i, mo in enumerate(MONTHS):
            total_vol = vol_base * (1 + 0.08 * np.sin((i+1-3)*np.pi/6))
            splits = np.random.dirichlet(np.ones(n)) * total_vol
            for j, pump in enumerate(pumps):
                vol = splits[j]
                pump_ei = max(base_ei * (0.92 + 0.16 * np.random.random()) + np.random.normal(0,0.06), 1.5)
                kwh = pump_ei * vol
                rt  = np.clip(total_vol / (n * 280) + np.random.normal(0, 30), 100, 900)
                rows.append({'Month': mo, 'Station': stn, 'Pump': pump,
                    'Energy_kWh': round(kwh), 'Volume_m3': round(vol),
                    'Runtime_hrs': round(rt, 1),
                    'Energy_Intensity_kWh_m3': round(pump_ei, 4),
                    'Efficiency_Class': classify(pump_ei),
                    'Cost_KShs': round(kwh * KPLC_RATE)})
    return pd.DataFrame(rows)


# ── Helpers ────────────────────────────────────────────────────────────────────
def generate_commentary(stn_df, station, eff_t, ineff_t, tariff):
    rows      = stn_df.sort_values('Date')
    avg_ei    = rows['Energy_Intensity_kWh_m3'].mean()
    best_mo   = rows.loc[rows['Energy_Intensity_kWh_m3'].idxmin(), 'Month']
    worst_mo  = rows.loc[rows['Energy_Intensity_kWh_m3'].idxmax(), 'Month']
    best_ei   = rows['Energy_Intensity_kWh_m3'].min()
    worst_ei  = rows['Energy_Intensity_kWh_m3'].max()
    pct_gap   = ((worst_ei - best_ei) / best_ei) * 100
    total_cost = rows['Energy_kWh'].sum() * tariff
    lines = [
        f"**{station}** averaged **{avg_ei:.3f} kWh/m³** over Jan–Jun 2026, "
        f"classified as **{classify(avg_ei, eff_t, ineff_t)}**.",
        f"Best month: **{best_mo}** ({best_ei:.3f} kWh/m³)  ·  "
        f"Worst month: **{worst_mo}** ({worst_ei:.3f} kWh/m³) — gap of **{pct_gap:.1f}%**.",
    ]
    for k in range(1, len(rows)):
        prev = rows.iloc[k-1]; curr = rows.iloc[k]
        chg  = ((curr['Energy_Intensity_kWh_m3'] - prev['Energy_Intensity_kWh_m3'])
                / prev['Energy_Intensity_kWh_m3']) * 100
        if abs(chg) >= 6:
            direction = "rose" if chg > 0 else "fell"
            cause = ""
            if chg > 10:
                if curr['Volume_m3'] < prev['Volume_m3'] * 0.90:
                    cause = " — volume drop suggests supply variation or batching change"
                elif curr['Energy_kWh'] > prev['Energy_kWh'] * 1.08:
                    cause = " — energy spike; check power quality or pump condition"
            lines.append(f"EI {direction} **{abs(chg):.1f}%** from {prev['Month']} to {curr['Month']}{cause}.")
    lines.append(f"Total electricity cost Jan–Jun 2026: **KShs {total_cost:,.0f}** "
                 f"(~KShs {total_cost/6:,.0f}/month).")
    cls = classify(avg_ei, eff_t, ineff_t)
    if   cls == "Efficient":   lines.append("Operating efficiently — maintain current scheduling and monitoring.")
    elif cls == "Moderate":    lines.append("Moderate band — review pump scheduling and check for off-BEP operation.")
    else:                      lines.append("Inefficient — urgent review of pump condition, scheduling, and power factor recommended.")
    return "\n\n".join(lines)


def detect_anomalies(stn_df):
    flags = []
    med_ei  = stn_df['Energy_Intensity_kWh_m3'].median()
    med_vol = stn_df['Volume_m3'].median()
    med_rt  = stn_df['Runtime_hrs'].median()
    for _, row in stn_df.iterrows():
        ei_dev  = (row['Energy_Intensity_kWh_m3'] - med_ei)  / med_ei
        vol_dev = (row['Volume_m3']               - med_vol) / med_vol
        rt_dev  = (row['Runtime_hrs']             - med_rt)  / med_rt
        if ei_dev > 0.10 and rt_dev > 0.05:
            flags.append((row['Month'], "High EI + extended runtime — possible off-BEP or pump wear", "HIGH"))
        elif ei_dev > 0.10 and vol_dev < -0.08:
            flags.append((row['Month'], "High EI + low volume — possible maintenance or supply issue", "MED"))
        elif ei_dev > 0.08:
            flags.append((row['Month'], "EI spike above baseline — check equipment condition", "LOW"))
        elif vol_dev < -0.20:
            flags.append((row['Month'], "Significant volume drop — planned/unplanned maintenance likely", "INFO"))
    return flags


# ── Load data ──────────────────────────────────────────────────────────────────
df_case   = get_case_study_data()
df_master = get_master_data()
df_pump   = get_pump_data()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### KPC Energy Dashboard")
    st.caption("Kenya Pipeline Company\nEnergy Intensity Benchmarking")
    st.divider()
    uploaded = st.file_uploader("Upload SCADA data (CSV)", type=["csv"],
        help="Columns: Date, Station, Energy_kWh, Volume_m3")
    st.divider()
    st.markdown("**Benchmark Thresholds (kWh/m3)**")
    eff_t   = st.number_input("Efficient below",   value=EFFICIENT_T,   step=0.1, format="%.1f")
    ineff_t = st.number_input("Inefficient above", value=INEFFICIENT_T, step=0.1, format="%.1f")
    tariff  = st.number_input("KPLC tariff (KShs/kWh)", value=KPLC_RATE, step=0.5, format="%.1f")
    st.divider()
    page = st.radio("Navigate", [
        "System Overview",
        "Pipeline Map",
        "Station Deep Dive",
        "Pump-Level Breakdown",
        "Anomaly Detection",
        "Data Audit",
        "Model Training",
        "Prediction",
        "What-If Simulator",
        "Cost Analysis",
        "ML Model Performance",
        "4-Year Training Data",
    ], label_visibility="collapsed")
    st.divider()
    st.caption("MSc Sustainable Energy Transition\nStrathmore University 2026")

if uploaded:
    try:
        df_up = pd.read_csv(uploaded); df_up['Date'] = pd.to_datetime(df_up['Date'])
        if 'Energy_Intensity_kWh_m3' not in df_up.columns:
            df_up['Energy_Intensity_kWh_m3'] = df_up['Energy_kWh'] / df_up['Volume_m3']
        df_up['Efficiency_Class'] = df_up['Energy_Intensity_kWh_m3'].apply(
            lambda x: classify(x, eff_t, ineff_t))
        df_up['Cost_KShs'] = df_up['Energy_kWh'] * tariff
        if 'Month' not in df_up.columns:
            df_up['Month'] = df_up['Date'].dt.strftime('%b')
        df_case = df_up
    except Exception as e:
        st.error(f"Upload error: {e}")

df_case['Efficiency_Class'] = df_case['Energy_Intensity_kWh_m3'].apply(
    lambda x: classify(x, eff_t, ineff_t))
df_case['Cost_KShs'] = df_case['Energy_kWh'] * tariff

ACOLS = {'Equipment_Degradation':'#f97316','Off_BEP_Operation':'#a855f7',
          'Maintenance_Period':'#06b6d4','Power_Quality_Issue':'#ef4444',
          'Pump_Failure_Indicator':'#fbbf24'}


def color_cls(val):
    return {'Efficient':   'background-color:#064e3b;color:#10b981',
            'Moderate':    'background-color:#451a03;color:#f59e0b',
            'Inefficient': 'background-color:#450a0a;color:#ef4444'}.get(val, '')


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SYSTEM OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "System Overview":
    st.markdown("""<div class="kpc-header">
      <h1>Kenya Pipeline Company — Energy Intensity Benchmarking</h1>
      <p>PS1 &nbsp;|&nbsp; PS3 &nbsp;|&nbsp; PS5 &nbsp;|&nbsp; PS7 &nbsp;|&nbsp; Jan–Jun 2026 &nbsp;|&nbsp;
      Energy: Actual KPLC Billing (PS1A/PS3A/PS5A/PS7A) &nbsp;|&nbsp; Volume: Real ML5 Mainline Throughput</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("""<div class="data-note">
    Energy (kWh) = actual KPLC billing records &nbsp;|&nbsp;
    Volume (m3) = ML5 real mainline throughput (MSP + AGO + JETA-1) &nbsp;|&nbsp;
    EI = kWh / m3
    </div>""", unsafe_allow_html=True)

    st.markdown('<p class="section-header">Station Status — Jan–Jun 2026</p>', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, stn in enumerate(['PS1','PS3','PS5','PS7']):
        sd  = df_case[df_case['Station'] == stn]
        avg_ei = sd['Energy_Intensity_kWh_m3'].mean()
        cls = classify(avg_ei, eff_t, ineff_t)
        css = "tl-green" if cls == "Efficient" else ("tl-yellow" if cls == "Moderate" else "tl-red")
        with cols[i]:
            st.markdown(f"""<div class="{css}">
                <div style="font-weight:700;font-size:1rem;color:#fff">{stn}</div>
                <div style="font-size:1.6rem;font-weight:700;color:#fff;margin:5px 0">{avg_ei:.3f}</div>
                <div style="font-size:0.72rem;color:#d1d5db">kWh/m3 — {cls}</div>
                <div style="font-size:0.72rem;color:#d1d5db;margin-top:3px">KShs {sd['Cost_KShs'].sum()/1e6:.1f}M total</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<p class="section-header">System KPIs</p>', unsafe_allow_html=True)
    c1,c2,c3,c4,c5 = st.columns(5)
    for col, (val, lbl, color) in zip([c1,c2,c3,c4,c5],[
        (f"{df_case['Energy_Intensity_kWh_m3'].mean():.3f}", "Avg System EI (kWh/m3)",    "#4a9eff"),
        (f"{df_case['Energy_kWh'].sum()/1e6:.1f}M",          "Total Energy (kWh)",         "#f59e0b"),
        (f"{df_case['Volume_m3'].mean()/1e6:.2f}M",          "Avg Monthly Volume (m3)",    "#10b981"),
        (f"KShs {df_case['Cost_KShs'].sum()/1e6:.1f}M",      "Total Electricity Cost",     "#ef4444"),
        (f"{df_case['Flow_Rate_m3hr'].mean():.0f}",           "Avg Flow Rate (m3/hr)",      "#c084fc"),
    ]):
        with col:
            st.markdown(f"""<div class="metric-card" style="border-left-color:{color}">
                <div class="metric-value">{val}</div><div class="metric-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    col_t, col_r = st.columns([3, 2])
    with col_t:
        fig = go.Figure()
        for stn in ['PS1','PS3','PS5','PS7']:
            sd = df_case[df_case['Station'] == stn].sort_values('Date')
            fig.add_trace(go.Scatter(
                x=sd['Month'], y=sd['Energy_Intensity_kWh_m3'], name=stn,
                mode='lines+markers+text',
                text=[f"{v:.3f}" for v in sd['Energy_Intensity_kWh_m3']],
                textposition='top center', textfont=dict(size=8),
                marker=dict(size=7, color=STATION_COLORS[stn]),
                line=dict(width=2.5, color=STATION_COLORS[stn])))
        fig.add_hline(y=eff_t,   line_dash='dash', line_color='#10b981',
                      annotation_text=f'Efficient <={eff_t}',   annotation_position='top left')
        fig.add_hline(y=ineff_t, line_dash='dash', line_color='#ef4444',
                      annotation_text=f'Inefficient >{ineff_t}', annotation_position='top left')
        fig.add_hrect(y0=0,       y1=eff_t,   fillcolor='#10b981', opacity=0.05, line_width=0)
        fig.add_hrect(y0=eff_t,   y1=ineff_t, fillcolor='#f59e0b', opacity=0.05, line_width=0)
        fig.add_hrect(y0=ineff_t, y1=8,       fillcolor='#ef4444', opacity=0.05, line_width=0)
        fig.update_layout(title='Monthly EI Trend — All Stations',
            xaxis=dict(categoryorder='array', categoryarray=MONTHS),
            yaxis_title='kWh/m3', template='plotly_dark', height=370,
            legend=dict(orientation='h', y=1.02, x=1, xanchor='right'),
            margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        rank = (df_case.groupby('Station')['Energy_Intensity_kWh_m3']
                .mean().reset_index().sort_values('Energy_Intensity_kWh_m3'))
        rank['Color'] = rank['Energy_Intensity_kWh_m3'].apply(
            lambda x: '#10b981' if x < eff_t else ('#ef4444' if x > ineff_t else '#f59e0b'))
        fig2 = go.Figure(go.Bar(
            y=rank['Station'], x=rank['Energy_Intensity_kWh_m3'], orientation='h',
            marker_color=rank['Color'],
            text=[f"{v:.3f}" for v in rank['Energy_Intensity_kWh_m3']],
            textposition='outside'))
        fig2.add_vline(x=eff_t,   line_dash='dash', line_color='#10b981')
        fig2.add_vline(x=ineff_t, line_dash='dash', line_color='#ef4444')
        fig2.update_layout(title='Station Ranking', template='plotly_dark', height=200,
            xaxis_title='Avg EI (kWh/m3)', margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig2, use_container_width=True)

        heat = (df_case.pivot_table(index='Station', columns='Month',
                values='Energy_Intensity_kWh_m3', aggfunc='mean')
                .reindex(columns=MONTHS))
        fig3 = px.imshow(heat, color_continuous_scale='RdYlGn_r', template='plotly_dark',
            title='EI Heatmap (kWh/m3)', labels=dict(color='kWh/m3'), aspect='auto', text_auto='.3f')
        fig3.update_layout(height=165, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<p class="section-header">Data Provenance</p>', unsafe_allow_html=True)
    st.markdown("""<div class="data-note">
    <b>Energy:</b> Actual KPLC billing records, PS1A + PS3A + PS5A + PS7A metered totals (High Rate + Low Rate tariff units), Jan–Jun 2026.<br>
    <b>Volume:</b> Real ML5 mainline throughput — sum of MSP, AGO, and JETA-1 product deliveries per month (source: KPC batch management system).<br>
    <b>EI = Energy (kWh) / Volume (m3).</b> Each station receives the full mainline throughput flow.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PIPELINE MAP
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Pipeline Map":
    st.markdown("""<div class="kpc-header">
      <h1>KPC Pipeline — Mombasa to Nairobi Corridor</h1>
      <p>20-inch main pipeline &nbsp;|&nbsp; ~500 km &nbsp;|&nbsp; Elevation gain 5 m to 1,600 m &nbsp;|&nbsp; PS1 to PS3 to PS5 to PS7</p>
    </div>""", unsafe_allow_html=True)

    STATIONS = {
        "Mombasa Port":  dict(km=0,   elev=5,    desc="Dispatch terminal — petroleum products from refinery"),
        "PS1":           dict(km=18,  elev=25,   desc="First mainline pump station — 3 pumps, C3 tariff"),
        "PS3":           dict(km=135, elev=420,  desc="Intermediate booster station — 2 pumps, C5 tariff"),
        "PS5":           dict(km=310, elev=950,  desc="Mid-route station — 3 pumps, steepest gradient"),
        "PS7":           dict(km=455, elev=1520, desc="Near-Nairobi station — 2 pumps, final push"),
        "Nairobi Depot": dict(km=495, elev=1600, desc="Receiving terminal — distribution to inland depots"),
    }
    pipeline_km  = [0, 18, 135, 310, 455, 495]
    pipeline_elv = [5, 25, 420, 950, 1520, 1600]

    stn_ei = {stn: df_case[df_case['Station'] == stn]['Energy_Intensity_kWh_m3'].mean()
              for stn in ['PS1','PS3','PS5','PS7']}
    stn_cls = {stn: classify(ei, eff_t, ineff_t) for stn, ei in stn_ei.items()}
    cls_color = {"Efficient":"#10b981","Moderate":"#f59e0b","Inefficient":"#ef4444"}

    fig_pipe = go.Figure()
    fig_pipe.add_trace(go.Scatter(
        x=pipeline_km, y=pipeline_elv, fill='tozeroy', fillcolor='rgba(30,40,70,0.6)',
        line=dict(color='#374151', width=1), name='Terrain', showlegend=False))
    fig_pipe.add_trace(go.Scatter(
        x=pipeline_km, y=pipeline_elv, mode='lines',
        line=dict(color='#f5a623', width=6), name='20" Pipeline', showlegend=True))

    for name, d in [("Mombasa Port", STATIONS["Mombasa Port"]),
                     ("Nairobi Depot", STATIONS["Nairobi Depot"])]:
        fig_pipe.add_trace(go.Scatter(
            x=[d['km']], y=[d['elev']], mode='markers+text',
            marker=dict(size=16, color='#64748b', symbol='diamond', line=dict(width=2, color='white')),
            text=[name], textposition='top center', textfont=dict(size=10, color='#94a3b8'),
            name=name, showlegend=False))

    ps_km  = [18, 135, 310, 455]
    ps_elv = [25, 420, 950, 1520]
    for stn, km, elv in zip(['PS1','PS3','PS5','PS7'], ps_km, ps_elv):
        ei  = stn_ei[stn]; cls = stn_cls[stn]; col = cls_color[cls]
        fig_pipe.add_trace(go.Scatter(
            x=[km], y=[elv], mode='markers+text',
            marker=dict(size=20, color=col, symbol='square', line=dict(width=2, color='white')),
            text=[f"  {stn}  {ei:.3f} kWh/m3"],
            textposition='top right', textfont=dict(size=10, color=col),
            name=f"{stn} ({cls})", showlegend=True,
            hovertemplate=f"<b>{stn}</b><br>km {km} | {elv}m elevation<br>"
                          f"Avg EI: {ei:.3f} kWh/m3<br>Status: {cls}<extra></extra>"))

    fig_pipe.update_layout(
        title='KPC 20-inch Pipeline — Elevation Profile and Live Station EI Status',
        xaxis=dict(title='Distance from Mombasa (km)', showgrid=True, gridcolor='#1e2130', range=[-10,510]),
        yaxis=dict(title='Elevation (m above sea level)', showgrid=True, gridcolor='#1e2130'),
        template='plotly_dark', height=420,
        legend=dict(orientation='h', y=-0.2, font=dict(size=10)),
        margin=dict(l=10, r=10, t=60, b=10),
        paper_bgcolor='#0e1117', plot_bgcolor='#0e1117')
    st.plotly_chart(fig_pipe, use_container_width=True)

    st.markdown('<p class="section-header">Station Quick Reference</p>', unsafe_allow_html=True)
    cols = st.columns(4)
    for col, stn in zip(cols, ['PS1','PS3','PS5','PS7']):
        d   = STATIONS[stn]; ei = stn_ei[stn]; cls = stn_cls[stn]
        css = "tl-green" if cls == "Efficient" else ("tl-yellow" if cls == "Moderate" else "tl-red")
        pumps = len(PUMP_CONFIG[stn])
        with col:
            st.markdown(f"""<div class="{css}" style="min-height:140px">
                <div style="font-weight:700;font-size:1rem;color:#fff">{stn}</div>
                <div style="font-size:1.5rem;font-weight:700;color:#fff;margin:4px 0">{ei:.3f} kWh/m3</div>
                <div style="font-size:0.72rem;color:#d1d5db">{cls}</div>
                <hr style="border-color:#ffffff22;margin:8px 0">
                <div style="font-size:0.72rem;color:#d1d5db">km {d['km']} | {d['elev']}m elevation</div>
                <div style="font-size:0.72rem;color:#d1d5db">{pumps} pumps</div>
                <div style="font-size:0.72rem;color:#d1d5db;margin-top:4px">{d['desc']}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="insight-box">
    <b>Why elevation matters for energy intensity:</b> The Mombasa-Nairobi pipeline climbs
    <b>1,595 metres</b> over ~500 km. A significant share of energy at each station goes into
    lifting product against gravity, not just overcoming friction losses. Stations at higher
    elevations (PS5, PS7) must generate more hydraulic head, which raises their energy intensity.
    When comparing station EI values, the elevation component is expected by physics and does not
    necessarily indicate lower pump efficiency.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: STATION DEEP DIVE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Station Deep Dive":
    st.markdown("""<div class="kpc-header">
      <h1>Station Deep Dive</h1><p>Full performance profile for each pumping station</p>
    </div>""", unsafe_allow_html=True)

    stn = st.selectbox("Select Station", ['PS1','PS3','PS5','PS7'])
    sd  = df_case[df_case['Station'] == stn].sort_values('Date')
    avg_ei = sd['Energy_Intensity_kWh_m3'].mean()
    cls = classify(avg_ei, eff_t, ineff_t)
    css = "tl-green" if cls == "Efficient" else ("tl-yellow" if cls == "Moderate" else "tl-red")

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="{css}">
            <div style="font-weight:700;color:#fff;font-size:1.1rem">{stn} — {cls}</div>
            <div style="font-size:1.8rem;font-weight:700;color:#fff">{avg_ei:.3f}</div>
            <div style="font-size:0.72rem;color:#d1d5db">Avg EI (kWh/m3)</div>
        </div>""", unsafe_allow_html=True)
    for col, (val, lbl, color) in zip([c2,c3,c4], [
        (f"{sd['Energy_kWh'].sum()/1e6:.2f}M", "Total Energy (kWh)",  "#f59e0b"),
        (f"KShs {sd['Cost_KShs'].sum()/1e6:.2f}M", "Total Cost",      "#ef4444"),
        (f"{sd['Runtime_hrs'].mean():.0f}h",    "Avg Monthly Runtime", "#c084fc"),
    ]):
        with col:
            st.markdown(f"""<div class="metric-card" style="border-left-color:{color}">
                <div class="metric-value">{val}</div><div class="metric-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<p class="section-header">Auto-Generated Performance Commentary</p>', unsafe_allow_html=True)
    commentary = generate_commentary(sd, stn, eff_t, ineff_t, tariff)
    st.markdown(f'<div class="insight-box">{commentary}</div>', unsafe_allow_html=True)

    flags = detect_anomalies(sd)
    if flags:
        st.markdown('<p class="section-header">Detected Signals</p>', unsafe_allow_html=True)
        for mo, msg, level in flags:
            css_f = 'anomaly-flag' if level in ('HIGH','MED') else 'insight-box'
            st.markdown(f'<div class="{css_f}"><b>{mo} 2026</b> — {msg}</div>', unsafe_allow_html=True)

    st.markdown('<p class="section-header">Monthly Detail</p>', unsafe_allow_html=True)
    col_ei, col_ev = st.columns(2)
    with col_ei:
        fig = go.Figure(go.Bar(
            x=sd['Month'], y=sd['Energy_Intensity_kWh_m3'],
            marker_color=[('#10b981' if v < eff_t else ('#ef4444' if v > ineff_t else '#f59e0b'))
                          for v in sd['Energy_Intensity_kWh_m3']],
            text=[f"{v:.3f}" for v in sd['Energy_Intensity_kWh_m3']], textposition='outside'))
        fig.add_hline(y=eff_t,   line_dash='dash', line_color='#10b981')
        fig.add_hline(y=ineff_t, line_dash='dash', line_color='#ef4444')
        fig.update_layout(title=f'{stn} — Monthly EI', template='plotly_dark', height=300,
            xaxis=dict(categoryorder='array', categoryarray=MONTHS),
            yaxis_title='kWh/m3', margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with col_ev:
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.add_trace(go.Bar(x=sd['Month'], y=sd['Energy_kWh']/1e6, name='Energy (M kWh)',
            marker_color=STATION_COLORS[stn], opacity=0.7), secondary_y=False)
        fig2.add_trace(go.Scatter(x=sd['Month'], y=sd['Volume_m3']/1e3, name='Volume (k m3)',
            mode='lines+markers', marker=dict(size=7, color='#f5a623'),
            line=dict(color='#f5a623', width=2)), secondary_y=True)
        fig2.update_layout(title=f'{stn} — Energy vs Volume', template='plotly_dark', height=300,
            xaxis=dict(categoryorder='array', categoryarray=MONTHS),
            margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation='h', y=1.02))
        fig2.update_yaxes(title_text='Energy (M kWh)', secondary_y=False)
        fig2.update_yaxes(title_text='Volume (k m3)',  secondary_y=True)
        st.plotly_chart(fig2, use_container_width=True)

    col_rt, col_sc = st.columns(2)
    with col_rt:
        fig3 = go.Figure(go.Scatter(x=sd['Month'], y=sd['Runtime_hrs'], mode='lines+markers',
            fill='tozeroy', fillcolor='rgba(74,158,255,0.15)',
            line=dict(color='#4a9eff', width=2), marker=dict(size=7)))
        fig3.update_layout(title=f'{stn} — Monthly Runtime', template='plotly_dark', height=250,
            xaxis=dict(categoryorder='array', categoryarray=MONTHS),
            yaxis_title='Hours', margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig3, use_container_width=True)
    with col_sc:
        fig4 = go.Figure(go.Scatter(
            x=sd['Volume_m3']/1e3, y=sd['Energy_Intensity_kWh_m3'],
            mode='markers+text', text=sd['Month'], textposition='top center',
            marker=dict(size=12, color=STATION_COLORS[stn])))
        fig4.add_hline(y=eff_t,   line_dash='dash', line_color='#10b981')
        fig4.add_hline(y=ineff_t, line_dash='dash', line_color='#ef4444')
        fig4.update_layout(title=f'{stn} — Volume vs EI', template='plotly_dark', height=250,
            xaxis_title='Volume (k m3)', yaxis_title='EI (kWh/m3)',
            margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig4, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PUMP-LEVEL BREAKDOWN
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Pump-Level Breakdown":
    st.markdown("""<div class="kpc-header">
      <h1>Pump-Level Breakdown</h1>
      <p>Individual pump performance — identifies which pump is driving inefficiency</p>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="data-note">Pump-level data is simulated — replace with individual SCADA pump metering for production use.</div>', unsafe_allow_html=True)

    stn = st.selectbox("Station", ['PS1','PS3','PS5','PS7'], key='p_stn')
    mo  = st.selectbox("Month", MONTHS, key='p_mo')
    pdata = df_pump[(df_pump['Station'] == stn) & (df_pump['Month'] == mo)]

    cols = st.columns(len(pdata))
    for (_, row), col in zip(pdata.iterrows(), cols):
        cls = classify(row['Energy_Intensity_kWh_m3'], eff_t, ineff_t)
        css = "tl-green" if cls == "Efficient" else ("tl-yellow" if cls == "Moderate" else "tl-red")
        with col:
            st.markdown(f"""<div class="{css}">
                <div style="font-weight:700;color:#fff">{row['Pump']}</div>
                <div style="font-size:1.5rem;font-weight:700;color:#fff">{row['Energy_Intensity_kWh_m3']:.3f}</div>
                <div style="font-size:0.72rem;color:#d1d5db">kWh/m3 — {cls}</div>
                <div style="font-size:0.72rem;color:#d1d5db">KShs {row['Cost_KShs']:,.0f}</div>
            </div>""", unsafe_allow_html=True)

    col_bar, col_pie = st.columns(2)
    with col_bar:
        fig = px.bar(pdata, x='Pump', y='Energy_Intensity_kWh_m3', color='Efficiency_Class',
            color_discrete_map=COLOR_MAP, title=f'{stn} — EI per Pump ({mo} 2026)',
            text=[f"{v:.3f}" for v in pdata['Energy_Intensity_kWh_m3']], template='plotly_dark')
        fig.add_hline(y=eff_t,   line_dash='dash', line_color='#10b981')
        fig.add_hline(y=ineff_t, line_dash='dash', line_color='#ef4444')
        fig.update_traces(textposition='outside')
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=50, b=10),
            showlegend=False, yaxis_title='kWh/m3')
        st.plotly_chart(fig, use_container_width=True)
    with col_pie:
        fig2 = px.pie(pdata, names='Pump', values='Energy_kWh',
            title=f'{stn} — Energy Share ({mo} 2026)', template='plotly_dark', hole=0.45)
        fig2.update_layout(height=300, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    all_p = df_pump[df_pump['Station'] == stn]
    fig3  = px.line(all_p, x='Month', y='Energy_Intensity_kWh_m3', color='Pump', markers=True,
        title=f'{stn} — Monthly EI by Pump', template='plotly_dark',
        category_orders={'Month': MONTHS})
    fig3.add_hline(y=eff_t,   line_dash='dash', line_color='#10b981')
    fig3.add_hline(y=ineff_t, line_dash='dash', line_color='#ef4444')
    fig3.update_layout(height=300, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig3, use_container_width=True)

    worst = pdata.loc[pdata['Energy_Intensity_kWh_m3'].idxmax()]
    best  = pdata.loc[pdata['Energy_Intensity_kWh_m3'].idxmin()]
    gap   = worst['Energy_Intensity_kWh_m3'] - best['Energy_Intensity_kWh_m3']
    pot   = gap * pdata['Volume_m3'].mean()
    st.markdown(f"""<div class="insight-box">
    <b>{worst['Pump']}</b> is least efficient at <b>{worst['Energy_Intensity_kWh_m3']:.3f} kWh/m3</b> vs
    <b>{best['Pump']}</b> at <b>{best['Energy_Intensity_kWh_m3']:.3f} kWh/m3</b> (gap: {gap:.3f} kWh/m3).<br>
    If {worst['Pump']} matched {best['Pump']}: estimated saving
    <b>{pot/1e3:.0f}k kWh/month (~KShs {pot*tariff/1e3:.0f}k)</b>.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ANOMALY DETECTION
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Anomaly Detection":
    st.markdown("""<div class="kpc-header">
      <h1>Anomaly Detection</h1>
      <p>Statistical flagging with cause diagnosis and recommended actions</p>
    </div>""", unsafe_allow_html=True)

    st.markdown('<p class="section-header">Jan–Jun 2026 — Live Anomaly Scan (All Stations)</p>', unsafe_allow_html=True)
    all_flags = []
    for stn in ['PS1','PS3','PS5','PS7']:
        for mo, msg, level in detect_anomalies(df_case[df_case['Station'] == stn]):
            all_flags.append({'Station': stn, 'Month': mo, 'Level': level, 'Diagnosis': msg})

    if all_flags:
        for f in all_flags:
            css_f = 'anomaly-flag' if f['Level'] in ('HIGH','MED') else 'insight-box'
            st.markdown(f'<div class="{css_f}"><b>{f["Station"]} — {f["Month"]} 2026</b><br>{f["Diagnosis"]}</div>',
                        unsafe_allow_html=True)
    else:
        st.success("No anomalies detected across all stations for Jan–Jun 2026.")

    st.markdown('<p class="section-header">Anomaly Type Reference Guide</p>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([
        {"Type":"Equipment Degradation",   "EI Effect":"+28%", "Volume":"-3%",  "Runtime":"+5%",  "First Action":"Vibration analysis, inspect impeller"},
        {"Type":"Off-BEP Operation",        "EI Effect":"+22%", "Volume":"-12%", "Runtime":"+12%", "First Action":"Review pump scheduling and VFD settings"},
        {"Type":"Maintenance Period",        "EI Effect":"-5%",  "Volume":"-45%", "Runtime":"-50%", "First Action":"Verify against maintenance log"},
        {"Type":"Power Quality Issue",       "EI Effect":"+18%", "Volume":"0%",   "Runtime":"0%",   "First Action":"Check PF capacitor banks, review KPLC bill"},
        {"Type":"Pump Failure Indicator",    "EI Effect":"+45%", "Volume":"-30%", "Runtime":"+30%", "First Action":"PRIORITY — switch to standby, inspect immediately"},
    ]), use_container_width=True, hide_index=True)

    st.markdown('<p class="section-header">4-Year Anomaly Map (Jul 2022 – Jun 2026)</p>', unsafe_allow_html=True)
    stn2 = st.selectbox("Station", ['PS1','PS3','PS5','PS7'], key='a_stn')
    td   = df_master[df_master['Station'] == stn2].sort_values('Date')
    fig  = go.Figure()
    fig.add_trace(go.Scatter(
        x=td[td['Is_Anomaly']==0]['Date'], y=td[td['Is_Anomaly']==0]['Energy_Intensity_kWh_m3'],
        mode='lines', name='Normal', line=dict(color='#4a9eff', width=1.5)))
    for at, ac in ACOLS.items():
        a = td[td['Anomaly_Type'] == at]
        if not a.empty:
            fig.add_trace(go.Scatter(
                x=a['Date'], y=a['Energy_Intensity_kWh_m3'], mode='markers',
                name=at.replace('_',' '),
                marker=dict(size=14, symbol='star', color=ac, line=dict(width=1, color='white'))))
    fig.add_hline(y=eff_t,   line_dash='dash', line_color='#10b981', annotation_text='Efficient')
    fig.add_hline(y=ineff_t, line_dash='dash', line_color='#ef4444', annotation_text='Inefficient')
    fig.update_layout(title=f'{stn2} — 4-Year EI with Anomaly Markers',
        template='plotly_dark', height=380,
        legend=dict(orientation='h', y=-0.2), margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DATA AUDIT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Data Audit":
    st.markdown("""<div class="kpc-header">
      <h1>Data Audit</h1>
      <p>Data quality checks — completeness, consistency, outlier flags, and statistical summary</p>
    </div>""", unsafe_allow_html=True)

    audit_df = df_master.copy()

    # ── Completeness ────────────────────────────────────────────────────────
    st.markdown('<p class="section-header">1. Completeness Check</p>', unsafe_allow_html=True)
    expected_rows = 48 * 4  # 48 months x 4 stations
    actual_rows   = len(audit_df)
    missing_vals  = audit_df[['Energy_kWh','Volume_m3','Energy_Intensity_kWh_m3']].isnull().sum().sum()
    real_rows     = len(audit_df[audit_df['Data_Source'].str.contains('Actual')])
    synth_rows    = actual_rows - real_rows

    c1,c2,c3,c4 = st.columns(4)
    for col, (val, lbl, color) in zip([c1,c2,c3,c4],[
        (actual_rows,   "Total Records",     "#4a9eff"),
        (real_rows,     "Real Data Rows",    "#10b981"),
        (synth_rows,    "Synthetic Rows",    "#f59e0b"),
        (missing_vals,  "Missing Values",    "#ef4444" if missing_vals > 0 else "#10b981"),
    ]):
        with col:
            st.markdown(f"""<div class="metric-card" style="border-left-color:{color}">
                <div class="metric-value">{val}</div><div class="metric-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    css_c = 'audit-pass' if missing_vals == 0 else 'audit-fail'
    st.markdown(f'<div class="{css_c}">{"PASS" if missing_vals==0 else "FAIL"} — '
                f'{"No missing values in key columns." if missing_vals==0 else f"{missing_vals} missing values found."}'
                '</div>', unsafe_allow_html=True)

    # ── Date coverage ────────────────────────────────────────────────────────
    st.markdown('<p class="section-header">2. Date Coverage</p>', unsafe_allow_html=True)
    for stn in ['PS1','PS3','PS5','PS7']:
        sd = audit_df[audit_df['Station'] == stn]
        n  = len(sd)
        st.markdown(f'<div class="audit-pass">PASS — {stn}: {n} months from {sd["Date"].min().strftime("%b %Y")} '
                    f'to {sd["Date"].max().strftime("%b %Y")}</div>', unsafe_allow_html=True)

    # ── EI range check ───────────────────────────────────────────────────────
    st.markdown('<p class="section-header">3. EI Plausibility Check (0.5 – 8.0 kWh/m3)</p>', unsafe_allow_html=True)
    low_ei  = audit_df[audit_df['Energy_Intensity_kWh_m3'] < 0.5]
    high_ei = audit_df[audit_df['Energy_Intensity_kWh_m3'] > 8.0]
    css_ei  = 'audit-pass' if (len(low_ei) == 0 and len(high_ei) == 0) else 'audit-warn'
    st.markdown(f'<div class="{css_ei}">'
                f'{"PASS — All EI values within plausible range (0.5 – 8.0 kWh/m3)." if len(low_ei)==0 and len(high_ei)==0 else f"WARN — {len(low_ei)} values below 0.5 and {len(high_ei)} values above 8.0 kWh/m3."}'
                '</div>', unsafe_allow_html=True)

    # ── Volume range check ───────────────────────────────────────────────────
    st.markdown('<p class="section-header">4. Volume Plausibility Check</p>', unsafe_allow_html=True)
    low_vol = audit_df[audit_df['Volume_m3'] < 200000]
    st.markdown(f'<div class="{"audit-warn" if len(low_vol)>0 else "audit-pass"}">'
                f'{"WARN — " + str(len(low_vol)) + " months with volume below 200,000 m3 (possible maintenance shutdowns)." if len(low_vol)>0 else "PASS — All monthly volumes above 200,000 m3."}'
                '</div>', unsafe_allow_html=True)
    if len(low_vol) > 0:
        st.dataframe(low_vol[['Date','Station','Volume_m3','Energy_kWh','Energy_Intensity_kWh_m3','Anomaly_Type']],
                     use_container_width=True, hide_index=True)

    # ── Outlier detection ────────────────────────────────────────────────────
    st.markdown('<p class="section-header">5. Statistical Outlier Detection (IQR method)</p>', unsafe_allow_html=True)
    outliers_all = []
    for stn in ['PS1','PS3','PS5','PS7']:
        sd = audit_df[audit_df['Station'] == stn]
        Q1 = sd['Energy_Intensity_kWh_m3'].quantile(0.25)
        Q3 = sd['Energy_Intensity_kWh_m3'].quantile(0.75)
        IQR = Q3 - Q1
        out = sd[(sd['Energy_Intensity_kWh_m3'] < Q1 - 1.5*IQR) |
                 (sd['Energy_Intensity_kWh_m3'] > Q3 + 1.5*IQR)].copy()
        out['IQR_Fence_Low']  = round(Q1 - 1.5*IQR, 3)
        out['IQR_Fence_High'] = round(Q3 + 1.5*IQR, 3)
        outliers_all.append(out)

    outliers = pd.concat(outliers_all)
    if len(outliers) > 0:
        st.markdown(f'<div class="audit-warn">WARN — {len(outliers)} statistical outliers detected (IQR method). Review below.</div>',
                    unsafe_allow_html=True)
        st.dataframe(outliers[['Date','Station','Energy_Intensity_kWh_m3',
                                'IQR_Fence_Low','IQR_Fence_High','Anomaly_Type','Data_Source']].reset_index(drop=True),
                     use_container_width=True, hide_index=True)
    else:
        st.markdown('<div class="audit-pass">PASS — No statistical outliers detected.</div>', unsafe_allow_html=True)

    # ── Statistical summary ──────────────────────────────────────────────────
    st.markdown('<p class="section-header">6. Statistical Summary</p>', unsafe_allow_html=True)
    summary = (audit_df.groupby('Station')['Energy_Intensity_kWh_m3']
               .agg(['count','mean','std','min',
                     lambda x: x.quantile(0.25),
                     'median',
                     lambda x: x.quantile(0.75),
                     'max'])
               .round(4))
    summary.columns = ['N','Mean','Std','Min','Q1','Median','Q3','Max']
    st.dataframe(summary, use_container_width=True)

    # ── EI distribution ──────────────────────────────────────────────────────
    st.markdown('<p class="section-header">7. EI Distribution by Station</p>', unsafe_allow_html=True)
    fig_box = px.box(audit_df, x='Station', y='Energy_Intensity_kWh_m3', color='Station',
        color_discrete_map=STATION_COLORS, template='plotly_dark',
        title='EI Distribution — Jul 2022 to Jun 2026',
        points='all', labels={'Energy_Intensity_kWh_m3':'EI (kWh/m3)'})
    fig_box.add_hline(y=eff_t,   line_dash='dash', line_color='#10b981', annotation_text='Efficient')
    fig_box.add_hline(y=ineff_t, line_dash='dash', line_color='#ef4444', annotation_text='Inefficient')
    fig_box.update_layout(height=380, margin=dict(l=10,r=10,t=50,b=10), showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: MODEL TRAINING
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Model Training":
    st.markdown("""<div class="kpc-header">
      <h1>Model Training — Anomaly Detection</h1>
      <p>Supervised classifier trained on 4-year KPC operational data with TimeSeriesSplit cross-validation</p>
    </div>""", unsafe_allow_html=True)

    try:
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from sklearn.model_selection import TimeSeriesSplit, cross_val_score
        from sklearn.preprocessing import LabelEncoder
        from sklearn.metrics import (roc_auc_score, classification_report,
                                     confusion_matrix, mean_squared_error)
        from scipy.stats import pearsonr
        sklearn_ok = True
    except ImportError:
        sklearn_ok = False
        st.warning("scikit-learn not installed. Run: pip install scikit-learn scipy")

    if sklearn_ok:
        train_df = df_master.copy()
        train_df['Station_Code'] = LabelEncoder().fit_transform(train_df['Station'])
        train_df['Month_Sin'] = np.sin(2 * np.pi * train_df['Month'] / 12)
        train_df['Month_Cos'] = np.cos(2 * np.pi * train_df['Month'] / 12)

        FEATURES = ['Energy_Intensity_kWh_m3','Volume_m3','Energy_kWh',
                    'Runtime_hrs','Flow_Rate_m3hr','Avg_Power_kW',
                    'Power_Factor','Station_Code','Month_Sin','Month_Cos']
        TARGET = 'Is_Anomaly'

        X = train_df[FEATURES].fillna(0)
        y = train_df[TARGET]

        col_cfg, col_res = st.columns([1, 2])
        with col_cfg:
            st.markdown('<p class="section-header">Training Configuration</p>', unsafe_allow_html=True)
            model_choice = st.selectbox("Model", ["Random Forest", "Gradient Boosting"])
            n_folds  = st.slider("CV Folds (TimeSeriesSplit)", 3, 8, 5)
            n_trees  = st.slider("Number of Trees", 50, 500, 100, step=50)
            max_dep  = st.slider("Max Depth", 2, 10, 5)
            test_pct = st.slider("Test Set Size (%)", 10, 40, 20)
            run_btn  = st.button("Train Model", type="primary")

        with col_res:
            if run_btn:
                with st.spinner("Training..."):
                    # Train/test split (time-ordered)
                    split_idx = int(len(X) * (1 - test_pct / 100))
                    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
                    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

                    if model_choice == "Random Forest":
                        clf = RandomForestClassifier(n_estimators=n_trees, max_depth=max_dep,
                                                     random_state=42, class_weight='balanced')
                    else:
                        clf = GradientBoostingClassifier(n_estimators=n_trees, max_depth=max_dep,
                                                          random_state=42)

                    # TimeSeriesSplit CV
                    tscv = TimeSeriesSplit(n_splits=n_folds)
                    cv_scores = cross_val_score(clf, X_train, y_train, cv=tscv,
                                                scoring='roc_auc', n_jobs=-1)
                    clf.fit(X_train, y_train)

                    # Metrics
                    tr_prob = clf.predict_proba(X_train)[:,1]
                    te_prob = clf.predict_proba(X_test)[:,1]
                    tr_auc  = roc_auc_score(y_train, tr_prob) if y_train.nunique() > 1 else float('nan')
                    te_auc  = roc_auc_score(y_test,  te_prob) if y_test.nunique()  > 1 else float('nan')
                    tr_r, _ = pearsonr(y_train, tr_prob) if y_train.nunique() > 1 else (float('nan'), None)
                    te_r, _ = pearsonr(y_test,  te_prob) if y_test.nunique()  > 1 else (float('nan'), None)
                    tr_mse  = mean_squared_error(y_train, tr_prob)
                    te_mse  = mean_squared_error(y_test,  te_prob)

                    # Store in session
                    st.session_state['trained_model']   = clf
                    st.session_state['feature_names']   = FEATURES
                    st.session_state['model_metrics']   = dict(
                        tr_auc=tr_auc, te_auc=te_auc,
                        cv_mean=cv_scores.mean(), cv_std=cv_scores.std(),
                        tr_r=tr_r, te_r=te_r, tr_mse=tr_mse, te_mse=te_mse,
                        n_train=len(X_train), n_test=len(X_test), n_folds=n_folds)

                    # Display metrics
                    st.markdown('<p class="section-header">Model Report Card</p>', unsafe_allow_html=True)
                    mc1,mc2,mc3,mc4 = st.columns(4)
                    for c,(v,l,col) in zip([mc1,mc2,mc3,mc4],[
                        (f"{te_auc:.4f}", "Test AUC", "#10b981" if te_auc>=0.85 else "#f59e0b"),
                        (f"{cv_scores.mean():.4f} +/-{cv_scores.std():.4f}",
                         f"CV AUC ({n_folds}-fold)", "#4a9eff"),
                        (f"{te_r:.4f}" if not np.isnan(te_r) else "N/A", "Test Pearson R", "#c084fc"),
                        (f"{te_mse:.4f}", "Test MSE", "#f59e0b"),
                    ]):
                        with c:
                            st.markdown(f"""<div class="metric-card" style="border-left-color:{col}">
                                <div class="metric-value" style="font-size:1.2rem">{v}</div>
                                <div class="metric-label">{l}</div>
                            </div>""", unsafe_allow_html=True)

                    # Feature importance
                    fi = pd.DataFrame({'Feature': FEATURES,
                                       'Importance': clf.feature_importances_}).sort_values(
                        'Importance', ascending=True)
                    fig_fi = go.Figure(go.Bar(
                        y=fi['Feature'], x=fi['Importance'], orientation='h',
                        marker_color='#4a9eff',
                        text=[f"{v:.3f}" for v in fi['Importance']], textposition='outside'))
                    fig_fi.update_layout(title='Feature Importance', template='plotly_dark',
                        height=350, margin=dict(l=10,r=10,t=50,b=10))
                    st.plotly_chart(fig_fi, use_container_width=True)

                    # CV fold chart
                    fold_labels = [f"Fold {i+1}" for i in range(n_folds)]
                    fig_cv = go.Figure(go.Bar(
                        x=fold_labels, y=cv_scores,
                        marker_color=['#10b981' if v >= 0.8 else '#f59e0b' for v in cv_scores],
                        text=[f"{v:.3f}" for v in cv_scores], textposition='outside'))
                    fig_cv.add_hline(y=cv_scores.mean(), line_dash='dash', line_color='#4a9eff',
                        annotation_text=f'Mean {cv_scores.mean():.3f}')
                    fig_cv.update_layout(title=f'AUC per CV Fold ({n_folds}-fold TimeSeriesSplit)',
                        template='plotly_dark', height=280, yaxis=dict(range=[0,1.1]),
                        margin=dict(l=10,r=10,t=50,b=10))
                    st.plotly_chart(fig_cv, use_container_width=True)

                    # Train / Test summary
                    st.markdown(f"""<div class="insight-box">
                    <b>Training summary:</b> {len(X_train)} training rows | {len(X_test)} test rows
                    | Anomaly rate: {y_train.mean():.1%} (train) / {y_test.mean():.1%} (test)<br>
                    Train AUC: <b>{tr_auc:.4f}</b> | Test AUC: <b>{te_auc:.4f}</b> |
                    Overfit gap: <b>{(tr_auc-te_auc):.4f}</b>
                    {"(acceptable)" if abs(tr_auc-te_auc)<0.10 else "(review — possible overfitting)"}
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("Configure training parameters on the left and click Train Model.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PREDICTION
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Prediction":
    st.markdown("""<div class="kpc-header">
      <h1>Prediction</h1>
      <p>Enter new operational readings to predict EI and anomaly probability</p>
    </div>""", unsafe_allow_html=True)

    if 'trained_model' not in st.session_state:
        st.warning("No trained model found. Go to the Model Training page and train a model first.")
    else:
        clf      = st.session_state['trained_model']
        features = st.session_state['feature_names']
        metrics  = st.session_state.get('model_metrics', {})

        st.markdown('<p class="section-header">Enter New Reading</p>', unsafe_allow_html=True)
        col_in, col_out = st.columns([1, 2])
        with col_in:
            pred_stn  = st.selectbox("Station", ['PS1','PS3','PS5','PS7'])
            pred_vol  = st.number_input("Volume (m3)", value=760000.0, step=10000.0, format="%.0f")
            pred_kwh  = st.number_input("Energy (kWh)", value=2200000.0, step=10000.0, format="%.0f")
            pred_rt   = st.number_input("Runtime (hrs)", value=2700.0, step=50.0, format="%.0f")
            pred_pf   = st.number_input("Power Factor", value=0.95, step=0.01, min_value=0.5, max_value=1.0, format="%.3f")
            pred_mon  = st.slider("Month", 1, 12, 6)
            predict_btn = st.button("Predict", type="primary")

        with col_out:
            if predict_btn:
                from sklearn.preprocessing import LabelEncoder
                le = LabelEncoder().fit(['PS1','PS3','PS5','PS7'])
                stn_code = le.transform([pred_stn])[0]
                ei_val   = pred_kwh / pred_vol if pred_vol > 0 else 0
                flow_val = pred_vol / pred_rt  if pred_rt  > 0 else 0
                pwr_val  = pred_kwh / pred_rt  if pred_rt  > 0 else 0
                mon_sin  = np.sin(2 * np.pi * pred_mon / 12)
                mon_cos  = np.cos(2 * np.pi * pred_mon / 12)

                X_pred = pd.DataFrame([{
                    'Energy_Intensity_kWh_m3': ei_val,
                    'Volume_m3':               pred_vol,
                    'Energy_kWh':              pred_kwh,
                    'Runtime_hrs':             pred_rt,
                    'Flow_Rate_m3hr':          flow_val,
                    'Avg_Power_kW':            pwr_val,
                    'Power_Factor':            pred_pf,
                    'Station_Code':            stn_code,
                    'Month_Sin':               mon_sin,
                    'Month_Cos':               mon_cos,
                }])

                prob     = clf.predict_proba(X_pred)[0][1]
                label    = clf.predict(X_pred)[0]
                ei_class = classify(ei_val, eff_t, ineff_t)
                css_ei   = "tl-green" if ei_class=="Efficient" else ("tl-yellow" if ei_class=="Moderate" else "tl-red")
                css_prob = "tl-red" if prob > 0.7 else ("tl-yellow" if prob > 0.4 else "tl-green")

                st.markdown('<p class="section-header">Prediction Result</p>', unsafe_allow_html=True)
                r1,r2,r3 = st.columns(3)
                with r1:
                    st.markdown(f"""<div class="{css_ei}">
                        <div style="font-size:0.8rem;color:#d1d5db;font-weight:600">PREDICTED EI</div>
                        <div style="font-size:2rem;font-weight:700;color:#fff">{ei_val:.3f}</div>
                        <div style="font-size:0.72rem;color:#d1d5db">kWh/m3 — {ei_class}</div>
                    </div>""", unsafe_allow_html=True)
                with r2:
                    st.markdown(f"""<div class="{css_prob}">
                        <div style="font-size:0.8rem;color:#d1d5db;font-weight:600">ANOMALY PROBABILITY</div>
                        <div style="font-size:2rem;font-weight:700;color:#fff">{prob:.1%}</div>
                        <div style="font-size:0.72rem;color:#d1d5db">{"HIGH RISK" if prob>0.7 else ("MODERATE" if prob>0.4 else "LOW RISK")}</div>
                    </div>""", unsafe_allow_html=True)
                with r3:
                    st.markdown(f"""<div class="metric-card">
                        <div style="font-size:0.8rem;color:#d1d5db;font-weight:600">ESTIMATED COST</div>
                        <div style="font-size:1.8rem;font-weight:700;color:#fff">KShs {pred_kwh*tariff/1e6:.2f}M</div>
                        <div style="font-size:0.72rem;color:#d1d5db">@ KShs {tariff}/kWh</div>
                    </div>""", unsafe_allow_html=True)

                # Interpretation
                advice = ""
                avg_ei_ref_val = df_master[df_master['Station']==pred_stn]['Energy_Intensity_kWh_m3'].quantile(0.75)
                if prob > 0.7:
                    if ei_val > avg_ei_ref_val:
                        advice = "EI is above the 75th percentile for this station. Likely Equipment Degradation or Off-BEP Operation. Schedule inspection."
                    else:
                        advice = "Anomaly signal detected. Check power quality — low power factor or voltage sag may be increasing consumption."
                elif prob > 0.4:
                    advice = "Moderate anomaly signal. Monitor over next 2–4 weeks. Compare against same month in prior years."
                else:
                    advice = "Operating within expected range. Continue standard monitoring cycle."

                css_adv = 'anomaly-flag' if prob > 0.7 else ('data-note' if prob > 0.4 else 'cost-box')
                st.markdown(f'<div class="{css_adv}"><b>Recommendation:</b> {advice}</div>',
                            unsafe_allow_html=True)

                # Gauge chart
                fig_g = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=prob * 100,
                    title={'text': "Anomaly Probability (%)"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar':  {'color': '#ef4444' if prob > 0.7 else ('#f59e0b' if prob > 0.4 else '#10b981')},
                        'steps': [
                            {'range': [0, 40],  'color': '#064e3b'},
                            {'range': [40, 70], 'color': '#451a03'},
                            {'range': [70, 100],'color': '#450a0a'},
                        ],
                        'threshold': {'line': {'color': 'white', 'width': 2}, 'value': 70},
                    }))
                fig_g.update_layout(template='plotly_dark', height=300,
                    margin=dict(l=20,r=20,t=60,b=20))
                st.plotly_chart(fig_g, use_container_width=True)

                # Feature inputs vs training range
                st.markdown('<p class="section-header">Your Input vs Training Range</p>', unsafe_allow_html=True)
                stn_train = df_master[df_master['Station'] == pred_stn]
                comp_data = {
                    'Metric':  ['EI (kWh/m3)',       'Volume (m3)',       'Power Factor'],
                    'Input':   [round(ei_val,3),      pred_vol,            pred_pf],
                    'Train Min':[stn_train['Energy_Intensity_kWh_m3'].min(),
                                 stn_train['Volume_m3'].min(),
                                 stn_train['Power_Factor'].min()],
                    'Train Mean':[stn_train['Energy_Intensity_kWh_m3'].mean(),
                                  stn_train['Volume_m3'].mean(),
                                  stn_train['Power_Factor'].mean()],
                    'Train Max':[stn_train['Energy_Intensity_kWh_m3'].max(),
                                 stn_train['Volume_m3'].max(),
                                 stn_train['Power_Factor'].max()],
                }
                st.dataframe(pd.DataFrame(comp_data).round(3), use_container_width=True, hide_index=True)
            else:
                st.info("Enter operational readings on the left and click Predict.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: WHAT-IF SIMULATOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "What-If Simulator":
    st.markdown("""<div class="kpc-header">
      <h1>What-If Simulator</h1>
      <p>Estimate energy consumption and cost under different operating scenarios</p>
    </div>""", unsafe_allow_html=True)

    col_in, col_out = st.columns([1, 2])
    with col_in:
        sim_stn   = st.selectbox("Station", ['PS1','PS3','PS5','PS7'])
        sim_vol   = st.slider("Target throughput (m3/month)", 400000, 1000000, 760000, step=10000, format="%d")
        base_ei_v = df_case[df_case['Station']==sim_stn]['Energy_Intensity_kWh_m3'].mean()
        sim_ei    = st.slider("Target EI (kWh/m3)", 2.0, 6.0, float(round(base_ei_v, 2)), step=0.05, format="%.2f")
        sim_hrs   = st.slider("Planned runtime (hrs/month)", 500, 3500, 2700, step=50)
        sim_mo    = st.slider("Projection (months)", 1, 12, 6)
        st.divider()
        st.info(f"Current avg EI: **{base_ei_v:.3f} kWh/m3**")

    with col_out:
        proj_kwh  = sim_ei * sim_vol * sim_mo
        base_kwh  = base_ei_v * sim_vol * sim_mo
        saving_kwh= base_kwh - proj_kwh
        saving_ksh= saving_kwh * tariff
        r1,r2,r3 = st.columns(3)
        for col, (val, lbl, color) in zip([r1,r2,r3],[
            (f"{proj_kwh/1e6:.2f}M",        "Projected Energy (kWh)",  "#4a9eff"),
            (f"KShs {proj_kwh*tariff/1e6:.2f}M", "Projected Cost",     "#f59e0b"),
            (f"{sim_vol/sim_hrs:.0f}",        "Flow Rate (m3/hr)",      "#10b981"),
        ]):
            with col:
                st.markdown(f"""<div class="metric-card" style="border-left-color:{color}">
                    <div class="metric-value">{val}</div><div class="metric-label">{lbl}</div>
                </div>""", unsafe_allow_html=True)

        if abs(saving_kwh) > 0:
            css_s = "cost-box" if saving_kwh > 0 else "anomaly-flag"
            direction = "saving" if saving_kwh > 0 else "additional cost"
            st.markdown(f"""<div class="{css_s}">
            vs current average EI ({base_ei_v:.3f} kWh/m3): projected <b>{direction}</b> of
            <b>{abs(saving_kwh)/1e3:.0f}k kWh</b> over {sim_mo} months = <b>KShs {abs(saving_ksh)/1e3:.0f}k</b>
            </div>""", unsafe_allow_html=True)

        months_list = [f"M{i+1}" for i in range(sim_mo)]
        monthly_kwh = [sim_ei * sim_vol] * sim_mo
        monthly_cost = [x * tariff for x in monthly_kwh]
        fig_proj = make_subplots(specs=[[{"secondary_y": True}]])
        fig_proj.add_trace(go.Bar(x=months_list, y=[x/1e6 for x in monthly_kwh],
            name='Energy (M kWh)', marker_color=STATION_COLORS[sim_stn], opacity=0.8), secondary_y=False)
        fig_proj.add_trace(go.Scatter(x=months_list, y=[x/1e6 for x in monthly_cost],
            name='Cost (M KShs)', mode='lines+markers',
            line=dict(color='#f5a623', width=2), marker=dict(size=7)), secondary_y=True)
        fig_proj.update_layout(title=f'{sim_stn} — {sim_mo}-Month Projection at {sim_ei:.2f} kWh/m3',
            template='plotly_dark', height=320,
            legend=dict(orientation='h', y=1.02),
            margin=dict(l=10, r=10, t=50, b=10))
        fig_proj.update_yaxes(title_text='Energy (M kWh)', secondary_y=False)
        fig_proj.update_yaxes(title_text='Cost (M KShs)', secondary_y=True)
        st.plotly_chart(fig_proj, use_container_width=True)

        # Scenario comparison
        st.markdown('<p class="section-header">Scenario Comparison</p>', unsafe_allow_html=True)
        scenarios = pd.DataFrame({
            'Scenario': ['Baseline (current avg)', 'Target (this simulation)',
                         'Best on record', 'Worst on record'],
            'EI (kWh/m3)': [
                round(base_ei_v, 3), round(sim_ei, 3),
                round(df_case[df_case['Station']==sim_stn]['Energy_Intensity_kWh_m3'].min(), 3),
                round(df_case[df_case['Station']==sim_stn]['Energy_Intensity_kWh_m3'].max(), 3),
            ],
        })
        scenarios[f'Monthly Energy (kWh @ {sim_vol:,.0f} m3)'] = (
            (scenarios['EI (kWh/m3)'] * sim_vol).round().astype(int))
        scenarios['Monthly Cost (KShs)'] = (
            (scenarios['EI (kWh/m3)'] * sim_vol * tariff).round().astype(int))
        st.dataframe(scenarios, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: COST ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Cost Analysis":
    st.markdown("""<div class="kpc-header">
      <h1>Cost Analysis</h1>
      <p>KPLC electricity cost breakdown — Jan to Jun 2026</p>
    </div>""", unsafe_allow_html=True)

    total_cost = df_case['Cost_KShs'].sum()
    avg_monthly = total_cost / 6
    cost_per_m3 = total_cost / df_case['Volume_m3'].sum()

    c1,c2,c3,c4 = st.columns(4)
    for col, (val, lbl, color) in zip([c1,c2,c3,c4],[
        (f"KShs {total_cost/1e6:.2f}M",   "Total Cost Jan–Jun 2026", "#ef4444"),
        (f"KShs {avg_monthly/1e6:.2f}M",  "Avg Monthly Cost",        "#f59e0b"),
        (f"KShs {cost_per_m3:.2f}",        "Cost per m3 Pumped",      "#4a9eff"),
        (f"KShs {tariff:.1f}/kWh",         "KPLC Blended Tariff",     "#10b981"),
    ]):
        with col:
            st.markdown(f"""<div class="metric-card" style="border-left-color:{color}">
                <div class="metric-value">{val}</div><div class="metric-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    col_bar, col_pie = st.columns(2)
    with col_bar:
        cost_by_stn = (df_case.groupby('Station')['Cost_KShs'].sum().reset_index()
                       .sort_values('Cost_KShs'))
        fig = go.Figure(go.Bar(
            y=cost_by_stn['Station'], x=cost_by_stn['Cost_KShs']/1e6,
            orientation='h',
            marker_color=[STATION_COLORS[s] for s in cost_by_stn['Station']],
            text=[f"KShs {v/1e6:.2f}M" for v in cost_by_stn['Cost_KShs']],
            textposition='outside'))
        fig.update_layout(title='Total Cost by Station (Jan–Jun 2026)',
            template='plotly_dark', height=300, xaxis_title='Cost (M KShs)',
            margin=dict(l=10,r=10,t=50,b=10))
        st.plotly_chart(fig, use_container_width=True)
    with col_pie:
        fig2 = px.pie(cost_by_stn, names='Station', values='Cost_KShs',
            color='Station', color_discrete_map=STATION_COLORS,
            title='Cost Share by Station', template='plotly_dark', hole=0.45)
        fig2.update_layout(height=300, margin=dict(l=10,r=10,t=50,b=10))
        st.plotly_chart(fig2, use_container_width=True)

    # Monthly trend
    cost_monthly = (df_case.groupby(['Month','Station'])['Cost_KShs']
                    .sum().reset_index())
    fig3 = px.bar(cost_monthly, x='Month', y='Cost_KShs', color='Station',
        color_discrete_map=STATION_COLORS,
        title='Monthly Cost Breakdown by Station',
        template='plotly_dark', barmode='stack',
        category_orders={'Month': MONTHS},
        labels={'Cost_KShs': 'Cost (KShs)'})
    fig3.update_yaxes(tickformat=',')
    fig3.update_layout(height=320, margin=dict(l=10,r=10,t=50,b=10))
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<p class="section-header">Detailed Cost Table</p>', unsafe_allow_html=True)
    cost_tbl = (df_case.pivot_table(index='Station', columns='Month', values='Cost_KShs',
                                    aggfunc='sum').reindex(columns=MONTHS))
    cost_tbl['Total (Jan-Jun)'] = cost_tbl.sum(axis=1)
    cost_tbl = cost_tbl.applymap(lambda x: f"KShs {x:,.0f}" if pd.notna(x) else "—")
    st.dataframe(cost_tbl, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ML MODEL PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "ML Model Performance":
    st.markdown("""<div class="kpc-header">
      <h1>ML Model Performance</h1>
      <p>Supervised anomaly detection — model evaluation metrics and plain-English explanation</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="data-note">
    Enter your trained model metrics below — or train a model on the Model Training page
    and the metrics will appear here automatically.
    </div>""", unsafe_allow_html=True)

    # Pre-fill from session if available
    saved = st.session_state.get('model_metrics', {})

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        train_auc = st.number_input("Train AUC",     value=float(saved.get('tr_auc', 1.0000)), format="%.4f")
        test_auc  = st.number_input("Test AUC",      value=float(saved.get('te_auc', 0.9687)), format="%.4f")
        cv_auc    = st.number_input("CV AUC (mean)", value=float(saved.get('cv_mean',0.8876)), format="%.4f")
        cv_std    = st.number_input("CV AUC (std)",  value=float(saved.get('cv_std', 0.0774)), format="%.4f")
    with col_m2:
        train_r   = st.number_input("Train Pearson R", value=float(saved.get('tr_r', 0.7784)), format="%.4f")
        test_r    = st.number_input("Test Pearson R",  value=float(saved.get('te_r', 0.7281)), format="%.4f")
        n_folds   = st.number_input("CV Folds", value=int(saved.get('n_folds', 5)), min_value=2, max_value=10, step=1)
    with col_m3:
        train_mse = st.number_input("Train MSE", value=float(saved.get('tr_mse', 0.1345)), format="%.4f")
        test_mse  = st.number_input("Test MSE",  value=float(saved.get('te_mse', 0.1284)), format="%.4f")

    overfitting = train_auc - test_auc
    g_label = ("Excellent" if test_auc >= 0.97 else ("Very Good" if test_auc >= 0.90
               else ("Good" if test_auc >= 0.80 else "Needs Improvement")))
    g_css   = "tl-green" if test_auc >= 0.90 else ("tl-yellow" if test_auc >= 0.80 else "tl-red")
    of_css  = "tl-green" if overfitting < 0.05 else ("tl-yellow" if overfitting < 0.15 else "tl-red")
    r_grade = "Strong" if test_r >= 0.7 else ("Moderate" if test_r >= 0.5 else "Weak")
    r_css   = "tl-green" if test_r >= 0.7 else ("tl-yellow" if test_r >= 0.5 else "tl-red")
    mse_css = "tl-green" if test_mse <= train_mse else "tl-yellow"

    st.markdown('<p class="section-header">Model Report Card</p>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="{g_css}">
            <div style="font-size:0.8rem;color:#d1d5db;font-weight:600">TEST AUC</div>
            <div style="font-size:2rem;font-weight:700;color:#fff">{test_auc:.4f}</div>
            <div style="font-size:0.72rem;color:#d1d5db">{g_label}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="{of_css}">
            <div style="font-size:0.8rem;color:#d1d5db;font-weight:600">OVERFIT GAP</div>
            <div style="font-size:2rem;font-weight:700;color:#fff">{overfitting:.4f}</div>
            <div style="font-size:0.72rem;color:#d1d5db">{"Acceptable" if overfitting<0.05 else ("Moderate" if overfitting<0.15 else "High")}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="{r_css}">
            <div style="font-size:0.8rem;color:#d1d5db;font-weight:600">TEST PEARSON R</div>
            <div style="font-size:2rem;font-weight:700;color:#fff">{test_r:.4f}</div>
            <div style="font-size:0.72rem;color:#d1d5db">{r_grade} correlation</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="{mse_css}">
            <div style="font-size:0.8rem;color:#d1d5db;font-weight:600">TEST MSE</div>
            <div style="font-size:2rem;font-weight:700;color:#fff">{test_mse:.4f}</div>
            <div style="font-size:0.72rem;color:#d1d5db">{"Test <= Train (good)" if test_mse<=train_mse else "Test > Train (watch)"}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<p class="section-header">Plain-English Explanations</p>', unsafe_allow_html=True)
    for title, body in [
        ("AUC — Area Under the ROC Curve",
         f"Imagine ranking all months from most to least likely to be anomalous. AUC measures how often the model "
         f"correctly ranks a real anomaly above a normal month. Your test AUC of **{test_auc:.4f}** means the model "
         f"gets this right **{test_auc*100:.1f}%** of the time on data it has never seen — rated **{g_label.lower()}**."),

        (f"Cross-Validation AUC — {cv_auc:.4f} +/- {cv_std:.4f} ({int(n_folds)}-fold TimeSeriesSplit)",
         f"The {int(n_folds)}-fold TimeSeriesSplit trains on older data and tests on newer data each fold, "
         f"preventing data leakage. Mean CV AUC of **{cv_auc:.4f}** with spread **+/-{cv_std:.4f}** shows the model is "
         f"{'consistent across time periods' if cv_std < 0.10 else 'variable — consider more labelled training data'}."),

        ("Pearson R — Predicted Probability vs Actual Severity",
         f"Test Pearson R of **{test_r:.4f}** is **{r_grade.lower()}** — the model's confidence scores "
         f"reliably rank months by actual operational severity."),

        ("MSE — Mean Squared Error",
         f"{'Test MSE (**' + str(round(test_mse,4)) + '**) is lower than Train MSE (**' + str(round(train_mse,4)) + '**) — the model generalises well.' if test_mse<=train_mse else 'Test MSE is higher than Train MSE — mild overfitting; normal for small labelled datasets.'}"),
    ]:
        with st.expander(title, expanded=True):
            st.markdown(body)

    st.markdown('<p class="section-header">Summary Statement for Report</p>', unsafe_allow_html=True)
    st.markdown(f"""<div class="insight-box">
    The anomaly detection model achieved a test AUC of <b>{test_auc:.4f}</b>, indicating {g_label.lower()}
    discrimination between normal and anomalous pumping station operations on unseen data.
    The {int(n_folds)}-fold TimeSeriesSplit cross-validation yielded a mean AUC of
    <b>{cv_auc:.4f} +/- {cv_std:.4f}</b>, confirming the model generalises consistently
    across different time periods without data leakage. The Pearson correlation between
    predicted anomaly probabilities and actual labels was <b>{test_r:.4f}</b> on the test set ({r_grade.lower()}).
    Train MSE: {train_mse:.4f} | Test MSE: {test_mse:.4f}
    {"— test MSE is lower, confirming no overfitting to noise." if test_mse<=train_mse else "."}
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 4-YEAR TRAINING DATA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "4-Year Training Data":
    st.markdown("""<div class="kpc-header">
      <h1>4-Year Training Dataset</h1>
      <p>Jul 2022 – Jun 2026 | Real ML5 throughput | Real energy (2026) + modelled energy (pre-2026)</p>
    </div>""", unsafe_allow_html=True)

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        stn_filter = st.multiselect("Station", ['PS1','PS3','PS5','PS7'],
                                    default=['PS1','PS3','PS5','PS7'])
    with col_f2:
        at_filter  = st.multiselect("Anomaly Type",
                                    ['Normal','Equipment_Degradation','Off_BEP_Operation',
                                     'Maintenance_Period','Power_Quality_Issue','Pump_Failure_Indicator'],
                                    default=['Normal','Equipment_Degradation','Off_BEP_Operation',
                                             'Maintenance_Period','Power_Quality_Issue','Pump_Failure_Indicator'])

    show_df = df_master[(df_master['Station'].isin(stn_filter)) &
                         (df_master['Anomaly_Type'].isin(at_filter))].copy()

    c1,c2,c3,c4 = st.columns(4)
    for col, (val, lbl, color) in zip([c1,c2,c3,c4],[
        (len(show_df),               "Records",          "#4a9eff"),
        (show_df['Is_Anomaly'].sum(), "Labelled Anomalies", "#ef4444"),
        (f"{show_df['Energy_Intensity_kWh_m3'].mean():.3f}", "Avg EI (kWh/m3)", "#10b981"),
        (f"{show_df['Volume_m3'].mean()/1e3:.0f}k", "Avg Monthly Vol (m3)", "#c084fc"),
    ]):
        with col:
            st.markdown(f"""<div class="metric-card" style="border-left-color:{color}">
                <div class="metric-value">{val}</div><div class="metric-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    # EI trend all stations
    fig = go.Figure()
    for stn in stn_filter:
        sd = show_df[show_df['Station'] == stn].sort_values('Date')
        fig.add_trace(go.Scatter(x=sd['Date'], y=sd['Energy_Intensity_kWh_m3'],
            name=stn, mode='lines', line=dict(color=STATION_COLORS.get(stn,'#fff'), width=1.5)))
        anom = sd[sd['Is_Anomaly'] == 1]
        if not anom.empty:
            fig.add_trace(go.Scatter(x=anom['Date'], y=anom['Energy_Intensity_kWh_m3'],
                mode='markers', name=f'{stn} anomaly',
                marker=dict(size=10, symbol='star', color=STATION_COLORS.get(stn,'#fff'),
                            line=dict(width=1, color='white')), showlegend=False))
    fig.add_hline(y=eff_t,   line_dash='dash', line_color='#10b981')
    fig.add_hline(y=ineff_t, line_dash='dash', line_color='#ef4444')
    fig.update_layout(title='4-Year EI Trend with Anomaly Markers',
        template='plotly_dark', height=360,
        legend=dict(orientation='h', y=-0.15),
        margin=dict(l=10,r=10,t=50,b=10))
    st.plotly_chart(fig, use_container_width=True)

    # Volume trend
    fig_v = px.line(show_df, x='Date', y='Volume_m3', color='Station',
        color_discrete_map=STATION_COLORS,
        title='Monthly ML5 Mainline Throughput Volume', template='plotly_dark',
        labels={'Volume_m3': 'Volume (m3)'})
    fig_v.update_layout(height=280, margin=dict(l=10,r=10,t=50,b=10))
    st.plotly_chart(fig_v, use_container_width=True)

    st.markdown('<p class="section-header">Data Table</p>', unsafe_allow_html=True)
    display_cols = ['Date','Station','Energy_kWh','Volume_m3','Energy_Intensity_kWh_m3',
                    'Efficiency_Class','Power_Factor','Cost_KShs','Is_Anomaly','Anomaly_Type','Data_Source']
    st.dataframe(
        show_df[display_cols].reset_index(drop=True).style.applymap(
            color_cls, subset=['Efficiency_Class']),
        use_container_width=True, height=350)

    buf = io.BytesIO()
    show_df.to_csv(buf, index=False)
    st.download_button("Download filtered dataset (CSV)", buf.getvalue(),
                       "kpc_master_dataset.csv", "text/csv")


# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    f"KPC Energy Intensity Benchmarking | EI = kWh / m3 | "
    f"Efficient < {eff_t} | Moderate {eff_t}–{ineff_t} | Inefficient > {ineff_t} kWh/m3 | "
    f"Tariff: KShs {tariff}/kWh | Energy: Actual KPLC Billing Jan–Jun 2026 | "
    f"Volume: Real ML5 Mainline Throughput | "
    "Capstone Project | Dorothy Lizz Odoyo | 221883 | Strathmore University 2026"
)
