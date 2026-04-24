import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import pandas as pd
import plotly.express as px
import database as db
from datetime import date, timedelta

# ── CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="DataDrive OOH Manager", page_icon="📊", layout="wide")

# Forzar inicialización limpia
if 'initialized_v25' not in st.session_state:
    db.init_db()
    st.session_state['initialized_v25'] = True

# ── DISEÑO PROFESIONAL ────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0e1117; }
    [data-testid="stMetric"] { background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 10px; padding: 20px; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid rgba(255, 255, 255, 0.05); }
</style>
""", unsafe_allow_html=True)

# ── DATA FETCH ────────────────────────────────────────────────────────
df = db.get_paneles_con_estado()

# ── SIDEBAR ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='color:#3b82f6;'>DataDrive</h2>", unsafe_allow_html=True)
    st.caption("Gestión Inteligente v2.5")
    st.divider()
    page = st.radio("Menú", ["🗺️ Mapa", "📊 KPIs", "📋 Contratos", "🏢 Clientes", "⚙️ Sistema"], label_visibility="collapsed")
    st.divider()
    
    if page == "🗺️ Mapa":
        st.subheader("Filtros de Audiencia")
        nse_filter = st.multiselect("NSE", ["A", "B", "C"], default=["A", "B"])
        demo_filter = st.multiselect("Target", df['demografia'].unique() if 'demografia' in df.columns else [], default=None)
        show_heat = st.checkbox("Mapa de Calor", value=True)

# ── PÁGINAS ───────────────────────────────────────────────────────────
if page == "🗺️ Mapa":
    st.title("Mapa de Inventario")
    
    subset = df.copy()
    if 'nse' in subset.columns and nse_filter:
        subset = subset[subset['nse'].str.contains('|'.join(nse_filter))]
    if 'demografia' in subset.columns and demo_filter:
        subset = subset[subset['demografia'].isin(demo_filter)]

    m = folium.Map(location=[-12.08, -77.05], zoom_start=12, tiles="CartoDB dark_matter")
    if show_heat and 'puntuacion' in df.columns:
        HeatMap([[r['latitud'], r['longitud'], r['puntuacion']] for _, r in df.iterrows()], radius=20).add_to(m)

    for _, row in subset.iterrows():
        color = "#22c55e" if row["estado"]=="ocupado" else "#f59e0b" if row["estado"]=="por_vencer" else "#ef4444"
        folium.CircleMarker(
            location=[row["latitud"], row["longitud"]], radius=8, color="white", weight=0.5, 
            fill=True, fill_color=color, fill_opacity=0.8,
            tooltip=f"{row['nombre']} | NSE: {row.get('nse','-')}"
        ).add_to(m)
    st_folium(m, width="100%", height=550)

elif page == "📊 KPIs":
    st.title("Dashboard Operativo")
    c1, c2, c3 = st.columns(3)
    c1.metric("Revenue", f"S/ {df[df['estado']!='libre']['precio_mensual'].sum():,}")
    c2.metric("Paneles Libres", len(df[df['estado']=='libre']))
    c3.metric("Ocupación", f"{int(len(df[df['estado']!='libre'])/len(df)*100)}%")

elif page == "⚙️ Sistema":
    st.title("Configuración de Sistema")
    if st.button("🔄 Forzar Reinicio de Base de Datos"):
        db.init_db()
        st.rerun()

else:
    st.title(page)
    st.dataframe(df)
