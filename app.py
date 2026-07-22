"""
Kenya Pipeline Company — Energy Intensity Benchmarking Dashboard
Pumping Stations: PS1, PS3, PS5, PS7 | Jan–Jun 2026
Capstone Project | Dorothy Lizz Odoyo | MSc Sustainable Energy Transition | Strathmore University

Data: Energy consumption (kWh) from actual KPLC billing records (Jan–Jun 2026)
      Throughput volumes (m³) from sample/estimated operational data
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="KPC Energy Intensity Dashboard",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .kpc-header {
    background: linear-gradient(90deg, #0a2342, #1a4a7a);
    padding: 18px 24px; border-radius: 10px; margin-bottom: 18px;
    border-left: 5px solid #f5a623;
  }
  .kpc-header h1 { color: #ffffff; font-size: 1.5rem; margin: 0; }
  .kpc-header p  { color: #b8d4f0; font-size: 0.82rem; margin: 4px 0 0 0; }
  .metric-card {
    background: linear-gradient(135deg, #1e2130, #252a3a);
    border-radius: 10px; padding: 16px;
    border-left: 4px solid #4a9eff; margin-bottom: 8px;
  }
  .metric-value { font-size: 1.8rem; font-weight: 700; color: #ffffff; }
  .metric-label { font-size: 0.78rem; color: #9ca3af; margin-top: 3px; }
  .tl-green  { background: linear-gradient(135deg,#064e3b,#065f46); border-left:4px solid #10b981; border-radius:10px; padding:14px; }
  .tl-yellow { background: linear-gradient(135deg,#451a03,#78350f); border-left:4px solid #f59e0b; border-radius:10px; padding:14px; }
  .tl-red    { background: linear-gradient(135deg,#450a0a,#7f1d1d); border-left:4px solid #ef4444; border-radius:10px; padding:14px; }
  .tl-label  { font-weight:700; font-size:1.05rem; }
  .tl-sub    { font-size:0.75rem; color:#d1d5db; margin-top:2px; }
  .section-header {
    font-size:1rem; font-weight:600; color:#e2e8f0;
    margin:20px 0 8px; border-bottom:1px solid #374151; padding-bottom:5px;
  }
  .data-note {
    background:#1e2d45; border-left:3px solid #f5a623;
    padding:10px 14px; border-radius:6px; font-size:0.8rem; color:#b8d4f0;
  }
</style>
""", unsafe_allow_html=True)

# ── Thresholds ─────────────────────────────────────────────────────────────────
EFFICIENT_T  = 5.5    # kWh/m³ — Efficient (green)
INEFFICIENT_T = 7.5   # kWh/m³ — Inefficient (red)

COLOR_MAP = {"Efficient": "#10b981", "Moderate": "#f59e0b", "Inefficient": "#ef4444"}
STATION_COLORS = {"PS1": "#4a9eff", "PS3": "#f59e0b", "PS5": "#10b981", "PS7": "#c084fc"}

def classify(ei, eff=EFFICIENT_T, ineff=INEFFICIENT_T):
    if ei < eff:   return "Efficient"
    if ei <= ineff: return "Moderate"
    return "Inefficient"

# ── Embedded data (real kWh from KPLC bills + sample volumes) ─────────────────
@st.cache_data
def get_base_data():
    months      = ['Jan','Feb','Mar','Apr','May','Jun']
    month_dates = pd.to_datetime(['2026-01-01','2026-02-01','2026-03-01',
                                  '2026-04-01','2026-05-01','2026-06-01'])

    # REAL energy consumption (kWh) — auxiliary meter + main pump meter
    energy = {
        'PS1': [2317134, 2349447, 2716257, 2257791, 2169519, 2384220],
        'PS3': [1899924, 2225376, 1906080, 2118120, 1861224, 2040312],
        'PS5': [2193846, 2138910, 2502426, 2057286, 2029614, 2245356],
        'PS7': [2038182, 1977528, 2415570, 1949652, 1904724, 2136456],
    }
    # SAMPLE throughput volumes (m³) — to be replaced with SCADA data
    volumes = [395000, 350000, 430000, 360000, 400000, 375000]
    runtimes = {
        'PS1': [580, 520, 630, 545, 590, 560],
        'PS3': [560, 510, 610, 530, 575, 545],
        'PS5': [575, 515, 625, 535, 580, 548],
        'PS7': [548, 498, 605, 518, 568, 536],
    }

    rows = []
    for stn in ['PS1','PS3','PS5','PS7']:
        for i in range(6):
            kwh = energy[stn][i]
            vol = volumes[i]
            rt  = runtimes[stn][i]
            ei  = round(kwh / vol, 4)
            rows.append({
                'Date':    month_dates[i],
                'Month':   months[i],
                'Year':    2026,
                'Station': stn,
                'Energy_kWh':  kwh,
                'Volume_m3':   vol,
                'Runtime_hrs': rt,
                'Flow_Rate_m3hr':  round(vol / rt, 1),
                'Avg_Power_kW':    round(kwh / rt, 1),
                'Energy_Intensity_kWh_m3': ei,
                'Efficiency_Class': classify(ei),
            })
    return pd.DataFrame(rows)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛢️ KPC Dashboard")
    st.caption("Kenya Pipeline Company\nEnergy Intensity Benchmarking")
    st.divider()

    uploaded = st.file_uploader(
        "📂 Upload real SCADA/volume data (CSV)",
        type=["csv"],
        help="Must include: Date, Station, Energy_kWh, Volume_m3",
    )

    st.divider()
    st.markdown("**Benchmark Thresholds (kWh/m³)**")
    eff_t   = st.number_input("🟢 Efficient below", value=EFFICIENT_T,  step=0.5, format="%.1f")
    ineff_t = st.number_input("🔴 Inefficient above", value=INEFFICIENT_T, step=0.5, format="%.1f")

    st.divider()
    sel_stations = st.multiselect("Stations", ['PS1','PS3','PS5','PS7'],
                                  default=['PS1','PS3','PS5','PS7'])
    sel_months   = st.multiselect("Months", ['Jan','Feb','Mar','Apr','May','Jun'],
                                  default=['Jan','Feb','Mar','Apr','May','Jun'])
    st.divider()
    st.caption("MSc Sustainable Energy Transition\nStrathmore University · 2026")

# ── Load & filter ──────────────────────────────────────────────────────────────
df_base = get_base_data()

if uploaded:
    try:
        df_up = pd.read_csv(uploaded)
        df_up['Date'] = pd.to_datetime(df_up['Date'])
        if 'Energy_Intensity_kWh_m3' not in df_up.columns:
            df_up['Energy_Intensity_kWh_m3'] = df_up['Energy_kWh'] / df_up['Volume_m3']
        df_up['Efficiency_Class'] = df_up['Energy_Intensity_kWh_m3'].apply(
            lambda x: classify(x, eff_t, ineff_t))
        df_all = df_up
        using_upload = True
    except Exception as e:
        st.error(f"Upload error: {e}")
        df_all = df_base; using_upload = False
else:
    df_all = df_base; using_upload = False

# Re-classify with current threshold sliders
df_all['Efficiency_Class'] = df_all['Energy_Intensity_kWh_m3'].apply(
    lambda x: classify(x, eff_t, ineff_t))

df = df_all[
    df_all['Station'].isin(sel_stations) &
    df_all['Month'].isin(sel_months)
].copy()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="kpc-header">
  <h1>🛢️ Kenya Pipeline Company — Energy Intensity Benchmarking</h1>
  <p>Pumping Stations PS1 · PS3 · PS5 · PS7 &nbsp;|&nbsp; January – June 2026 &nbsp;|&nbsp;
     Energy data: Actual KPLC billing &nbsp;|&nbsp; Throughput: Sample data (replace with SCADA)</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📋 June 2026 Case Study (Actual Energy Data)", "📊 5-Year Training Dataset (Anomaly Explorer)"])

with tab1:

    st.markdown("""<div class="data-note">
    ⚡ <b>Energy consumption (kWh)</b> is sourced from actual KPLC electricity billing records (Jan–Jun 2026).
    &nbsp;|&nbsp; 📦 <b>Throughput volumes (m³)</b> are estimated sample data — replace with SCADA meter readings for precise EI values.
    &nbsp;|&nbsp; EI = kWh consumed ÷ m³ pumped
    </div>""", unsafe_allow_html=True)

    # ── Station Traffic Lights ──────────────────────────────────────────────────────
    st.markdown('<p class="section-header">Station Status — Average Energy Intensity (Jan–Jun 2026)</p>',
                unsafe_allow_html=True)

    cols = st.columns(4)
    for i, stn in enumerate(['PS1','PS3','PS5','PS7']):
        stn_df = df[df['Station'] == stn]
        if stn_df.empty:
            continue
        avg_ei = stn_df['Energy_Intensity_kWh_m3'].mean()
        total_kwh = stn_df['Energy_kWh'].sum()
        cls = classify(avg_ei, eff_t, ineff_t)
        css = "tl-green" if cls=="Efficient" else ("tl-yellow" if cls=="Moderate" else "tl-red")
        icon = "🟢" if cls=="Efficient" else ("🟡" if cls=="Moderate" else "🔴")
        with cols[i]:
            st.markdown(f"""<div class="{css}">
                <div class="tl-label" style="color:#fff">{icon} {stn}</div>
                <div style="font-size:1.6rem;font-weight:700;color:#fff;margin:6px 0">{avg_ei:.2f} kWh/m³</div>
                <div class="tl-sub">{cls.upper()} &nbsp;|&nbsp; {total_kwh/1e6:.2f}M kWh total</div>
            </div>""", unsafe_allow_html=True)

    # ── KPIs ───────────────────────────────────────────────────────────────────────
    st.markdown('<p class="section-header">System-Level KPIs (Filtered Selection)</p>',
                unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    kpi_data = [
        (f"{df['Energy_Intensity_kWh_m3'].mean():.2f}", "Avg Energy Intensity (kWh/m³)", "#4a9eff"),
        (f"{df['Energy_kWh'].sum()/1e6:.1f}M", "Total Energy Consumed (kWh)", "#f59e0b"),
        (f"{df['Volume_m3'].sum()/1e6:.2f}M", "Total Volume Pumped (m³) ★", "#10b981"),
        (f"{df['Avg_Power_kW'].mean()/1000:.2f}K", "Avg Demand (kW)", "#c084fc"),
        (f"{df['Flow_Rate_m3hr'].mean():.0f}", "Avg Flow Rate (m³/hr)", "#64748b"),
    ]
    for col, (val, lbl, color) in zip([c1,c2,c3,c4,c5], kpi_data):
        with col:
            st.markdown(f"""<div class="metric-card" style="border-left-color:{color}">
                <div class="metric-value">{val}</div>
                <div class="metric-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.caption("★ Volume figures are sample/estimated — replace with actual SCADA meter data")

    # ── Row 1: EI Trend + Monthly bar ──────────────────────────────────────────────
    st.markdown('<p class="section-header">Energy Intensity Trends</p>', unsafe_allow_html=True)
    col_trend, col_month = st.columns([3, 2])

    month_order = ['Jan','Feb','Mar','Apr','May','Jun']

    with col_trend:
        fig_trend = go.Figure()
        for stn in sel_stations:
            sd = df[df['Station']==stn].sort_values('Date')
            fig_trend.add_trace(go.Scatter(
                x=sd['Month'], y=sd['Energy_Intensity_kWh_m3'],
                name=stn, mode='lines+markers+text',
                text=[f"{v:.2f}" for v in sd['Energy_Intensity_kWh_m3']],
                textposition='top center', textfont=dict(size=9),
                marker=dict(size=8, color=STATION_COLORS.get(stn, '#888')),
                line=dict(width=2.5, color=STATION_COLORS.get(stn, '#888')),
            ))
        fig_trend.add_hline(y=eff_t, line_dash='dash', line_color='#10b981',
                            annotation_text=f'Efficient ≤{eff_t}', annotation_position='top left')
        fig_trend.add_hline(y=ineff_t, line_dash='dash', line_color='#ef4444',
                            annotation_text=f'Inefficient >{ineff_t}', annotation_position='top left')
        fig_trend.add_hrect(y0=0,       y1=eff_t,   fillcolor='#10b981', opacity=0.05, line_width=0)
        fig_trend.add_hrect(y0=eff_t,   y1=ineff_t, fillcolor='#f59e0b', opacity=0.05, line_width=0)
        fig_trend.add_hrect(y0=ineff_t, y1=15,      fillcolor='#ef4444', opacity=0.05, line_width=0)
        fig_trend.update_layout(
            title='Monthly Energy Intensity per Station (kWh/m³)',
            xaxis=dict(title='Month 2026', categoryorder='array', categoryarray=month_order),
            yaxis_title='Energy Intensity (kWh/m³)',
            template='plotly_dark', height=380,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=10,r=10,t=60,b=10),
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_month:
        month_avg = df.groupby('Month')['Energy_Intensity_kWh_m3'].mean().reindex(month_order).reset_index()
        month_avg.columns = ['Month','Avg_EI']
        month_avg['Color'] = month_avg['Avg_EI'].apply(
            lambda x: '#10b981' if x < eff_t else ('#ef4444' if x > ineff_t else '#f59e0b'))
        fig_bar = go.Figure(go.Bar(
            x=month_avg['Month'], y=month_avg['Avg_EI'],
            marker_color=month_avg['Color'],
            text=[f"{v:.2f}" for v in month_avg['Avg_EI']],
            textposition='outside',
        ))
        fig_bar.add_hline(y=eff_t, line_dash='dash', line_color='#10b981')
        fig_bar.add_hline(y=ineff_t, line_dash='dash', line_color='#ef4444')
        fig_bar.update_layout(
            title='Monthly Avg EI (All Stations)',
            xaxis=dict(categoryorder='array', categoryarray=month_order),
            yaxis_title='kWh/m³', template='plotly_dark', height=380,
            margin=dict(l=10,r=10,t=50,b=10),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Row 2: Energy consumption + Station comparison ─────────────────────────────
    st.markdown('<p class="section-header">Energy Consumption & Station Comparison</p>',
                unsafe_allow_html=True)
    col_kwh, col_box = st.columns(2)

    with col_kwh:
        fig_kwh = go.Figure()
        for stn in sel_stations:
            sd = df[df['Station']==stn].sort_values('Date')
            fig_kwh.add_trace(go.Bar(
                x=sd['Month'], y=sd['Energy_kWh']/1e6,
                name=stn, marker_color=STATION_COLORS.get(stn,'#888'),
            ))
        fig_kwh.update_layout(
            title='Monthly Energy Consumption by Station (Million kWh) — ACTUAL KPLC Data',
            barmode='group', template='plotly_dark', height=320,
            xaxis=dict(categoryorder='array', categoryarray=month_order),
            yaxis_title='Energy (M kWh)',
            margin=dict(l=10,r=10,t=50,b=10),
            legend=dict(orientation='h', y=1.02),
        )
        st.plotly_chart(fig_kwh, use_container_width=True)

    with col_box:
        fig_box = px.box(df, x='Station', y='Energy_Intensity_kWh_m3',
                         color='Station', color_discrete_map=STATION_COLORS,
                         title='EI Distribution by Station',
                         points='all', hover_data=['Month','Energy_kWh'],
                         template='plotly_dark')
        fig_box.add_hline(y=eff_t,   line_dash='dash', line_color='#10b981',
                          annotation_text='Efficient', annotation_position='top right')
        fig_box.add_hline(y=ineff_t, line_dash='dash', line_color='#ef4444',
                          annotation_text='Inefficient', annotation_position='top right')
        fig_box.update_layout(height=320, margin=dict(l=10,r=10,t=50,b=10),
                              showlegend=False, yaxis_title='kWh/m³', xaxis_title='')
        st.plotly_chart(fig_box, use_container_width=True)

    # ── Row 3: Ranked bar + Power demand ──────────────────────────────────────────
    st.markdown('<p class="section-header">Station Rankings & Power Demand</p>',
                unsafe_allow_html=True)
    col_rank, col_power = st.columns(2)

    with col_rank:
        station_avg = df.groupby('Station').agg(
            Avg_EI=('Energy_Intensity_kWh_m3','mean'),
            Total_kWh=('Energy_kWh','sum'),
            Avg_kWh=('Energy_kWh','mean'),
        ).reset_index().sort_values('Avg_EI')
        station_avg['Color'] = station_avg['Avg_EI'].apply(
            lambda x: '#10b981' if x < eff_t else ('#ef4444' if x > ineff_t else '#f59e0b'))

        fig_rank = go.Figure(go.Bar(
            y=station_avg['Station'], x=station_avg['Avg_EI'],
            orientation='h',
            marker_color=station_avg['Color'],
            text=[f"{v:.2f} kWh/m³" for v in station_avg['Avg_EI']],
            textposition='outside',
        ))
        fig_rank.add_vline(x=eff_t,   line_dash='dash', line_color='#10b981')
        fig_rank.add_vline(x=ineff_t, line_dash='dash', line_color='#ef4444')
        fig_rank.update_layout(
            title='Station Ranking — Avg Energy Intensity (lower = better)',
            template='plotly_dark', height=300,
            xaxis_title='Avg EI (kWh/m³)',
            margin=dict(l=10,r=10,t=50,b=10),
        )
        st.plotly_chart(fig_rank, use_container_width=True)

    with col_power:
        fig_power = go.Figure()
        for stn in sel_stations:
            sd = df[df['Station']==stn].sort_values('Date')
            fig_power.add_trace(go.Scatter(
                x=sd['Month'], y=sd['Avg_Power_kW'],
                name=stn, mode='lines+markers',
                marker=dict(size=7, color=STATION_COLORS.get(stn,'#888')),
                line=dict(width=2, color=STATION_COLORS.get(stn,'#888')),
            ))
        fig_power.update_layout(
            title='Average Power Demand per Station (kW)',
            xaxis=dict(categoryorder='array', categoryarray=month_order),
            yaxis_title='Avg Power (kW)', template='plotly_dark', height=300,
            legend=dict(orientation='h', y=1.02),
            margin=dict(l=10,r=10,t=50,b=10),
        )
        st.plotly_chart(fig_power, use_container_width=True)

    # ── Row 4: Heat map + Efficiency classification count ─────────────────────────
    st.markdown('<p class="section-header">Heatmap & Classification</p>', unsafe_allow_html=True)
    col_heat, col_class = st.columns([3, 2])

    with col_heat:
        heat = df.pivot_table(index='Station', columns='Month',
                              values='Energy_Intensity_kWh_m3', aggfunc='mean')
        heat = heat.reindex(columns=month_order)
        fig_heat = px.imshow(heat, color_continuous_scale='RdYlGn_r',
                             title='Energy Intensity Heatmap — Station × Month (kWh/m³)',
                             labels=dict(color='kWh/m³'), template='plotly_dark', aspect='auto',
                             text_auto='.2f')
        fig_heat.update_layout(height=280, margin=dict(l=10,r=10,t=50,b=10))
        fig_heat.update_coloraxes(colorbar_title='kWh/m³')
        st.plotly_chart(fig_heat, use_container_width=True)

    with col_class:
        cls_counts = df.groupby(['Station','Efficiency_Class']).size().reset_index(name='Count')
        fig_cls = px.bar(cls_counts, x='Station', y='Count', color='Efficiency_Class',
                         color_discrete_map=COLOR_MAP, barmode='stack',
                         title='Classification Count per Station',
                         template='plotly_dark')
        fig_cls.update_layout(height=280, margin=dict(l=10,r=10,t=50,b=10),
                              legend_title='', xaxis_title='', yaxis_title='Months')
        st.plotly_chart(fig_cls, use_container_width=True)

    # ── Row 5: Potential savings insight ──────────────────────────────────────────
    st.markdown('<p class="section-header">Benchmark Gap & Potential Savings</p>',
                unsafe_allow_html=True)

    best_ei = df.groupby('Station')['Energy_Intensity_kWh_m3'].min()
    avg_ei_stn = df.groupby('Station')['Energy_Intensity_kWh_m3'].mean()
    avg_vol = df.groupby('Station')['Volume_m3'].mean()
    gap_df = pd.DataFrame({
        'Station': best_ei.index,
        'Best_EI_kWh_m3': best_ei.values,
        'Avg_EI_kWh_m3': avg_ei_stn.values,
        'Avg_Volume_m3': avg_vol.values,
    }).reset_index(drop=True)
    gap_df['EI_Gap'] = gap_df['Avg_EI_kWh_m3'] - gap_df['Best_EI_kWh_m3']
    gap_df['Potential_Saving_kWh_per_month'] = gap_df['EI_Gap'] * gap_df['Avg_Volume_m3']
    gap_df['Potential_Saving_MkWh'] = (gap_df['Potential_Saving_kWh_per_month'] / 1e6).round(3)

    col_gap, col_insight = st.columns([2, 1])

    with col_gap:
        fig_gap = go.Figure()
        fig_gap.add_trace(go.Bar(name='Current Avg EI', x=gap_df['Station'],
                                  y=gap_df['Avg_EI_kWh_m3'], marker_color='#f59e0b'))
        fig_gap.add_trace(go.Bar(name='Best Observed EI', x=gap_df['Station'],
                                  y=gap_df['Best_EI_kWh_m3'], marker_color='#10b981'))
        fig_gap.update_layout(
            title='Current vs Best-Observed Energy Intensity per Station',
            barmode='group', template='plotly_dark', height=300,
            yaxis_title='kWh/m³', margin=dict(l=10,r=10,t=50,b=10),
            legend=dict(orientation='h', y=1.02),
        )
        st.plotly_chart(fig_gap, use_container_width=True)

    with col_insight:
        st.markdown("**If each station consistently achieved its own best-observed EI:**")
        total_saving = gap_df['Potential_Saving_kWh_per_month'].sum()
        for _, row in gap_df.iterrows():
            st.metric(
                label=row['Station'],
                value=f"{row['Potential_Saving_MkWh']:.3f}M kWh/mo",
                delta=f"Gap: {row['EI_Gap']:.2f} kWh/m³",
                delta_color="inverse",
            )
        st.info(f"💡 Combined potential saving: **{total_saving/1e6:.2f}M kWh/month** "
                f"across all 4 stations — based on sample volumes")

    # ── Data table ─────────────────────────────────────────────────────────────────
    st.markdown('<p class="section-header">Detailed Data Table</p>', unsafe_allow_html=True)

    show_cols = [c for c in ['Date','Month','Station','Energy_kWh','Volume_m3',
        'Runtime_hrs','Flow_Rate_m3hr','Avg_Power_kW',
        'Energy_Intensity_kWh_m3','Efficiency_Class'] if c in df.columns]

    disp = df[show_cols].copy()
    disp['Date'] = disp['Date'].dt.strftime('%Y-%m')
    disp = disp.sort_values(['Station','Date'])

    def color_class(val):
        return {'Efficient':'background-color:#064e3b;color:#10b981',
                'Moderate':'background-color:#451a03;color:#f59e0b',
                'Inefficient':'background-color:#450a0a;color:#ef4444'}.get(val,'')

    st.dataframe(
        disp.style.applymap(color_class, subset=['Efficiency_Class'])
                  .format({'Energy_kWh':'{:,.0f}','Volume_m3':'{:,.0f}',
                           'Flow_Rate_m3hr':'{:.1f}','Avg_Power_kW':'{:,.0f}',
                           'Energy_Intensity_kWh_m3':'{:.4f}'}),
        use_container_width=True, height=320,
    )

    # ── Export ─────────────────────────────────────────────────────────────────────
    st.markdown('<p class="section-header">Export</p>', unsafe_allow_html=True)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    st.download_button("⬇️ Download Filtered Data (CSV)", buf.getvalue(),
                       "kpc_ei_filtered.csv", "text/csv")

    st.divider()
    st.caption(
        "Kenya Pipeline Company · Energy Intensity = kWh ÷ m³ · "
        f"Benchmarks: Efficient < {eff_t} | Moderate {eff_t}–{ineff_t} | Inefficient > {ineff_t} kWh/m³ · "
        "Energy data: Actual KPLC billing Jan–Jun 2026 · Volume: Sample data · "
        "Capstone Project | Dorothy Lizz Odoyo | MSc Sustainable Energy Transition | Strathmore University 2026"
    )




# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — 5-YEAR TRAINING DATASET WITH ANOMALY EXPLORER
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""<div class="kpc-header">
      <h1>📊 5-Year Training Dataset — Anomaly Explorer (2020–2024)</h1>
      <p>Synthetic dataset calibrated to KPC operating profile · 240 monthly records ·
         5 anomaly types injected & labelled for ML training</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="data-note">
    🔬 This dataset uses <b>sample energy & volume data</b> calibrated to KPC's billing profile.
    &nbsp;20 labelled anomalies across 4 stations &amp; 5 anomaly types are embedded for supervised ML training.
    &nbsp;The anomaly labels (<code>Is_Anomaly</code>, <code>Anomaly_Type</code>) are the training targets.
    </div>""", unsafe_allow_html=True)

    # Load training data
    @st.cache_data
    def get_training_data():
        try:
            df_t = pd.read_csv('/sessions/dazzling-tender-pasteur/mnt/outputs/kpc_5yr_training_data.csv')
        except:
            df_t = build_training_data()
        df_t['Date'] = pd.to_datetime(df_t['Date'])
        return df_t

    def build_training_data():
        stations = ['PS1', 'PS3', 'PS5', 'PS7']
        dates    = pd.date_range('2020-01-01', '2024-12-01', freq='MS')
        base_ei  = {'PS1': 5.90, 'PS3': 5.00, 'PS5': 5.60, 'PS7': 5.30}
        base_vol = 375_000
        anomaly_schedule = {
            ('PS1',2020,9):'Maintenance_Period',('PS1',2021,3):'Equipment_Degradation',
            ('PS1',2022,7):'Off_BEP_Operation',('PS1',2023,11):'Power_Quality_Issue',
            ('PS1',2024,5):'Pump_Failure_Indicator',
            ('PS3',2020,6):'Off_BEP_Operation',('PS3',2021,10):'Maintenance_Period',
            ('PS3',2022,4):'Equipment_Degradation',('PS3',2023,8):'Power_Quality_Issue',
            ('PS3',2024,2):'Pump_Failure_Indicator',
            ('PS5',2020,11):'Equipment_Degradation',('PS5',2021,5):'Power_Quality_Issue',
            ('PS5',2022,9):'Maintenance_Period',('PS5',2023,3):'Off_BEP_Operation',
            ('PS5',2024,8):'Pump_Failure_Indicator',
            ('PS7',2020,4):'Pump_Failure_Indicator',('PS7',2021,8):'Equipment_Degradation',
            ('PS7',2022,1):'Power_Quality_Issue',('PS7',2023,6):'Off_BEP_Operation',
            ('PS7',2024,10):'Maintenance_Period',
        }
        effects = {
            'Equipment_Degradation': dict(ei=1.28,vol=0.97,rt=1.05,pf=-0.02),
            'Off_BEP_Operation':     dict(ei=1.22,vol=0.88,rt=1.12,pf=-0.03),
            'Maintenance_Period':    dict(ei=0.95,vol=0.55,rt=0.50,pf=0.00),
            'Power_Quality_Issue':   dict(ei=1.18,vol=1.00,rt=1.00,pf=-0.08),
            'Pump_Failure_Indicator':dict(ei=1.45,vol=0.70,rt=1.30,pf=-0.05),
            None:                    dict(ei=1.00,vol=1.00,rt=1.00,pf=0.00),
        }
        np.random.seed(42)
        rows = []
        for stn in stations:
            b_ei = base_ei[stn]
            rt_base = {'PS1':575,'PS3':555,'PS5':570,'PS7':548}[stn]
            for dt in dates:
                yr,mo = dt.year, dt.month
                i = (yr-2020)*12+(mo-1)
                degrad = 1 + 0.04*(i/len(dates))
                season = 1 + 0.12*np.sin((mo-3)*np.pi/6)
                at = anomaly_schedule.get((stn,yr,mo), None)
                e  = effects[at]
                vol = max(base_vol*season*e['vol']+np.random.normal(0,8000),80000)
                rt  = np.clip(rt_base*season*e['rt']*degrad**0.3+np.random.normal(0,15),200,720)
                ei  = max(b_ei*degrad*e['ei']+np.random.normal(0,0.12),3.5)
                pf  = np.clip(0.955+e['pf']+np.random.normal(0,0.015),0.70,1.0)
                cls = 'Efficient' if ei<5.5 else ('Moderate' if ei<7.5 else 'Inefficient')
                rows.append({'Date':dt,'Year':yr,'Month':mo,'Month_Name':dt.strftime('%b'),
                    'Quarter':f"Q{(mo-1)//3+1}",'Station':stn,
                    'Energy_kWh':round(ei*vol),'Volume_m3':round(vol),
                    'Runtime_hrs':round(rt,1),'Flow_Rate_m3hr':round(vol/rt,1),
                    'Avg_Power_kW':round(ei*vol/rt,1),'Power_Factor':round(pf,4),
                    'Energy_Intensity_kWh_m3':round(ei,4),'Efficiency_Class':cls,
                    'Is_Anomaly':int(at is not None),
                    'Anomaly_Type':at if at else 'Normal','Anomaly_Notes':''})
        return pd.DataFrame(rows)

    dft = get_training_data()

    # Sidebar filters for tab2
    t2_stations = st.multiselect("Stations (Training)", ['PS1','PS3','PS5','PS7'],
                                  default=['PS1','PS3','PS5','PS7'], key='t2_stn')
    t2_years    = st.multiselect("Years", [2020,2021,2022,2023,2024],
                                  default=[2020,2021,2022,2023,2024], key='t2_yr')
    dft_f = dft[dft['Station'].isin(t2_stations) & dft['Year'].isin(t2_years)].copy()

    # Training dataset KPIs
    st.markdown('<p class="section-header">Dataset Overview</p>', unsafe_allow_html=True)
    k1,k2,k3,k4,k5 = st.columns(5)
    kpis_t = [
        (len(dft_f), "Total Records", "#4a9eff"),
        (dft_f['Is_Anomaly'].sum(), "Labelled Anomalies", "#ef4444"),
        (f"{dft_f['Energy_Intensity_kWh_m3'].mean():.2f}", "Avg EI (kWh/m³)", "#f59e0b"),
        (f"{dft_f['Energy_kWh'].sum()/1e9:.2f}B", "Total Energy (kWh)", "#10b981"),
        (len(dft_f['Anomaly_Type'].unique())-1, "Anomaly Types", "#c084fc"),
    ]
    for col,(val,lbl,color) in zip([k1,k2,k3,k4,k5],kpis_t):
        with col:
            st.markdown(f"""<div class="metric-card" style="border-left-color:{color}">
                <div class="metric-value">{val}</div>
                <div class="metric-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    # EI Trend with anomaly markers
    st.markdown('<p class="section-header">Energy Intensity Trend — Anomalies Highlighted</p>',
                unsafe_allow_html=True)

    ANOMALY_COLORS = {
        'Equipment_Degradation':  '#f97316',
        'Off_BEP_Operation':      '#a855f7',
        'Maintenance_Period':     '#06b6d4',
        'Power_Quality_Issue':    '#ef4444',
        'Pump_Failure_Indicator': '#fbbf24',
        'Normal':                 '#6b7280',
    }

    sel_stn_t2 = st.selectbox("Select station for trend detail", t2_stations, key='t2_detail')
    sd = dft_f[dft_f['Station']==sel_stn_t2].sort_values('Date')

    fig_t2 = go.Figure()
    # Normal points
    norm = sd[sd['Is_Anomaly']==0]
    fig_t2.add_trace(go.Scatter(x=norm['Date'], y=norm['Energy_Intensity_kWh_m3'],
        mode='lines+markers', name='Normal', marker=dict(size=6,color='#4a9eff'),
        line=dict(color='#4a9eff',width=2)))

    # Anomaly points by type
    for atype, acolor in ANOMALY_COLORS.items():
        if atype == 'Normal': continue
        anom = sd[sd['Anomaly_Type']==atype]
        if not anom.empty:
            fig_t2.add_trace(go.Scatter(
                x=anom['Date'], y=anom['Energy_Intensity_kWh_m3'],
                mode='markers', name=atype.replace('_',' '),
                marker=dict(size=14, symbol='star', color=acolor,
                            line=dict(width=1,color='white')),
                hovertemplate=f"<b>{atype}</b><br>%{{x|%b %Y}}<br>EI: %{{y:.3f}} kWh/m³<extra></extra>",
            ))

    fig_t2.add_hline(y=5.5, line_dash='dash', line_color='#10b981',
                     annotation_text='Efficient ≤5.5')
    fig_t2.add_hline(y=7.5, line_dash='dash', line_color='#ef4444',
                     annotation_text='Inefficient >7.5')
    fig_t2.update_layout(
        title=f'{sel_stn_t2} — Monthly EI Trend 2020–2024 (★ = injected anomaly)',
        template='plotly_dark', height=400,
        xaxis_title='Date', yaxis_title='Energy Intensity (kWh/m³)',
        margin=dict(l=10,r=10,t=60,b=10),
        legend=dict(orientation='h', y=-0.2),
    )
    st.plotly_chart(fig_t2, use_container_width=True)

    # Anomaly type distribution + all-stations overview
    st.markdown('<p class="section-header">Anomaly Distribution & Multi-Station Overview</p>',
                unsafe_allow_html=True)
    col_adist, col_multi = st.columns(2)

    with col_adist:
        anom_counts = dft_f[dft_f['Is_Anomaly']==1].groupby('Anomaly_Type').agg(
            Count=('Is_Anomaly','sum'),
            Avg_EI=('Energy_Intensity_kWh_m3','mean'),
        ).reset_index()
        fig_adist = px.bar(anom_counts, x='Anomaly_Type', y='Avg_EI',
                           color='Anomaly_Type',
                           color_discrete_map={k:v for k,v in ANOMALY_COLORS.items()},
                           title='Avg EI by Anomaly Type (vs Normal baseline)',
                           text=[f"{v:.2f}" for v in anom_counts['Avg_EI']],
                           template='plotly_dark')
        normal_avg = dft_f[dft_f['Is_Anomaly']==0]['Energy_Intensity_kWh_m3'].mean()
        fig_adist.add_hline(y=normal_avg, line_dash='dot', line_color='#4a9eff',
                            annotation_text=f'Normal avg: {normal_avg:.2f}')
        fig_adist.update_layout(height=350, margin=dict(l=10,r=10,t=50,b=10),
                                showlegend=False, xaxis_title='', yaxis_title='Avg EI (kWh/m³)',
                                xaxis_tickangle=-20)
        fig_adist.update_traces(textposition='outside')
        st.plotly_chart(fig_adist, use_container_width=True)

    with col_multi:
        fig_multi = go.Figure()
        for stn in t2_stations:
            sd2 = dft_f[dft_f['Station']==stn].sort_values('Date')
            fig_multi.add_trace(go.Scatter(
                x=sd2['Date'], y=sd2['Energy_Intensity_kWh_m3'],
                name=stn, mode='lines', opacity=0.8,
                line=dict(color=STATION_COLORS.get(stn,'#888'), width=1.5),
            ))
            # Mark anomalies
            anoms2 = sd2[sd2['Is_Anomaly']==1]
            fig_multi.add_trace(go.Scatter(
                x=anoms2['Date'], y=anoms2['Energy_Intensity_kWh_m3'],
                name=f'{stn} anomaly', mode='markers', showlegend=False,
                marker=dict(size=10, symbol='x', color=STATION_COLORS.get(stn,'#888'),
                            line=dict(width=2)),
            ))
        fig_multi.add_hline(y=7.5, line_dash='dash', line_color='#ef4444')
        fig_multi.update_layout(title='All Stations — EI Trend with Anomaly Markers (✕)',
                                template='plotly_dark', height=350,
                                margin=dict(l=10,r=10,t=50,b=10),
                                legend=dict(orientation='h', y=-0.2))
        st.plotly_chart(fig_multi, use_container_width=True)

    # Feature correlation for ML
    st.markdown('<p class="section-header">Feature Distributions — Normal vs Anomaly</p>',
                unsafe_allow_html=True)

    feature = st.selectbox("Compare feature", [
        'Energy_Intensity_kWh_m3','Energy_kWh','Volume_m3',
        'Runtime_hrs','Flow_Rate_m3hr','Avg_Power_kW','Power_Factor'
    ], key='feat_sel')

    fig_viol = px.violin(dft_f, x='Anomaly_Type', y=feature,
                         color='Anomaly_Type',
                         color_discrete_map=ANOMALY_COLORS,
                         box=True, points='all',
                         title=f'{feature} Distribution by Category',
                         template='plotly_dark')
    fig_viol.update_layout(height=380, margin=dict(l=10,r=10,t=50,b=10),
                           showlegend=False, xaxis_title='', xaxis_tickangle=-15)
    st.plotly_chart(fig_viol, use_container_width=True)

    # Annual EI heatmap
    heat_t = dft_f.pivot_table(index='Station', columns='Year',
                                values='Energy_Intensity_kWh_m3', aggfunc='mean')
    fig_ht = px.imshow(heat_t, color_continuous_scale='RdYlGn_r',
                       title='Annual Avg EI Heatmap (kWh/m³) — degradation visible left→right',
                       labels=dict(color='kWh/m³'), template='plotly_dark',
                       aspect='auto', text_auto='.2f')
    fig_ht.update_layout(height=250, margin=dict(l=10,r=10,t=50,b=10))
    st.plotly_chart(fig_ht, use_container_width=True)

    # Training data table
    st.markdown('<p class="section-header">Training Data Table</p>', unsafe_allow_html=True)
    tcols = ['Date','Station','Year','Month_Name','Energy_kWh','Volume_m3',
             'Runtime_hrs','Power_Factor','Energy_Intensity_kWh_m3',
             'Efficiency_Class','Is_Anomaly','Anomaly_Type']
    tdisp = dft_f[[c for c in tcols if c in dft_f.columns]].copy()
    tdisp['Date'] = tdisp['Date'].dt.strftime('%Y-%m')
    tdisp = tdisp.sort_values(['Station','Date'])

    def color_anomaly(val):
        if val == 1: return 'background-color:#450a0a;color:#ef4444;font-weight:700'
        return ''
    def color_atype(val):
        colors = {
            'Equipment_Degradation':'color:#f97316',
            'Off_BEP_Operation':'color:#a855f7',
            'Maintenance_Period':'color:#06b6d4',
            'Power_Quality_Issue':'color:#ef4444',
            'Pump_Failure_Indicator':'color:#fbbf24',
        }
        return colors.get(val,'')

    st.dataframe(
        tdisp.style
             .applymap(color_anomaly, subset=['Is_Anomaly'])
             .applymap(color_atype, subset=['Anomaly_Type'])
             .format({'Energy_kWh':'{:,.0f}','Volume_m3':'{:,.0f}',
                      'Energy_Intensity_kWh_m3':'{:.4f}','Power_Factor':'{:.3f}'}),
        use_container_width=True, height=350,
    )

    # Download
    tbuf = io.StringIO()
    dft_f.to_csv(tbuf, index=False)
    st.download_button("⬇️ Download Training Dataset (CSV)", tbuf.getvalue(),
                       "kpc_5yr_training_data.csv", "text/csv")

    st.divider()
    st.caption(
        "5-year synthetic dataset calibrated to KPC operating profile · "
        "Anomaly types: Equipment Degradation, Off-BEP Operation, Maintenance Period, "
        "Power Quality Issue, Pump Failure Indicator · "
        "Capstone Project | Dorothy Lizz Odoyo | MSc Sustainable Energy Transition | Strathmore University 2026"
    )
