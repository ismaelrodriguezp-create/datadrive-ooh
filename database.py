import sqlite3
import os
import pandas as pd
from datetime import date

DB_PATH = "ooh_datadrive.db"

# Columnas: ID(1), Nombre(2), Lat(3), Lng(4), Distrito(5), Dir(6), Tipo(7), Cara(8), Ancho(9), Alto(10), Traf(11), Precio(12), NSE(13), Demo(14), Punt(15)
SAMPLE_PANELS = [
    (1,  "MIR-01 Av. Larco",        -12.1211, -77.0283, "Miraflores", "Av. Larco cdra. 12", "Valla", "Norte", 12.0, 4.0, "Alto", 8500, "A", "Ejecutivos", 95),
    (2,  "MIR-02 Óvalo Miraflores", -12.1180, -77.0310, "Miraflores", "Óvalo Miraflores", "Digital", "Este", 6.0, 3.0, "Muy Alto", 12000, "A/B", "Jóvenes/Turistas", 98),
    (3,  "SI-01 Javier Prado",      -12.0974, -77.0356, "San Isidro", "Av. Javier Prado Este 8", "Valla", "Sur", 14.0, 4.5, "Muy Alto", 10500, "A", "Ejecutivos", 99),
    (4,  "SI-02 Rep. Panamá",       -12.0950, -77.0420, "San Isidro", "Av. Rep. Panamá 3", "Tótem", "Doble", 1.8, 4.0, "Medio", 4500, "B", "Oficinistas", 75),
    (5,  "SUR-01 Primavera",        -12.1188, -76.9921, "Surco", "Av. Primavera 20", "Valla", "Norte", 12.0, 4.0, "Alto", 6500, "A/B", "Familias", 82),
    (6,  "SUR-02 El Derby",         -12.1210, -76.9880, "Surco", "Av. El Derby 5", "Digital", "Oeste", 8.0, 4.0, "Alto", 11000, "A", "Ejecutivos", 90),
    (7,  "LM-01 Av. La Molina",     -12.0740, -76.9393, "La Molina", "Av. La Molina 15", "Valla", "Este", 12.0, 4.0, "Medio", 5500, "A/B", "Estudiantes", 68),
    (8,  "SB-01 Av. San Luis",      -12.1011, -77.0005, "San Borja", "Av. San Luis 10", "Valla", "Norte", 14.0, 5.0, "Alto", 9000, "B", "Adultos", 80),
    (9,  "JM-01 Av. Brasil",        -12.0775, -77.0502, "Jesús María", "Av. Brasil 28", "Valla", "Sur", 12.0, 4.0, "Alto", 6000, "B/C", "Público General", 72),
    (10, "BAR-01 Av. Grau",         -12.1500, -77.0219, "Barranco", "Av. Grau 7", "Tótem", "Doble", 1.8, 4.0, "Bajo", 3000, "A/B", "Turistas/Bohemios", 60),
    (11, "CHO-01 Av. Huaylas",      -12.1693, -77.0185, "Chorrillos", "Av. Huaylas 12", "Valla", "Norte", 12.0, 4.0, "Medio", 5000, "C", "Familias", 65),
    (12, "ATE-01 Javier Prado E",   -12.0606, -76.9356, "Ate", "Av. Javier Prado E 40", "Valla", "Sur", 14.0, 5.0, "Muy Alto", 7500, "C", "Trabajadores", 88),
    (13, "LO-01 Mendiola",          -11.9845, -77.0689, "Los Olivos", "Av. Alfredo Mendiola 18", "Digital", "Norte", 6.0, 3.0, "Muy Alto", 10000, "B/C", "Comerciantes", 92),
    (14, "SM-01 La Marina",         -12.0769, -77.0864, "San Miguel", "Av. La Marina 22", "Valla", "Este", 12.0, 4.0, "Alto", 8000, "B", "Familias", 85),
    (15, "LIN-01 Arequipa",         -12.0870, -77.0319, "Lince", "Av. Arequipa 20", "Valla", "Oeste", 12.0, 4.0, "Alto", 7800, "B", "Adultos", 84),
]

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    # Eliminamos para asegurar nueva estructura
    c.execute("DROP TABLE IF EXISTS paneles")
    c.execute("""
        CREATE TABLE paneles (
            id INTEGER PRIMARY KEY,
            nombre TEXT, latitud REAL, longitud REAL, distrito TEXT,
            direccion TEXT, tipo TEXT, cara TEXT, ancho_m REAL, alto_m REAL,
            nivel_trafico TEXT, precio_mensual REAL, nse TEXT, demografia TEXT, puntuacion INTEGER,
            activo INTEGER DEFAULT 1
        )
    """)
    c.executemany("INSERT INTO paneles VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1)", SAMPLE_PANELS)
    
    # Asegurar tablas de soporte
    c.execute("CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY, empresa TEXT, ruc TEXT, contacto TEXT, email TEXT, telefono TEXT, sector TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS contratos (id INTEGER PRIMARY KEY AUTOINCREMENT, panel_id INTEGER, cliente_id INTEGER, fecha_inicio TEXT, fecha_fin TEXT, tarifa_mensual REAL, nombre_campana TEXT, notas TEXT)")
    
    conn.commit()
    conn.close()

def get_paneles_con_estado():
    conn = get_conn()
    # Query explícito para evitar errores de p.*
    query = """
        SELECT p.id, p.nombre, p.latitud, p.longitud, p.distrito, p.direccion, 
               p.tipo, p.cara, p.ancho_m, p.alto_m, p.nivel_trafico, 
               p.precio_mensual, p.nse, p.demografia, p.puntuacion,
               c.fecha_fin, cl.empresa AS cliente, c.nombre_campana
        FROM paneles p
        LEFT JOIN contratos c ON c.panel_id = p.id AND c.fecha_fin >= date('now')
        LEFT JOIN clientes cl ON cl.id = c.cliente_id
        WHERE p.activo = 1
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    today = date.today()
    def calc_status(row):
        if not row["fecha_fin"] or str(row["fecha_fin"]) == 'None': return "libre"
        end = date.fromisoformat(str(row["fecha_fin"]))
        return "por_vencer" if (end - today).days <= 30 else "ocupado"
    
    df["estado"] = df.apply(calc_status, axis=1)
    df["dias_restantes"] = df["fecha_fin"].apply(lambda f: (date.fromisoformat(str(f)) - today).days if f and str(f)!='None' else None)
    return df
