import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import altair as alt
from datetime import datetime, timedelta

# ==========================================
# 1. CSS & CONFIG (DOVE THEME)
# ==========================================
st.set_page_config(layout="wide", page_title="Dove Control Tower")

st.markdown("""
<style>
    /* SIDEBAR COLOR */
    [data-testid="stSidebar"] {background-color: #0F4C81;}
    [data-testid="stSidebar"] * {color: white !important;}

    /* MENU TABS STYLE */
    .stRadio > div {gap: 8px;}
    .stRadio label {
        background-color: rgba(255,255,255,0.1);
        color: white !important;
        padding: 10px; border-radius: 5px; border: 1px solid rgba(255,255,255,0.2);
    }
    .stRadio label[data-checked="true"] {
        background-color: #C9A446 !important;
        color: #0F4C81 !important;
        font-weight: bold; border-color: #C9A446;
    }
    
    /* BLUE BOX HIGHLIGHT */
    .metric-box {
        border: 2px solid #0F4C81;
        background-color: white;
        padding: 15px; border-radius: 10px; text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .metric-label {font-size: 14px; color: #555;}
    .metric-value {font-size: 24px; font-weight: bold; color: #0F4C81;}
    
    /* STANDARD CARD */
    div[data-testid="stMetric"] {
        background-color: white; border: 1px solid #eee;
        padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    [data-testid="stMetricValue"] {font-size: 26px; color: #0F4C81;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA LOADING & GEOJSON MANUAL
# ==========================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data_supply_chain.csv")
        df['Departure'] = pd.to_datetime(df['Departure'])
        df['Arrival'] = pd.to_datetime(df['Arrival'])
        return df
    except: return None

@st.cache_data
def get_local_geojson():
    # Peta Provinsi Jawa & Sumatera (Hardcoded biar stabil tanpa internet)
    return {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "properties": {"Propinsi": "DKI Jakarta"}, "geometry": {"type": "Polygon", "coordinates": [[[106.68, -6.1], [106.97, -6.1], [106.97, -6.36], [106.68, -6.36], [106.68, -6.1]]]}},
            {"type": "Feature", "properties": {"Propinsi": "Jawa Barat"}, "geometry": {"type": "Polygon", "coordinates": [[[106.3, -5.9], [108.8, -5.9], [108.8, -7.8], [106.3, -7.8], [106.3, -5.9]]]}},
            {"type": "Feature", "properties": {"Propinsi": "Jawa Tengah"}, "geometry": {"type": "Polygon", "coordinates": [[[108.8, -6.4], [111.6, -6.4], [111.6, -8.2], [108.8, -8.2], [108.8, -6.4]]]}},
            {"type": "Feature", "properties": {"Propinsi": "Jawa Timur"}, "geometry": {"type": "Polygon", "coordinates": [[[111.6, -6.6], [114.6, -6.6], [114.6, -8.8], [111.6, -8.8], [111.6, -6.6]]]}},
            {"type": "Feature", "properties": {"Propinsi": "Banten"}, "geometry": {"type": "Polygon", "coordinates": [[[105.1, -5.8], [106.3, -5.8], [106.3, -7.0], [105.1, -7.0], [105.1, -5.8]]]}},
            {"type": "Feature", "properties": {"Propinsi": "Sumatera Utara"}, "geometry": {"type": "Polygon", "coordinates": [[[97.5, 4.2], [100.5, 4.2], [100.5, 1.0], [97.5, 1.0], [97.5, 4.2]]]}}
        ]
    }

df_master = load_data()
geojson_indo = get_local_geojson()

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
if df_master is None:
    st.error("🚨 Data tidak ditemukan! Jalankan 'python create_data.py' dulu.")
    st.stop()

st.sidebar.title("🕊️ Dove Tower")
menu = st.sidebar.radio("Menu", ["Inbound Logistics", "Last Mile Delivery", "Inventory Health", "AI Forecasting"], label_visibility="collapsed")

st.sidebar.divider()
day_slider = st.sidebar.slider("Timeline 2024", 1, 365, 45)
curr_time = datetime(2024, 1, 1) + timedelta(days=day_slider)
curr_time = curr_time.replace(hour=14, minute=0) # Set jam 2 siang biar ramai
st.sidebar.write(f"📅 **{curr_time.strftime('%d %B %Y')}**")

def get_live_data(df, time):
    return df[(df['Departure'] <= time) & (df['Arrival'] >= time)].copy()

df_live = get_live_data(df_master, curr_time)

# ==========================================
# TAB 1: INBOUND (IMPORT)
# ==========================================
if menu == "Inbound Logistics":
    st.title("🚢 Inbound Logistics (Global → Hub)")
    
    df_in = df_live[df_live['Category']=='Inbound']
    
    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Active Vessels", len(df_in), "+2")
    c2.metric("Pending Clearance", "5 Cont.", "Avg Wait: 2 Days")
    c3.metric("Volume In-Transit", f"{df_in['Qty'].sum():,} L", "Raw Material")

    # Map
    layers = [
        pdk.Layer("LineLayer", data=df_in, get_source_position="[Start_Lon, Start_Lat]", get_target_position="[End_Lon, End_Lat]", get_width=2, get_color=[200, 200, 200]),
        pdk.Layer("ScatterplotLayer", data=df_in, get_position="[Start_Lon + (End_Lon-Start_Lon)*0.5, Start_Lat + (End_Lat-Start_Lat)*0.5]", get_radius=60000, get_color=[201, 164, 70], pickable=True)
    ]
    st.pydeck_chart(pdk.Deck(map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json", initial_view_state=pdk.ViewState(latitude=5, longitude=115, zoom=2.5), layers=layers, tooltip={"html": "<b>{ID}</b><br/>{Item}"}))
    
    # Table
    st.subheader("📋 Inbound Tracking")
    if not df_in.empty:
        disp = df_in[['ID', 'Item', 'Origin', 'Qty', 'Arrival']].copy()
        disp['ETA'] = disp['Arrival'].dt.strftime('%d-%b %H:%M')
        st.dataframe(disp, use_container_width=True)

# ==========================================
# TAB 2: LAST MILE (RETAIL)
# ==========================================
elif menu == "Last Mile Delivery":
    st.title("🚚 Last Mile Tracking (Jabodetabek)")
    
    df_ret = df_live[df_live['Category']=='Last Mile']
    
    m1, m2 = st.columns(2)
    m1.metric("Active Fleet", len(df_ret), "Unit Jalan")
    m2.metric("On-Time Performance", "97.2%", "Target 95%")
    
    # Peta Real-time
    live_pos = []
    for _, row in df_ret.iterrows():
        tot = (row['Arrival'] - row['Departure']).total_seconds()
        elap = (curr_time - row['Departure']).total_seconds()
        prog = elap / tot if tot > 0 else 0
        clat = row['Start_Lat'] + (row['End_Lat'] - row['Start_Lat']) * prog
        clon = row['Start_Lon'] + (row['End_Lon'] - row['Start_Lon']) * prog
        live_pos.append({'Lat': clat, 'Lon': clon, 'Item': row['Item'], 'Dest': row['Destination'], 'ID': row['ID']})
        
    df_pos = pd.DataFrame(live_pos)
    
    layers = [
        pdk.Layer("ScatterplotLayer", data=df_pos, get_position='[Lon, Lat]', get_color=[0, 75, 147], get_radius=1200, pickable=True)
    ]
    
    st.pydeck_chart(pdk.Deck(
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        initial_view_state=pdk.ViewState(latitude=-6.25, longitude=106.85, zoom=9.5),
        layers=layers,
        tooltip={"html": "<b>{ID}</b><br/>To: {Dest}"}
    ))
    
    # Table
    st.subheader("📦 Delivery List")
    if not df_ret.empty:
        track_df = df_ret[['ID', 'Item', 'Destination', 'Status_Detail', 'Arrival']].copy()
        track_df['Est. Arrival'] = track_df['Arrival'].dt.strftime('%H:%M WIB')
        st.dataframe(track_df, use_container_width=True)

# ==========================================
# TAB 3: INVENTORY
# ==========================================
elif menu == "Inventory Health":
    st.title("📦 Inventory Management")
    
    c1, c2 = st.columns(2)
    with c1: wh_filter = st.selectbox("Gudang:", ["All", "DC Cikarang", "DC Surabaya", "DC Medan"])
    with c2: prod_filter = st.selectbox("Produk:", ["All Products"] + list(df_master[df_master['Category']=='Inventory_Snapshot']['Item'].unique()))

    df_inv = df_master[df_master['Category']=='Inventory_Snapshot']
    if wh_filter != "All": df_inv = df_inv[df_inv['Warehouse'] == wh_filter]
    if prod_filter != "All Products": df_inv = df_inv[df_inv['Item'] == prod_filter]
    
    total_stock = df_inv['Qty'].sum()
    
    # Blue Box Metric
    st.markdown("""
    <div style="border: 2px solid #0F4C81; background-color: #f0f8ff; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <h4 style="color: #0F4C81; margin:0;">⚠️ Risk & Service Aggregate</h4>
        <div style="display: flex; justify-content: space-around; margin-top: 10px;">
            <div><b>Stockout Risk:</b> <span style="color:red;">2 SKU</span></div>
            <div><b>Service Level:</b> <span style="color:green;">98.5%</span></div>
            <div><b>Current Stock:</b> """+ f"{total_stock:,}" +""" Unit</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("📈 Daily Stock Trend")
    dates = pd.date_range(end=curr_time, periods=30)
    trend_vals = np.random.randint(total_stock-5000, total_stock+5000, 30)
    df_trend = pd.DataFrame({'Date': dates, 'Stock': trend_vals})
    st.altair_chart(alt.Chart(df_trend).mark_line(color='#0F4C81').encode(x='Date', y='Stock').properties(height=250), use_container_width=True)
    
    st.subheader("Detailed Stock per DC")
    st.dataframe(df_inv[['Item', 'Warehouse', 'Qty']].reset_index(drop=True), use_container_width=True)

# ==========================================
# TAB 4: FORECASTING (MODE PITCHING/STATIS)
# ==========================================
elif menu == "AI Forecasting":
    st.title("📈 AI Demand Forecasting")
    st.caption("Visualisasi prediksi demand berbasis GNN (Graph Neural Network).")

    # 1. PENJELASAN LOGIKA (Untuk Pitching)
    with st.expander("🧠 Lihat Logika Model AI (How it works)", expanded=True):
        st.markdown("""
        **Sistem Forecasting Hybrid Spatio-Temporal:**
        1.  **Input:** Historis penjualan (3 tahun), Data promosi, Kalender event (Lebaran/Natal).
        2.  **Processing:** GNN mempelajari korelasi antar-wilayah (Spillover effect).
        3.  **Output:** Peta prediksi demand per provinsi untuk alokasi stok proaktif.
        """)

    st.divider()

    # 2. SKENARIO (Dummy Selectors)
    c_s1, c_s2 = st.columns(2)
    with c_s1: st.selectbox("Skenario Model:", ["Skenario Optimis (Promo Lebaran)", "Skenario Normal"])
    with c_s2: st.selectbox("Horizon Waktu:", ["Next 30 Days", "Next Quarter"])

    # 3. PETA FORECAST (HARDCODED STORYTELLING)
    st.subheader("🗺️ Prediksi Distribusi Demand (Pulau Jawa)")
    
    # Data Manual untuk Cerita: Jakarta & Jabar Merah (Butuh Stok)
    static_map_data = [
        {"Propinsi": "DKI Jakarta", "Demand": 85000, "Color": [200, 0, 0]},     # Merah Tua
        {"Propinsi": "Jawa Barat",  "Demand": 62000, "Color": [255, 140, 0]},   # Oranye
        {"Propinsi": "Jawa Timur",  "Demand": 45000, "Color": [255, 215, 0]},   # Kuning
        {"Propinsi": "Jawa Tengah", "Demand": 38000, "Color": [255, 215, 0]},   # Kuning
        {"Propinsi": "Banten",      "Demand": 25000, "Color": [0, 128, 0]},     # Hijau
        {"Propinsi": "Sumatera Utara", "Demand": 15000, "Color": [0, 128, 0]}   # Hijau
    ]
    
    # Inject warna ke Peta Manual
    colored_features = []
    for feature in geojson_indo['features']:
        prov_name = feature['properties']['Propinsi']
        color = [200, 200, 200] # Default abu
        demand_val = 0
        
        for item in static_map_data:
            if item['Propinsi'] == prov_name:
                color = item['Color']
                demand_val = item['Demand']
                break
        
        feature['properties']['fill_color'] = color
        feature['properties']['demand_val'] = demand_val
        colored_features.append(feature)
        
    geojson_indo['features'] = colored_features

    # Render Peta
    st.pydeck_chart(pdk.Deck(
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        initial_view_state=pdk.ViewState(latitude=-6.5, longitude=110, zoom=5.5),
        layers=[pdk.Layer("GeoJsonLayer", geojson_indo, pickable=True, filled=True, get_fill_color="properties.fill_color", get_line_color=[255, 255, 255], opacity=0.6)],
        tooltip={"html": "<b>{Propinsi}</b><br/>Prediksi Demand: {demand_val} Units"}
    ))

    # 4. REKOMENDASI AI
    st.info("💡 **AI Recommendation:** Segera lakukan *Stock Transfer* sebesar **15,000 unit** dari Gudang Surabaya ke Gudang Jakarta untuk mengantisipasi lonjakan demand di area Merah.")

    # 5. GRAFIK FORECAST (STATIS CANTIK)
    st.subheader("📊 Forecast Accuracy Validation")
    x = np.arange(30)
    y_actual = 100 + np.sin(x/5)*20 + np.random.normal(0, 5, 30)
    y_forecast = 100 + np.sin(x/5)*20 # Smooth curve
    
    df_chart = pd.DataFrame({'Day': list(range(1, 31)), 'Actual Sales': y_actual, 'AI Forecast': y_forecast})
    df_melt = df_chart.melt('Day', var_name='Type', value_name='Sales')
    
    chart = alt.Chart(df_melt).mark_line(point=True).encode(
        x='Day', y='Sales', color=alt.Color('Type', scale=alt.Scale(range=['#0F4C81', '#C9A446'])),
        tooltip=['Day', 'Sales', 'Type']
    ).properties(height=300)
    
    st.altair_chart(chart, use_container_width=True)