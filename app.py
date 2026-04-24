import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import database as db

# ── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DataDrive OOH · Input",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── INIT DB ─────────────────────────────────────────────────────────────────
db.init_db()

# ── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

/* KPI cards */
.kpi-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    text-align: center;
}
.kpi-val  { font-size: 2.2rem; font-weight: 800; margin: 0; }
.kpi-lbl  { font-size: .78rem; color: #94a3b8; margin: 0; }

/* Legend */
.legend-item { display:flex; align-items:center; gap:.5rem; font-size:.82rem; margin:.25rem 0; }
.dot { width:12px; height:12px; border-radius:50%; display:inline-block; }

/* Status badge */
.badge {
    display:inline-block; padding:.15rem .55rem; border-radius:999px;
    font-size:.72rem; font-weight:700;
}
.badge-ocu  { background:rgba(34,197,94,.15);  color:#22c55e; }
.badge-venc { background:rgba(245,158,11,.15); color:#f59e0b; }
.badge-lib  { background:rgba(239,68,68,.15);  color:#ef4444; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 **DataDrive OOH**")
    st.markdown("*Panel Manager · Input Perú*")
    st.divider()
    page = st.radio("Navegación", [
        "🗺️  Mapa de Paneles",
        "📊  Dashboard KPIs",
        "📋  Contratos",
        "🏢  Clientes",
        "➕  Agregar Datos",
    ], label_visibility="collapsed")
    st.divider()
    st.markdown("""
    **Leyenda del mapa**
    <div class="legend-item"><span class="dot" style="background:#22c55e"></span> Ocupado</div>
    <div class="legend-item"><span class="dot" style="background:#f59e0b"></span> Por vencer (&le;30 d)</div>
    <div class="legend-item"><span class="dot" style="background:#ef4444"></span> Libre</div>
    """, unsafe_allow_html=True)
    st.divider()
    st.caption("DataDrive Startup · Lima 2025")

# ── HELPERS ─────────────────────────────────────────────────────────────────
COLOR_MAP = {"ocupado": "#22c55e", "por_vencer": "#f59e0b", "libre": "#ef4444"}
LABEL_MAP = {"ocupado": "Ocupado", "por_vencer": "Por vencer", "libre": "Libre"}

def badge(estado):
    cls = {"ocupado":"badge-ocu","por_vencer":"badge-venc","libre":"badge-lib"}.get(estado,"")
    return f'<span class="badge {cls}">{LABEL_MAP.get(estado, estado)}</span>'

def build_map(df, filtro_estado=None, filtro_distrito=None):
    subset = df.copy()
    if filtro_estado:
        subset = subset[subset["estado"].isin(filtro_estado)]
    if filtro_distrito:
        subset = subset[subset["distrito"].isin(filtro_distrito)]

    m = folium.Map(
        location=[-12.08, -77.05],
        zoom_start=12,
        tiles="CartoDB dark_matter",
    )

    for _, row in subset.iterrows():
        color  = COLOR_MAP.get(row["estado"], "#6b7280")
        dias   = int(row["dias_restantes"]) if pd.notna(row["dias_restantes"]) else None
        popup_html = f"""
        <div style='font-family:Inter,sans-serif;min-width:210px'>
          <b style='font-size:13px'>{row['nombre']}</b><br/>
          <span style='color:#94a3b8;font-size:11px'>{row['direccion']} · {row['distrito']}</span>
          <hr style='margin:6px 0;border-color:#333'/>
          <b>Estado:</b> <span style='color:{color};font-weight:700'>{LABEL_MAP.get(row['estado'])}</span><br/>
          <b>Tipo:</b> {row['tipo']} — {row['cara']}<br/>
          <b>Dimensiones:</b> {row['ancho_m']}m × {row['alto_m']}m<br/>
          <b>Tráfico:</b> {row['nivel_trafico']}<br/>
          <b>Tarifa:</b> S/ {int(row['precio_mensual']):,}/mes<br/>
          <hr style='margin:6px 0;border-color:#333'/>
          <b>Cliente:</b> {row['cliente'] or '—'}<br/>
          <b>Campaña:</b> {row['nombre_campana'] or '—'}<br/>
          <b>Inicio:</b> {row['fecha_inicio'] or '—'}<br/>
          <b>Fin:</b> {row['fecha_fin'] or '—'}
          {f"<br/><b>Días restantes:</b> <span style='color:{color}'>{dias} días</span>" if dias else ''}
        </div>
        """
        folium.CircleMarker(
            location=[row["latitud"], row["longitud"]],
            radius=11,
            color="white",
            weight=1.5,
            fill=True,
            fill_color=color,
            fill_opacity=0.88,
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=f"{'🟢' if row['estado']=='ocupado' else '🟡' if row['estado']=='por_vencer' else '🔴'} {row['nombre']}",
        ).add_to(m)
    return m

# ═══════════════════════════════════════════════════════════════════════════
# PAGE 1 — MAPA
# ═══════════════════════════════════════════════════════════════════════════
if "🗺️" in page:
    st.markdown("# 🗺️ Mapa de Paneles")
    df = db.get_paneles_con_estado()

    col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
    with col_f1:
        filtro_estado = st.multiselect(
            "Filtrar por estado",
            ["ocupado", "por_vencer", "libre"],
            format_func=lambda x: LABEL_MAP[x],
        )
    with col_f2:
        distritos = sorted(df["distrito"].unique().tolist())
        filtro_dist = st.multiselect("Filtrar por distrito", distritos)
    with col_f3:
        filtro_tipo = st.multiselect("Filtrar por tipo", sorted(df["tipo"].dropna().unique().tolist()))

    subset = df.copy()
    if filtro_estado: subset = subset[subset["estado"].isin(filtro_estado)]
    if filtro_dist:   subset = subset[subset["distrito"].isin(filtro_dist)]
    if filtro_tipo:   subset = subset[subset["tipo"].isin(filtro_tipo)]

    # Metrics strip
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.metric("Total paneles", len(subset))
    with c2:
        n = len(subset[subset["estado"]=="ocupado"])
        st.metric("🟢 Ocupados", n)
    with c3:
        n = len(subset[subset["estado"]=="por_vencer"])
        st.metric("🟡 Por vencer", n)
    with c4:
        n = len(subset[subset["estado"]=="libre"])
        st.metric("🔴 Libres", n)

    mapa = build_map(subset)
    st_folium(mapa, width="100%", height=540)

    with st.expander("📋 Ver tabla de paneles filtrados"):
        show_cols = ["nombre","distrito","tipo","estado","cliente","fecha_fin","dias_restantes","precio_mensual"]
        st.dataframe(
            subset[show_cols].rename(columns={
                "nombre":"Panel","distrito":"Distrito","tipo":"Tipo",
                "estado":"Estado","cliente":"Cliente","fecha_fin":"Vence",
                "dias_restantes":"Días rest.","precio_mensual":"Tarifa S/"
            }),
            use_container_width=True,
            hide_index=True,
        )

# ═══════════════════════════════════════════════════════════════════════════
# PAGE 2 — KPIs
# ═══════════════════════════════════════════════════════════════════════════
elif "📊" in page:
    st.markdown("# 📊 Dashboard & KPIs")
    df = db.get_paneles_con_estado()

    total  = len(df)
    ocu    = len(df[df["estado"]=="ocupado"])
    venc   = len(df[df["estado"]=="por_vencer"])
    libre  = len(df[df["estado"]=="libre"])
    ocup_r = round((ocu + venc) / total * 100, 1) if total else 0
    mrr    = df[df["estado"].isin(["ocupado","por_vencer"])]["tarifa_mensual"].sum()

    k1,k2,k3,k4,k5,k6 = st.columns(6)
    k1.metric("Total Paneles",  total)
    k2.metric("Ocupados 🟢",    ocu)
    k3.metric("Por vencer 🟡",  venc)
    k4.metric("Libres 🔴",      libre)
    k5.metric("Ocupación",      f"{ocup_r}%")
    k6.metric("MRR (S/)",       f"{mrr:,.0f}")

    st.divider()
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Estado del inventario")
        fig_pie = px.pie(
            names=["Ocupado","Por vencer","Libre"],
            values=[ocu, venc, libre],
            color_discrete_sequence=["#22c55e","#f59e0b","#ef4444"],
            hole=0.55,
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(font=dict(color="#94a3b8")),
            margin=dict(t=10,b=10,l=10,r=10),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        st.subheader("Paneles por distrito")
        dist_df = df.groupby("distrito").size().reset_index(name="total").sort_values("total", ascending=True)
        fig_bar = px.bar(
            dist_df, x="total", y="distrito", orientation="h",
            color_discrete_sequence=["#3b82f6"],
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(color="#64748b", gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(color="#94a3b8"),
            margin=dict(t=10,b=10,l=10,r=10),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("💰 Revenue por tipo de panel")
    rev_df = df[df["estado"].isin(["ocupado","por_vencer"])].groupby("tipo")["tarifa_mensual"].sum().reset_index()
    fig_rev = px.bar(
        rev_df, x="tipo", y="tarifa_mensual",
        color_discrete_sequence=["#8b5cf6"],
        text_auto=True,
        labels={"tipo":"Tipo","tarifa_mensual":"S/ / mes"},
    )
    fig_rev.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(color="#64748b"),
        yaxis=dict(color="#64748b", gridcolor="rgba(255,255,255,0.05)"),
        margin=dict(t=10,b=10,l=10,r=10),
    )
    st.plotly_chart(fig_rev, use_container_width=True)

    st.subheader("🚨 Contratos que vencen en los próximos 30 días")
    por_vencer = df[df["estado"]=="por_vencer"][["nombre","distrito","cliente","fecha_fin","dias_restantes","tarifa_mensual"]].sort_values("dias_restantes")
    if not por_vencer.empty:
        st.dataframe(por_vencer.rename(columns={
            "nombre":"Panel","distrito":"Distrito","cliente":"Cliente",
            "fecha_fin":"Vence","dias_restantes":"Días rest.","tarifa_mensual":"S//mes"
        }), use_container_width=True, hide_index=True)
    else:
        st.success("✅ Sin contratos próximos a vencer.")

# ═══════════════════════════════════════════════════════════════════════════
# PAGE 3 — CONTRATOS
# ═══════════════════════════════════════════════════════════════════════════
elif "📋" in page:
    st.markdown("# 📋 Gestión de Contratos")
    df_c = db.get_contratos()
    today = date.today()

    def row_status(fin):
        try:
            end = date.fromisoformat(str(fin))
            diff = (end - today).days
            if diff < 0:   return "Vencido"
            if diff <= 30: return "Por vencer"
            return "Activo"
        except: return "—"

    df_c["Estado"]     = df_c["fecha_fin"].apply(row_status)
    df_c["Días rest."] = df_c["fecha_fin"].apply(
        lambda f: (date.fromisoformat(str(f)) - today).days if f else None
    )

    buscar = st.text_input("🔍 Buscar por cliente, panel o campaña")
    if buscar:
        mask = df_c.apply(lambda r: buscar.lower() in str(r).lower(), axis=1)
        df_c = df_c[mask]

    st.dataframe(
        df_c[["id","panel","distrito","cliente","fecha_inicio","fecha_fin",
              "tarifa_mensual","nombre_campana","Estado","Días rest.","notas"]].rename(columns={
            "id":"#","panel":"Panel","distrito":"Distrito","cliente":"Cliente",
            "fecha_inicio":"Inicio","fecha_fin":"Fin","tarifa_mensual":"S//mes",
            "nombre_campana":"Campaña","notas":"Notas",
        }),
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "⬇️ Exportar CSV",
        df_c.to_csv(index=False).encode("utf-8"),
        "contratos_datadrive.csv",
        "text/csv",
    )

# ═══════════════════════════════════════════════════════════════════════════
# PAGE 4 — CLIENTES
# ═══════════════════════════════════════════════════════════════════════════
elif "🏢" in page:
    st.markdown("# 🏢 Directorio de Clientes")
    df_cl = db.get_clientes()
    df_ct = db.get_contratos()

    revenue = (
        df_ct[df_ct["fecha_fin"] >= str(date.today())]
        .groupby("cliente")["tarifa_mensual"].sum()
        .reset_index()
        .rename(columns={"cliente":"empresa","tarifa_mensual":"MRR (S/)"})
    )
    df_cl = df_cl.merge(revenue, on="empresa", how="left")
    df_cl["MRR (S/)"] = df_cl["MRR (S/)"].fillna(0)

    for _, row in df_cl.iterrows():
        with st.expander(f"🏢 {row['empresa']}  —  {row['sector']}  |  MRR: S/ {row['MRR (S/)']:,.0f}"):
            c1, c2 = st.columns(2)
            c1.markdown(f"**RUC:** {row['ruc']}")
            c1.markdown(f"**Contacto:** {row['contacto']}")
            c2.markdown(f"**Email:** {row['email']}")
            c2.markdown(f"**Teléfono:** {row['telefono']}")
            contratos_cli = df_ct[df_ct["cliente"] == row["empresa"]]
            if not contratos_cli.empty:
                st.dataframe(
                    contratos_cli[["panel","fecha_inicio","fecha_fin","tarifa_mensual","nombre_campana"]].rename(columns={
                        "panel":"Panel","fecha_inicio":"Inicio","fecha_fin":"Fin",
                        "tarifa_mensual":"S//mes","nombre_campana":"Campaña"
                    }),
                    use_container_width=True, hide_index=True,
                )

# ═══════════════════════════════════════════════════════════════════════════
# PAGE 5 — AGREGAR DATOS
# ═══════════════════════════════════════════════════════════════════════════
elif "➕" in page:
    st.markdown("# ➕ Agregar Datos")
    tab1, tab2, tab3 = st.tabs(["📍 Nuevo Panel", "📝 Nuevo Contrato", "🏢 Nuevo Cliente"])

    with tab1:
        st.subheader("Registrar nuevo panel")
        with st.form("form_panel"):
            c1, c2 = st.columns(2)
            nombre   = c1.text_input("Nombre del panel *")
            distrito = c2.text_input("Distrito *")
            direccion = st.text_input("Dirección")
            c3, c4   = st.columns(2)
            lat      = c3.number_input("Latitud *",  value=-12.08, format="%.6f")
            lng      = c4.number_input("Longitud *", value=-77.05, format="%.6f")
            c5, c6   = st.columns(2)
            tipo     = c5.selectbox("Tipo", ["Valla","Pantalla Digital","Tótem","Mupí","Banner"])
            cara     = c6.selectbox("Cara", ["Norte","Sur","Este","Oeste","Doble cara"])
            c7, c8, c9, c10 = st.columns(4)
            ancho    = c7.number_input("Ancho (m)", value=12.0)
            alto     = c8.number_input("Alto (m)",  value=4.0)
            trafico  = c9.selectbox("Tráfico", ["Alto","Medio","Bajo"])
            precio   = c10.number_input("Tarifa S//mes", value=5000)
            submitted = st.form_submit_button("✅ Guardar Panel", use_container_width=True)
            if submitted:
                if nombre and distrito:
                    db.insert_panel(nombre,lat,lng,distrito,direccion,tipo,cara,ancho,alto,trafico,precio)
                    st.success(f"✅ Panel **{nombre}** registrado correctamente.")
                    st.rerun()
                else:
                    st.error("Nombre y Distrito son obligatorios.")

    with tab2:
        st.subheader("Registrar nuevo contrato")
        df_pan = db.get_paneles_con_estado()
        df_cli = db.get_clientes()
        with st.form("form_contrato"):
            panel_opts  = dict(zip(df_pan["nombre"], df_pan["id"]))
            cliente_opts = dict(zip(df_cli["empresa"], df_cli["id"]))
            panel_sel   = st.selectbox("Panel *",   list(panel_opts.keys()))
            cliente_sel = st.selectbox("Cliente *", list(cliente_opts.keys()))
            c1, c2  = st.columns(2)
            inicio  = c1.date_input("Fecha inicio *", value=date.today())
            fin     = c2.date_input("Fecha fin *",    value=date.today() + timedelta(days=90))
            tarifa  = st.number_input("Tarifa mensual S/ *", value=5000)
            campana = st.text_input("Nombre de campaña")
            notas   = st.text_area("Notas", height=80)
            submitted = st.form_submit_button("✅ Guardar Contrato", use_container_width=True)
            if submitted:
                db.insert_contrato(panel_opts[panel_sel], cliente_opts[cliente_sel], inicio, fin, tarifa, campana, notas)
                st.success("✅ Contrato registrado correctamente.")
                st.rerun()

    with tab3:
        st.subheader("Registrar nuevo cliente")
        with st.form("form_cliente"):
            c1, c2 = st.columns(2)
            empresa  = c1.text_input("Empresa *")
            ruc      = c2.text_input("RUC")
            contacto = c1.text_input("Contacto")
            email    = c2.text_input("Email")
            telefono = c1.text_input("Teléfono")
            sector   = c2.selectbox("Sector", ["Retail","Financiero","Telecomunicaciones","Alimentos","Bebidas","Salud","Educación","Inmobiliario","Otro"])
            submitted = st.form_submit_button("✅ Guardar Cliente", use_container_width=True)
            if submitted:
                if empresa:
                    db.insert_cliente(empresa, ruc, contacto, email, telefono, sector)
                    st.success(f"✅ Cliente **{empresa}** registrado.")
                    st.rerun()
                else:
                    st.error("El nombre de empresa es obligatorio.")
