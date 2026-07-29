"""
Kenya Pipeline Company — Energy Intensity Benchmarking Dashboard
Pumping Stations: PS1, PS3, PS5, PS7 | Jul 2022 – Jun 2026
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
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Font: Bookman Old Style ── */
  @import url('https://fonts.googleapis.com/css2?family=IM+Fell+English:ital@0;1&display=swap');
  html, body, [class*="css"], .stApp, .stMarkdown, p, div, span, label, h1, h2, h3, h4, button {
    font-family: 'Bookman Old Style', 'BookmanOldStyle', 'Bookman', 'URW Bookman L', Georgia, serif !important;
  }

  /* ── Main background: white ── */
  .stApp { background-color: #F5F5F5 !important; }
  .block-container { background-color: #FFFFFF !important; border-radius: 8px; padding: 2rem 2rem 2rem !important; }

  /* ── Sidebar: user pipeline image + dark/red overlay ── */
  [data-testid="stSidebar"] {
    background-image:
      linear-gradient(rgba(0,0,0,0.68), rgba(150,0,0,0.50)),
      url('data:image/jpeg;base64,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') !important;
    background-size: cover !important;
    background-position: center !important;
  }
  /* Target only text-bearing elements — NOT all divs (fixes overlap) */
  [data-testid="stSidebar"] label { color: #FFFFFF !important; }
  [data-testid="stSidebar"] p { color: #FFFFFF !important; }
  [data-testid="stSidebar"] span { color: #FFFFFF !important; }
  [data-testid="stSidebar"] .stRadio label { color: #FFFFFF !important; }
  [data-testid="stSidebar"] .stMarkdown p { color: #FFFFFF !important; }
  [data-testid="stSidebar"] small { color: #FFE0E0 !important; }
  [data-testid="stSidebar"] .stNumberInput input { background: rgba(255,255,255,0.18) !important; color:#fff !important; border:1px solid rgba(255,255,255,0.3) !important; }
  [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.25) !important; }

  /* ── KPC Header banner: black + red accent ── */
  .kpc-header {
    background: linear-gradient(90deg, #1a1a1a 0%, #2d2d2d 60%, #8B0000 100%);
    padding: 20px 28px; border-radius: 10px; margin-bottom: 16px;
    border-left: 6px solid #CC0000;
    box-shadow: 0 3px 12px rgba(0,0,0,0.18);
  }
  .kpc-header h1 { color: #FFFFFF; font-size: 1.45rem; margin: 0; font-weight: 700; letter-spacing: 0.5px; }
  .kpc-header p  { color: #D0D0D0; font-size: 0.82rem; margin: 6px 0 0; }

  /* ── Metric cards: white + grey shadow + red/black accent ── */
  .metric-card {
    background: #FFFFFF; border-radius: 10px; padding: 16px;
    border-left: 5px solid #CC0000; margin-bottom: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
  }
  .metric-value { font-size: 1.7rem; font-weight: 700; color: #1a1a1a; }
  .metric-label { font-size: 0.76rem; color: #666666; margin-top: 4px; }

  /* ── Traffic-light status cards (original EI green/amber/red) ── */
  .tl-green  { background: linear-gradient(135deg,#064e3b,#065f46); border-left:4px solid #10b981; border-radius:10px; padding:14px; }
  .tl-yellow { background: linear-gradient(135deg,#451a03,#78350f); border-left:4px solid #f59e0b; border-radius:10px; padding:14px; }
  .tl-red    { background: linear-gradient(135deg,#450a0a,#7f1d1d); border-left:4px solid #ef4444; border-radius:10px; padding:14px; }
  .tl-green  div { color: #ffffff !important; }
  .tl-yellow div { color: #ffffff !important; }
  .tl-red    div { color: #ffffff !important; }

  /* ── Info/insight boxes ── */
  .insight-box {
    background: #F7F7F7; border-left: 3px solid #333333;
    padding: 12px 16px; border-radius: 6px; font-size: 0.83rem; color: #1a1a1a; margin: 8px 0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }
  .anomaly-flag {
    background: #FFF1F2; border-left: 4px solid #CC0000;
    padding: 10px 14px; border-radius: 6px; font-size: 0.83rem; color: #7f1d1d; margin: 6px 0;
  }
  .cost-box {
    background: #F0FDF4; border-left: 4px solid #10b981;
    padding: 12px 16px; border-radius: 6px; font-size: 0.83rem; color: #14532d; margin: 8px 0;
  }
  .section-header {
    font-size: 1.05rem; font-weight: 700; color: #1a1a1a;
    margin: 20px 0 10px; border-bottom: 3px solid #CC0000; padding-bottom: 6px;
  }
  .data-note {
    background: #F5F5F5; border-left: 4px solid #888888;
    padding: 10px 14px; border-radius: 6px; font-size: 0.79rem; color: #444444;
  }

  /* ── KPC Logo box in sidebar ── */
  .kpc-logo-box {
    background: rgba(204,0,0,0.7); border-radius: 8px; padding: 12px 14px;
    text-align: center; margin-bottom: 8px; border: 1px solid rgba(255,255,255,0.2);
  }
  .kpc-logo-box .logo-title { font-size: 1.2rem; font-weight: 800; color: #FFFFFF; letter-spacing: 3px; }
  .kpc-logo-box .logo-sub   { font-size: 0.7rem; color: #FFE0E0; margin-top: 3px; }

  /* ── Pipeline route badge ── */
  .route-badge {
    background: #1a1a1a; color: #FFFFFF; border-radius: 20px;
    padding: 5px 14px; font-size: 0.78rem; font-weight: 600; display: inline-block; margin: 3px 2px;
    border: 1px solid #CC0000;
  }

  /* ── Dataframe / table tweaks ── */
  .stDataFrame { border: 1px solid #E0E0E0 !important; border-radius: 8px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
EFFICIENT_T    = 3.0
INEFFICIENT_T  = 4.0
STATION_COLORS = {"PS1":"#CC0000","PS3":"#555555","PS5":"#8B0000","PS7":"#888888"}
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
    st.markdown(f"""<div class="kpc-logo-box">
        <img src="data:image/png;base64,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A89CrA7I4JG///77L1y48Jxzznnf+973lre85R3veMe73/3u+fPnA2iQjTSeHquEV4je3tyPfvSjOImjRt2vVmbM3Egc3YxD3JjSOhMO6BDaraS7SzG8eEaK/TWqoxuJswZDynPHWq3QmOmbbIqXkii5+eabOSxIkixbwqlorY888kgasR+0cuXKxx577FOf+lRfX1/nHrEcuAF2VHffffdHHnmk3W7zpezuu+/uRCvAd9FFFzGx2WzSDkoWLVo0NDQE/r73ve91JIOSr371q8cffzyeCdD09vYiDer4Hsdx4IEdytDyP//zP0899dTVV1/9iU984j3vec/b3va2D33oQxdccMEpp5zyhS984eGHH77yqqve9o63b7PttilOR2R4pH3bHXe4rmccJZXyRpttYj2Pz0fcO6iK8aBEaxboVuoYrJu0UwqvQ+CxSoAUmsEbJZxVhjb1edPpqTBAcv7Pf3G57wflchH/kQ0zZnR0FBuTZFDFnPih4eFh3Ax2pQUeV4T/mD59+s9+9rPFixfTDgpf97rXATsGACDgBcMYQAMmACLTfd93XReo4X7wWIcddtgXv/hF8IHvoZrjwF0EXwVYM+ch0tPT8/Of//y+++475phjCKPLli2bMWMGQoDa/fff/+ijj06dOhVpDMY7nnveOZd+77vlaqEdysBAFo5/ecVvc8Wi5PPVjTfSueyN1ThOLGhkZD2YZO0v+6wpoAowRXxXKORmbLqx+K4Enjhy7TXXN8abtVoDRwJ0MJs3cVHFTgjAfvgVvFQHELRADLnkkkuq1SqhDdC88Y1v/P3vf8902pkFJuABGVWsNzIy8trXvvaggw56+ctf/tBDD+G0QBhYgV7ykpe8973vZSQQYTCSWYWS+IXP23nnnRlJb4cuvvjiAw44YMcdd5wzZ86sWbMA0/nnnw/IUGDF8Nivf3fl6HgTnAwO1tDh0cce5/nJHphp05x8YD0ntqRhVnjMGCTd9/xz2xPUfZopHNIqrdSEihRGdCtN2dZNtt4Cn8R+jg6NLHn6KbrwTJSu6+IkcAZLly4lq8W64+NZMoQtlVJUIYZBH/vYx7bddltQAn/yySd///vfB1gErI7TIpeCoUovKDHG/PKXv7zhhhsuu+yyl770pcxiFQifxyonnnji4Ycfjj8Df8gHGWAOpIJgXBrDaEex00477Q1veMMT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"
             style="max-width:120px;margin-bottom:6px;border-radius:4px;">
    </div>""", unsafe_allow_html=True)
    st.markdown("<p style='color:#FFE0E0;font-size:0.75rem;text-align:center;margin-top:2px;'>Energy Intensity Benchmarking</p>", unsafe_allow_html=True)
    st.divider()
    uploaded = st.file_uploader("Upload SCADA data (CSV)", type=["csv"],
        help="Columns: Date, Station, Energy_kWh, Volume_m3")
    st.divider()
    st.markdown("<b style='color:#FFE0E0;font-size:0.82rem;'>Benchmark Thresholds (kWh/m³)</b>", unsafe_allow_html=True)
    eff_t   = st.number_input("Efficient below",   value=EFFICIENT_T,   step=0.1, format="%.1f")
    ineff_t = st.number_input("Inefficient above", value=INEFFICIENT_T, step=0.1, format="%.1f")
    tariff  = st.number_input("KPLC tariff (KShs/kWh)", value=KPLC_RATE, step=0.5, format="%.1f")
    st.divider()
    st.markdown("<b style='color:#FFE0E0;font-size:0.82rem;'>Navigation</b>", unsafe_allow_html=True)
    page = st.radio("Navigate", [
        "System Overview",
        "Pipeline Map",
        "Station Deep Dive",
        "Pump-Level Breakdown",
        "Anomaly Detection",
        "What-If Simulator",
        "Cost Analysis",
        "ML Model Performance",
        "5-Year Training Data",
    ], label_visibility="collapsed")
    st.divider()
    st.markdown("<p style='color:#FFE0E0;font-size:0.72rem;text-align:center;'>PS1 · PS3 · PS5 · PS7<br>Mombasa → Nairobi · ~500 km</p>", unsafe_allow_html=True)

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
    return {'Efficient':   'background-color:#064e3b;color:#10b981;font-weight:600',
            'Moderate':    'background-color:#451a03;color:#f59e0b;font-weight:600',
            'Inefficient': 'background-color:#450a0a;color:#ef4444;font-weight:600'}.get(val, '')


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
        (f"{df_case['Energy_Intensity_kWh_m3'].mean():.3f}", "Avg System EI (kWh/m³)",    "#CC0000"),
        (f"{df_case['Energy_kWh'].sum()/1e6:.1f}M",          "Total Energy (kWh)",         "#333333"),
        (f"{df_case['Volume_m3'].mean()/1e6:.2f}M",          "Avg Monthly Volume (m³)",    "#CC0000"),
        (f"KShs {df_case['Cost_KShs'].sum()/1e6:.1f}M",      "Total Electricity Cost",     "#333333"),
        (f"{df_case['Flow_Rate_m3hr'].mean():.0f}",           "Avg Flow Rate (m³/hr)",      "#CC0000"),
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
                      annotation_text=f'Efficient <={eff_t}', annotation_position='top left', annotation_font_color='#10b981')
        fig.add_hline(y=ineff_t, line_dash='dash', line_color='#CC0000',
                      annotation_text=f'Inefficient >{ineff_t}', annotation_position='top left', annotation_font_color='#ef4444')
        fig.add_hrect(y0=0,       y1=eff_t,   fillcolor='#10b981', opacity=0.05, line_width=0)
        fig.add_hrect(y0=eff_t,   y1=ineff_t, fillcolor='#f59e0b', opacity=0.05, line_width=0)
        fig.add_hrect(y0=ineff_t, y1=8,       fillcolor='#ef4444', opacity=0.05, line_width=0)
        fig.update_layout(title='Monthly EI Trend — All Stations',
            xaxis=dict(categoryorder='array', categoryarray=MONTHS),
            yaxis_title='kWh/m3', template='plotly_white', height=370,
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
        fig2.add_vline(x=ineff_t, line_dash='dash', line_color='#CC0000')
        fig2.update_layout(title='Station Ranking', template='plotly_white', height=200,
            xaxis_title='Avg EI (kWh/m3)', margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig2, use_container_width=True)

        heat = (df_case.pivot_table(index='Station', columns='Month',
                values='Energy_Intensity_kWh_m3', aggfunc='mean')
                .reindex(columns=MONTHS))
        fig3 = px.imshow(heat, color_continuous_scale='RdYlGn_r', template='plotly_white',
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
      <p>20-inch main pipeline &nbsp;|&nbsp; ~500 km &nbsp;|&nbsp; Elevation gain 5 m to 1,600 m &nbsp;|&nbsp; PS1 → PS3 → PS5 → PS7</p>
    </div>""", unsafe_allow_html=True)

    # Route badges
    st.markdown("""
    <div style="margin-bottom:12px;">
      <span class="route-badge">Mombasa Port (km 0)</span>
      <span style="color:#CC0000;font-weight:700;margin:0 4px;">→</span>
      <span class="route-badge">PS1 km 18</span>
      <span style="color:#CC0000;font-weight:700;margin:0 4px;">→</span>
      <span class="route-badge">PS3 km 135</span>
      <span style="color:#CC0000;font-weight:700;margin:0 4px;">→</span>
      <span class="route-badge">PS5 km 310</span>
      <span style="color:#CC0000;font-weight:700;margin:0 4px;">→</span>
      <span class="route-badge">PS7 km 455</span>
      <span style="color:#CC0000;font-weight:700;margin:0 4px;">→</span>
      <span class="route-badge">Nairobi Depot (km 495)</span>
    </div>
    """, unsafe_allow_html=True)

    col_img, col_info = st.columns([2, 1])
    with col_img:
        st.image("https://kpc.co.ke/wp-content/uploads/2023/10/pipeline.jpg",
                 caption="KPC 20-inch petroleum pipeline — Mombasa to Nairobi",
                 use_column_width=True)
    with col_info:
        st.markdown("""<div class="metric-card" style="margin-bottom:10px;">
          <div class="metric-value" style="font-size:1.2rem;color:#CC0000;">~500 km</div>
          <div class="metric-label">Total Pipeline Length</div>
        </div>
        <div class="metric-card" style="margin-bottom:10px;">
          <div class="metric-value" style="font-size:1.2rem;color:#CC0000;">1,595 m</div>
          <div class="metric-label">Total Elevation Gain</div>
        </div>
        <div class="metric-card" style="margin-bottom:10px;">
          <div class="metric-value" style="font-size:1.2rem;color:#CC0000;">20 inches</div>
          <div class="metric-label">Pipe Diameter</div>
        </div>
        <div class="metric-card">
          <div class="metric-value" style="font-size:1.2rem;color:#CC0000;">MSP · AGO · JETA-1</div>
          <div class="metric-label">Products Transported</div>
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
        x=pipeline_km, y=pipeline_elv, fill='tozeroy', fillcolor='rgba(200,200,200,0.35)',
        line=dict(color='#999999', width=1), name='Terrain', showlegend=False))
    fig_pipe.add_trace(go.Scatter(
        x=pipeline_km, y=pipeline_elv, mode='lines',
        line=dict(color='#CC0000', width=6), name='20" Pipeline', showlegend=True))

    for name, d in [("Mombasa Port", STATIONS["Mombasa Port"]),
                     ("Nairobi Depot", STATIONS["Nairobi Depot"])]:
        fig_pipe.add_trace(go.Scatter(
            x=[d['km']], y=[d['elev']], mode='markers+text',
            marker=dict(size=16, color='#333333', symbol='diamond', line=dict(width=2, color='white')),
            text=[name], textposition='top center', textfont=dict(size=10, color='#333333'),
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
        xaxis=dict(title='Distance from Mombasa (km)', showgrid=True, gridcolor='#e5e7eb', range=[-10,510]),
        yaxis=dict(title='Elevation (m above sea level)', showgrid=True, gridcolor='#e5e7eb'),
        template='plotly_white', height=420,
        legend=dict(orientation='h', y=-0.2, font=dict(size=10)),
        margin=dict(l=10, r=10, t=60, b=10),
        paper_bgcolor='#FFFFFF', plot_bgcolor='#F9FAFB')
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
        fig.add_hline(y=ineff_t, line_dash='dash', line_color='#CC0000')
        fig.update_layout(title=f'{stn} — Monthly EI', template='plotly_white', height=300,
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
        fig2.update_layout(title=f'{stn} — Energy vs Volume', template='plotly_white', height=300,
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
        fig3.update_layout(title=f'{stn} — Monthly Runtime', template='plotly_white', height=250,
            xaxis=dict(categoryorder='array', categoryarray=MONTHS),
            yaxis_title='Hours', margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig3, use_container_width=True)
    with col_sc:
        fig4 = go.Figure(go.Scatter(
            x=sd['Volume_m3']/1e3, y=sd['Energy_Intensity_kWh_m3'],
            mode='markers+text', text=sd['Month'], textposition='top center',
            marker=dict(size=12, color=STATION_COLORS[stn])))
        fig4.add_hline(y=eff_t,   line_dash='dash', line_color='#10b981')
        fig4.add_hline(y=ineff_t, line_dash='dash', line_color='#CC0000')
        fig4.update_layout(title=f'{stn} — Volume vs EI', template='plotly_white', height=250,
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
            text=[f"{v:.3f}" for v in pdata['Energy_Intensity_kWh_m3']], template='plotly_white')
        fig.add_hline(y=eff_t,   line_dash='dash', line_color='#10b981')
        fig.add_hline(y=ineff_t, line_dash='dash', line_color='#CC0000')
        fig.update_traces(textposition='outside')
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=50, b=10),
            showlegend=False, yaxis_title='kWh/m3')
        st.plotly_chart(fig, use_container_width=True)
    with col_pie:
        fig2 = px.pie(pdata, names='Pump', values='Energy_kWh',
            title=f'{stn} — Energy Share ({mo} 2026)', template='plotly_white', hole=0.45)
        fig2.update_layout(height=300, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    all_p = df_pump[df_pump['Station'] == stn]
    fig3  = px.line(all_p, x='Month', y='Energy_Intensity_kWh_m3', color='Pump', markers=True,
        title=f'{stn} — Monthly EI by Pump', template='plotly_white',
        category_orders={'Month': MONTHS})
    fig3.add_hline(y=eff_t,   line_dash='dash', line_color='#10b981')
    fig3.add_hline(y=ineff_t, line_dash='dash', line_color='#CC0000')
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

    st.markdown('<p class="section-header">5-Year Anomaly Map (Jul 2022 – Jun 2026)</p>', unsafe_allow_html=True)
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
    fig.add_hline(y=ineff_t, line_dash='dash', line_color='#CC0000', annotation_text='Inefficient')
    fig.update_layout(title=f'{stn2} — 5-Year EI with Anomaly Markers',
        template='plotly_white', height=380,
        legend=dict(orientation='h', y=-0.2), margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)


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
            template='plotly_white', height=320,
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
            template='plotly_white', height=300, xaxis_title='Cost (M KShs)',
            margin=dict(l=10,r=10,t=50,b=10))
        st.plotly_chart(fig, use_container_width=True)
    with col_pie:
        fig2 = px.pie(cost_by_stn, names='Station', values='Cost_KShs',
            color='Station', color_discrete_map=STATION_COLORS,
            title='Cost Share by Station', template='plotly_white', hole=0.45)
        fig2.update_layout(height=300, margin=dict(l=10,r=10,t=50,b=10))
        st.plotly_chart(fig2, use_container_width=True)

    # Monthly trend
    cost_monthly = (df_case.groupby(['Month','Station'])['Cost_KShs']
                    .sum().reset_index())
    fig3 = px.bar(cost_monthly, x='Month', y='Cost_KShs', color='Station',
        color_discrete_map=STATION_COLORS,
        title='Monthly Cost Breakdown by Station',
        template='plotly_white', barmode='stack',
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
elif page == "5-Year Training Data":
    st.markdown("""<div class="kpc-header">
      <h1>5-Year Training Dataset</h1>
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
    fig.add_hline(y=ineff_t, line_dash='dash', line_color='#CC0000')
    fig.update_layout(title='5-Year EI Trend with Anomaly Markers',
        template='plotly_white', height=360,
        legend=dict(orientation='h', y=-0.15),
        margin=dict(l=10,r=10,t=50,b=10))
    st.plotly_chart(fig, use_container_width=True)

    # Volume trend
    fig_v = px.line(show_df, x='Date', y='Volume_m3', color='Station',
        color_discrete_map=STATION_COLORS,
        title='Monthly ML5 Mainline Throughput Volume', template='plotly_white',
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
    f"KPC Energy Intensity Benchmarking Dashboard | EI = kWh / m³ | "
    f"Efficient < {eff_t} | Moderate {eff_t}–{ineff_t} | Inefficient > {ineff_t} kWh/m3 | "
    f"Tariff: KShs {tariff}/kWh | Energy: Actual KPLC Billing Jan–Jun 2026 | "
    f"Volume: Real ML5 Mainline Throughput | "
    "Data: Actual KPLC Billing (Jan–Jun 2026) + Real ML5 Mainline Throughput"
)
