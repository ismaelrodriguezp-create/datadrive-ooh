import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import pandas as pd
import plotly.express as px
import database as db
from datetime import date, timedelta

# ── CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="DataDrive OOH — Strategy Center", page_icon="📈", layout="wide")
db.init_db()

# ── CSS PREMIUM ────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stMetric { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 15px; }
    .roadmap-card { background: rgba(59,130,246,0.05); border-left: 4px solid #3b82f6; padding: 20px; border-radius: 8px; margin-bottom: 15px; }
    .audience-badge { background: #3b82f6; color: white; padding: 2px 10px; border-radius: 10px; font-size: 0.7rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
    st.title("DataDrive OOH")
    st.caption("Intelligence Strategy v2.0")
    st.divider()
    page = st.selectbox("Módulo Principal", ["🚀 Estrategia & Pitch", "🗺️ Mapa de Inteligencia", "📊 Dashboard Operativo", "➕ Gestión de Datos"])
    st.divider()
    if page == "🗺️ Mapa de Inteligencia":
        st.subheader("Filtros de Audiencia")
        target_nse = st.multiselect("NSE Objetivo", ["A", "B", "C"], default=["A", "B"])
        target_demo = st.multiselect("Perfil Demográfico", ["Ejecutivos", "Jóvenes/Turistas", "Familias", "Estudiantes", "Trabajadores"], default=["Ejecutivos"])
        st.divider()
        show_heatmap = st.checkbox("Capa de Calor (Tráfico)", value=True)

# ── PAGE 1: ESTRATEGIA & PITCH ─────────────────────────────────────────
if page == "🚀 Estrategia & Pitch":
    st.title("🚀 De vender 'Espacios' a vender 'Inteligencia'")
    st.subheader("Propuesta de Valor Data-Driven para la Gerencia")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"""
        ### 1. El Nuevo Paradigma: OOH Científico
        Como **Ingeniero Estadístico**, transformamos el medio intuitivo en uno basado en resultados predecibles.
        
        <div class="roadmap-card">
            <b>🛡️ Eliminación de Desperdicio (30%):</b> Nuestros modelos de atribución cruzan datos de movilidad real para impactar solo a quien importa. No vendemos "vistas", vendemos "relevancia".
        </div>
        <div class="roadmap-card">
            <b>🧠 Inteligencia de Audiencia (NSE A/B):</b> Mapeamos rutas de comportamiento específicas. Sabemos dónde está tu cliente a las 8 AM.
        </div>
        <div class="roadmap-card">
            <b>⚡ Optimización Real-Time (DOOH):</b> Motor de reglas dinámico que cambia anuncios según el clima, tráfico o eventos en vivo.
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.info("💡 **Argumento de Venta:** Seremos los únicos en el mercado peruano con reportes de impacto basados en ciencia, no en estimaciones visuales.")
        st.success("📈 **Nueva Fuente de Ingreso:** *Data-as-a-Service*. Cobrar por el análisis de audiencias además del panel.")

    st.divider()
    st.subheader("🧮 Simulador de Eficiencia de Campaña")
    c1, c2, c3 = st.columns(3)
    presupuesto = c1.number_input("Presupuesto Mensual (S/)", value=10000, step=1000)
    alcance_tradicional = c2.number_input("Impresiones Estimadas (Tradicional)", value=500000)
    precision = c3.slider("Optimización DataDrive (%)", 10, 50, 30)
    
    impacto_real = alcance_tradicional * (1 + precision/100)
    ahorro = presupuesto * (precision/100)
    
    res1, res2, res3 = st.columns(3)
    res1.metric("Alcance Optimizado", f"{int(impacto_real):,} imp.")
    res2.metric("Eficiencia Ganada", f"+{precision}%")
    res3.metric("Ahorro Estimado (S/)", f"S/ {int(ahorro):,}", delta="Eficiencia de Costos")

# ── PAGE 2: MAPA DE INTELIGENCIA ───────────────────────────────────────
elif page == "🗺️ Mapa de Inteligencia":
    st.title("🗺️ Mapa de Inteligencia de Audiencias")
    df = db.get_paneles_con_estado()
    
    # Filtrado inteligente
    subset = df.copy()
    if target_nse: subset = subset[subset['nse'].str.contains('|'.join(target_nse))]
    if target_demo: subset = subset[subset['demografia'].str.contains('|'.join(target_demo))]

    # Map construction
    m = folium.Map(location=[-12.08, -77.05], zoom_start=12, tiles="CartoDB dark_matter")
    
    if show_heatmap:
        heat_data = [[row['latitud'], row['longitud'], row['puntuacion']] for index, row in df.iterrows()]
        HeatMap(heat_data, radius=25, blur=15, gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}).add_to(m)

    for _, row in subset.iterrows():
        color = "green" if row["estado"]=="ocupado" else "orange" if row["estado"]=="por_vencer" else "red"
        html = f"""
        <div style='font-family:sans-serif; width:200px'>
            <b>{row['nombre']}</b><br/>
            <span style='font-size:0.8rem'>{row['direccion']}</span><hr/>
            <b>NSE:</b> {row['nse']} | <b>Puntaje:</b> {row['puntuacion']}/100<br/>
            <b>Target:</b> {row['demografia']}<br/>
            <b>Tarifa:</b> S/ {row['precio_mensual']}<br/>
            <b>Estado:</b> <span style='color:{color}'>{row['estado']}</span>
        </div>
        """
        folium.CircleMarker(
            location=[row["latitud"], row["longitud"]],
            radius=10, color="white", weight=1, fill=True, fill_color=color, fill_opacity=0.8,
            popup=folium.Popup(html, max_width=250)
        ).add_to(m)

    st_folium(m, width="100%", height=600)
    st.caption("🔥 La capa de calor muestra densidad de audiencia e intensidad de tráfico vehicular.")

# ── PAGE 3: DASHBOARD OPERATIVO ────────────────────────────────────────
elif page == "📊 Dashboard Operativo":
    st.title("📊 Indicadores de Gestión (Manager View)")
    df = db.get_paneles_con_estado()
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Ocupación Real", f"{int(len(df[df['estado']!='libre'])/len(df)*100)}%")
    m2.metric("Revenue Mensual", f"S/ {df[df['estado']!='libre']['precio_mensual'].sum():,}")
    m3.metric("Ingresos en Riesgo", f"S/ {df[df['estado']=='por_vencer']['precio_mensual'].sum():,}", delta_color="inverse")
    m4.metric("Puntuación Media", f"{int(df['puntuacion'].mean())} pts")

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Inventario por NSE")
        fig = px.bar(df.groupby("nse").size().reset_index(name="Cant"), x="nse", y="Cant", color="nse", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Potencial de Impacto por Distrito")
        fig2 = px.scatter(df, x="distrito", y="puntuacion", size="precio_mensual", color="tipo", hover_name="nombre", template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

# ── PAGE 4: GESTIÓN ────────────────────────────────────────────────────
else:
    st.title("➕ Gestión de Inventario y Clientes")
    st.info("Aquí puedes registrar nuevos paneles y contratos para alimentar el motor de inteligencia.")
    # (Formularios simplificados para ahorrar espacio)
    with st.expander("📝 Registrar Nuevo Contrato"):
        st.date_input("Fecha Inicio")
        st.date_input("Fecha Fin")
        st.button("Guardar Contrato")
