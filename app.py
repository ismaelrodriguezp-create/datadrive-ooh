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

# Asegurar DB inicializada
if 'db_ready' not in st.session_state:
    db.init_db()
    st.session_state['db_ready'] = True

# ── DISEÑO PROFESIONAL (Colores Cohesivos) ─────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* Fondo y contenedores */
    .stApp { background-color: #0e1117; }
    
    /* Métricas con estilo Dashboard Pro */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 20px;
    }
    
    /* Sidebar limpia */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Badges de estado */
    .badge { padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
    .badge-ok { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
    .badge-warn { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
    .badge-err { background: rgba(239, 68, 68, 0.15); color: #f87171; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='color:#3b82f6;'>DataDrive</h2>", unsafe_allow_html=True)
    st.caption("Gestión Inteligente de Paneles OOH")
    st.divider()
    page = st.radio("Navegación", 
                    ["🗺️ Mapa de Paneles", "📊 Dashboard KPIs", "📋 Contratos", "🏢 Clientes", "➕ Agregar Datos"],
                    label_visibility="collapsed")
    st.divider()
    
    if page == "🗺️ Mapa de Paneles":
        st.subheader("Inteligencia de Audiencia")
        nse_filter = st.multiselect("NSE Objetivo", ["A", "B", "C"], default=["A", "B"])
        demo_filter = st.multiselect("Público Target", 
                                     ["Ejecutivos", "Jóvenes/Turistas", "Familias", "Estudiantes", "Trabajadores", "Público General"],
                                     default=["Ejecutivos", "Jóvenes/Turistas"])
        show_heat = st.checkbox("Mapa de Calor (Tráfico)", value=True)
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.caption("v2.5 Professional Edition")

# ── DATA FETCH ────────────────────────────────────────────────────────
df = db.get_paneles_con_estado()

# ── PAGE 1: MAPA ──────────────────────────────────────────────────────
if page == "🗺️ Mapa de Paneles":
    st.title("Mapa de Inventario e Inteligencia")
    
    # Filtros aplicados
    subset = df.copy()
    if nse_filter: subset = subset[subset['nse'].str.contains('|'.join(nse_filter))]
    if demo_filter: subset = subset[subset['demografia'].str.contains('|'.join(demo_filter))]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Paneles", len(df))
    c2.metric("Filtrados", len(subset))
    c3.metric("Ocupación", f"{int(len(df[df['estado']!='libre'])/len(df)*100)}%")
    c4.metric("Score Medio", f"{int(subset['puntuacion'].mean())} pts")

    m = folium.Map(location=[-12.08, -77.05], zoom_start=12, tiles="CartoDB dark_matter")
    
    if show_heat:
        HeatMap([[r['latitud'], r['longitud'], r['puntuacion']] for _, r in df.iterrows()], 
                radius=25, blur=15, gradient={0.4: '#3b82f6', 0.65: '#10b981', 1: '#ef4444'}).add_to(m)

    for _, row in subset.iterrows():
        color = "#22c55e" if row["estado"]=="ocupado" else "#f59e0b" if row["estado"]=="por_vencer" else "#ef4444"
        folium.CircleMarker(
            location=[row["latitud"], row["longitud"]],
            radius=10, color="white", weight=0.5, fill=True, fill_color=color, fill_opacity=0.8,
            popup=f"<b>{row['nombre']}</b><br>NSE: {row['nse']}<br>Target: {row['demografia']}<br>Tarifa: S/ {row['precio_mensual']}"
        ).add_to(m)

    st_folium(m, width="100%", height=550)

# ── PAGE 2: KPIs ──────────────────────────────────────────────────────
elif page == "📊 Dashboard KPIs":
    st.title("Análisis de Rendimiento")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Revenue Mensual", f"S/ {df[df['estado']!='libre']['precio_mensual'].sum():,}")
    m2.metric("Ingresos en Riesgo", f"S/ {df[df['estado']=='por_vencer']['precio_mensual'].sum():,}", delta_color="inverse")
    m3.metric("Paneles Libres", len(df[df['estado']=='libre']))
    m4.metric("Valor del Inventario", f"S/ {df['precio_mensual'].sum():,}")

    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Distribución por NSE")
        fig = px.pie(df, names="nse", color="nse", hole=0.5, 
                     color_discrete_sequence=px.colors.sequential.Blues_r, template="plotly_dark")
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
    with col_b:
        st.subheader("Eficiencia por Distrito")
        fig2 = px.bar(df.groupby("distrito")["puntuacion"].mean().reset_index(), 
                      x="puntuacion", y="distrito", orientation='h', template="plotly_dark",
                      color_discrete_sequence=["#3b82f6"])
        fig2.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig2, use_container_width=True)

# ── PAGE 3: CONTRATOS ─────────────────────────────────────────────────
elif page == "📋 Contratos":
    st.title("Gestión de Contratos")
    df_contratos = db.get_paneles_con_estado()[["nombre", "distrito", "cliente", "fecha_fin", "estado", "precio_mensual"]]
    st.dataframe(df_contratos, use_container_width=True, hide_index=True)

# ── PAGE 4: CLIENTES ──────────────────────────────────────────────────
elif page == "🏢 Clientes":
    st.title("Directorio de Clientes")
    # Simulación de lista de clientes para la vista profesional
    st.info("Visualizando clientes activos y potencial de renovación.")
    st.dataframe(df[df['cliente'].notna()][["cliente", "nombre_campana", "precio_mensual"]], use_container_width=True)

# ── PAGE 5: AGREGAR ───────────────────────────────────────────────────
else:
    st.title("Gestión de Datos")
    st.markdown("Use este panel para actualizar el inventario o los contratos.")
    with st.expander("⚙️ Herramientas de Sistema"):
        if st.button("Resetear Base de Datos"):
            db.init_db()
            st.rerun()
    st.success("Sistema listo para nuevas entradas.")
