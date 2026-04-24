# 📊 DataDrive OOH · Panel Manager

Dashboard interactivo para gestión de paneles publicitarios (OOH) desarrollado con **Streamlit + Python**.

## 🚀 Demo en vivo
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://datadrive-ooh.streamlit.app)

## ✨ Funcionalidades

| Módulo | Descripción |
|--------|------------|
| 🗺️ **Mapa** | Visualiza los 25 paneles en Lima con círculos de color según estado |
| 📊 **KPIs** | Ocupación, MRR, distribución por distrito y alertas de vencimiento |
| 📋 **Contratos** | Tabla filtrable + exportación CSV |
| 🏢 **Clientes** | Directorio con revenue por cliente |
| ➕ **Agregar** | Formularios para nuevos paneles, contratos y clientes |

## 🎨 Colores del mapa
- 🟢 **Verde** — Panel ocupado (contrato activo > 30 días)
- 🟡 **Amarillo** — Por vencer (≤ 30 días)
- 🔴 **Rojo** — Libre (sin contrato activo)

## 🛠️ Instalación local

```bash
git clone https://github.com/TU_USUARIO/datadrive-ooh.git
cd datadrive-ooh
pip install -r requirements.txt
streamlit run app.py
```

## ☁️ Deploy en Streamlit Cloud

1. Sube este repositorio a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repositorio → selecciona `app.py`
4. ¡Listo! URL pública generada automáticamente

> **Nota:** La base de datos SQLite se reinicia en cada deploy. Para persistencia real, conecta a Supabase o Google Sheets.

## 📁 Estructura

```
datadrive-ooh/
├── app.py           # App principal Streamlit
├── database.py      # SQLite + datos de muestra
├── requirements.txt
├── .streamlit/
│   └── config.toml  # Tema dark
└── README.md
```

## 👨‍💻 Desarrollado por
**Bryan** · DataDrive Startup · Lima, Perú · 2025
