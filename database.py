import sqlite3
import os
from datetime import date

DB_PATH = "ooh_datadrive.db"

SAMPLE_PANELS = [
    (1,  "MIR-01 Av. Larco",        -12.1211, -77.0283, "Miraflores",          "Av. Larco cdra. 12",                 "Valla",           "Norte",      12.0, 4.0, "Alto",  8500),
    (2,  "MIR-02 Óvalo Miraflores", -12.1180, -77.0310, "Miraflores",          "Óvalo Miraflores",                   "Pantalla Digital","Este",       6.0,  3.0, "Alto",  12000),
    (3,  "SI-01 Javier Prado",      -12.0974, -77.0356, "San Isidro",          "Av. Javier Prado Este cdra. 8",      "Valla",           "Sur",        14.0, 4.5, "Alto",  10500),
    (4,  "SI-02 Rep. Panamá",       -12.0950, -77.0420, "San Isidro",          "Av. República de Panamá cdra. 3",    "Tótem",           "Doble cara", 1.8,  4.0, "Medio", 4500),
    (5,  "SUR-01 Primavera",        -12.1188, -76.9921, "Surco",               "Av. Primavera cdra. 20",             "Valla",           "Norte",      12.0, 4.0, "Medio", 6500),
    (6,  "SUR-02 El Derby",         -12.1210, -76.9880, "Surco",               "Av. El Derby cdra. 5",               "Pantalla Digital","Oeste",      8.0,  4.0, "Alto",  11000),
    (7,  "LM-01 Av. La Molina",     -12.0740, -76.9393, "La Molina",           "Av. La Molina cdra. 15",             "Valla",           "Este",       12.0, 4.0, "Medio", 5500),
    (8,  "SB-01 Av. San Luis",      -12.1011, -77.0005, "San Borja",           "Av. San Luis cdra. 10",              "Valla",           "Norte",      14.0, 5.0, "Alto",  9000),
    (9,  "JM-01 Av. Brasil",        -12.0775, -77.0502, "Jesús María",         "Av. Brasil cdra. 28",                "Valla",           "Sur",        12.0, 4.0, "Medio", 6000),
    (10, "BAR-01 Av. Grau",         -12.1500, -77.0219, "Barranco",            "Av. Grau cdra. 7",                   "Tótem",           "Doble cara", 1.8,  4.0, "Bajo",  3000),
    (11, "CHO-01 Av. Huaylas",      -12.1693, -77.0185, "Chorrillos",          "Av. Huaylas cdra. 12",               "Valla",           "Norte",      12.0, 4.0, "Medio", 5000),
    (12, "ATE-01 Javier Prado E",   -12.0606, -76.9356, "Ate",                 "Av. Javier Prado Este cdra. 40",     "Valla",           "Sur",        14.0, 5.0, "Alto",  7500),
    (13, "LO-01 Mendiola",          -11.9845, -77.0689, "Los Olivos",          "Av. Alfredo Mendiola cdra. 18",      "Pantalla Digital","Norte",      6.0,  3.0, "Alto",  10000),
    (14, "SM-01 La Marina",         -12.0769, -77.0864, "San Miguel",          "Av. La Marina cdra. 22",             "Valla",           "Este",       12.0, 4.0, "Alto",  8000),
    (15, "LIN-01 Arequipa",         -12.0870, -77.0319, "Lince",               "Av. Arequipa cdra. 20",              "Valla",           "Oeste",      12.0, 4.0, "Alto",  7800),
    (16, "PL-01 Av. Brasil",        -12.0776, -77.0639, "Pueblo Libre",        "Av. Brasil cdra. 35",                "Tótem",           "Norte",      1.8,  4.0, "Medio", 3500),
    (17, "BRE-01 Av. Arica",        -12.0617, -77.0487, "Breña",               "Av. Arica cdra. 5",                  "Valla",           "Sur",        10.0, 3.5, "Medio", 4500),
    (18, "RIM-01 El Ejército",      -12.0320, -77.0273, "Rímac",               "Av. El Ejército cdra. 3",            "Valla",           "Este",       10.0, 3.5, "Bajo",  3200),
    (19, "CER-01 Abancay",          -12.0453, -77.0311, "Cercado de Lima",     "Av. Abancay cdra. 2",                "Pantalla Digital","Norte",      6.0,  3.0, "Alto",  9500),
    (20, "SJM-01 Benavides",        -12.1600, -76.9800, "SJM",                 "Av. Benavides cdra. 55",             "Valla",           "Sur",        12.0, 4.0, "Medio", 5200),
    (21, "VMT-01 Allende",          -12.1720, -76.9520, "Villa María del Tr.", "Av. Salvador Allende cdra. 10",      "Valla",           "Norte",      10.0, 3.5, "Bajo",  3000),
    (22, "IND-01 Túpac Amaru",      -11.9987, -77.0556, "Independencia",       "Av. Túpac Amaru cdra. 35",           "Valla",           "Oeste",      12.0, 4.0, "Medio", 4800),
    (23, "COM-01 Universitaria",    -11.9465, -77.0456, "Comas",               "Av. Universitaria cdra. 80",         "Valla",           "Norte",      10.0, 3.5, "Medio", 4200),
    (24, "SJL-01 Próceres",         -12.0821, -77.0027, "SJL",                 "Av. Próceres cdra. 20",              "Pantalla Digital","Sur",        6.0,  3.0, "Alto",  8000),
    (25, "CAL-01 Óscar Benavides",  -12.0566, -77.1184, "Callao",              "Av. Óscar R. Benavides cdra. 20",    "Valla",           "Este",       14.0, 5.0, "Alto",  8500),
]

SAMPLE_CLIENTS = [
    (1, "Coca-Cola Perú S.A.",              "20100113610", "Carlos Mendoza",  "cmendoza@cocacola.com.pe",   "+51 1 615-8200", "Bebidas"),
    (2, "Saga Falabella S.A.",              "20100090038", "Ana Torres",      "atorres@falabella.com.pe",   "+51 1 616-0000", "Retail"),
    (3, "Banco BCP",                        "20100130204", "Jorge Quispe",    "jquispe@bcp.com.pe",         "+51 1 311-9898", "Financiero"),
    (4, "Claro Perú S.A.C.",               "20514757085", "María García",    "mgarcia@claro.com.pe",       "+51 1 701-7000", "Telecomunicaciones"),
    (5, "Supermercados Peruanos (PlazaVea)","20100070970", "Roberto Silva",   "rsilva@spsa.com.pe",         "+51 1 315-2000", "Retail"),
    (6, "Interbank",                        "20100053455", "Lucía Flores",    "lflores@interbank.com.pe",   "+51 1 219-2000", "Financiero"),
    (7, "Alicorp S.A.A.",                  "20100055237", "Diego Castro",    "dcastro@alicorp.com.pe",     "+51 1 315-0800", "Alimentos"),
    (8, "Cencosud (Wong)",                  "20109072177", "Patricia Vega",   "pvega@cencosud.com.pe",      "+51 1 626-0000", "Retail"),
]

SAMPLE_CONTRACTS = [
    # OCUPADOS activos (end > hoy+30)
    (1,  1,  1, "2026-01-01", "2026-12-31", 8500,  "Verano Refrescante 2026",     "Renovación anual"),
    (2,  2,  4, "2026-02-01", "2026-07-31", 12000, "Claro Hogar Fibra",           "Campaña nacional"),
    (3,  3,  2, "2026-03-01", "2026-08-31", 10500, "Falabella Verano Collection", ""),
    (4,  5,  7, "2026-01-15", "2026-09-15", 6500,  "Aceite Primor - Nuevo!",      ""),
    (5,  6,  3, "2026-02-15", "2026-08-15", 11000, "BCP Tu Banco Digital",        ""),
    (6,  7,  5, "2026-03-01", "2026-10-31", 5500,  "Plaza Vea - Ofertón",         ""),
    (7,  8,  6, "2026-01-01", "2026-09-30", 9000,  "Interbank - Cuenta Sueldo",   ""),
    (8,  12, 1, "2026-02-01", "2026-11-30", 7500,  "Inca Kola - Orgullo Peruano", ""),
    (9,  13, 4, "2026-01-15", "2026-07-15", 10000, "Claro 5G Lima Norte",         ""),
    (10, 14, 8, "2026-02-01", "2026-09-30", 8000,  "Wong - Fresh Market",         ""),
    (11, 15, 2, "2026-03-15", "2026-12-15", 7800,  "Falabella - Cyber Days",      ""),
    (12, 19, 3, "2026-01-01", "2026-08-31", 9500,  "BCP Crédito Hipotecario",     "Centro histórico"),
    (13, 24, 6, "2026-02-15", "2026-09-15", 8000,  "Interbank - Préstamo Libre",  ""),
    (14, 25, 7, "2026-01-01", "2026-12-31", 8500,  "Alicorp - Don Vittorio",      "Puerto Callao"),
    (15, 22, 5, "2026-02-01", "2026-07-31", 4800,  "Plaza Vea - Campaña Norte",   ""),
    # POR VENCER (end entre hoy y hoy+30)
    (16, 4,  3, "2025-11-01", "2026-05-01", 4500,  "BCP - Cuenta Corriente",      "Renovación pendiente"),
    (17, 9,  1, "2025-10-15", "2026-05-10", 6000,  "Coca-Cola Zero",              "Negociar renovación"),
    (18, 10, 8, "2025-12-01", "2026-05-15", 3000,  "Wong - Semana Santa",         "Campaña estacional"),
    (19, 11, 4, "2025-11-15", "2026-05-20", 5000,  "Claro - Prepago Máximo",      ""),
    (20, 23, 2, "2025-10-01", "2026-05-22", 4200,  "Falabella - Temporada",       ""),
    # Paneles 16,17,18,20,21 → LIBRES (sin contrato activo)
]


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS paneles (
            id            INTEGER PRIMARY KEY,
            nombre        TEXT NOT NULL,
            latitud       REAL NOT NULL,
            longitud      REAL NOT NULL,
            distrito      TEXT NOT NULL,
            direccion     TEXT,
            tipo          TEXT,
            cara          TEXT,
            ancho_m       REAL,
            alto_m        REAL,
            nivel_trafico TEXT,
            precio_mensual REAL,
            activo        INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS clientes (
            id            INTEGER PRIMARY KEY,
            empresa       TEXT NOT NULL,
            ruc           TEXT,
            contacto      TEXT,
            email         TEXT,
            telefono      TEXT,
            sector        TEXT
        );

        CREATE TABLE IF NOT EXISTS contratos (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            panel_id      INTEGER NOT NULL,
            cliente_id    INTEGER NOT NULL,
            fecha_inicio  TEXT NOT NULL,
            fecha_fin     TEXT NOT NULL,
            tarifa_mensual REAL,
            nombre_campana TEXT,
            notas         TEXT,
            FOREIGN KEY (panel_id)   REFERENCES paneles(id),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        );
    """)

    # Seed data only if tables are empty
    if c.execute("SELECT COUNT(*) FROM paneles").fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO paneles VALUES (?,?,?,?,?,?,?,?,?,?,?,?,1)",
            SAMPLE_PANELS
        )
    if c.execute("SELECT COUNT(*) FROM clientes").fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO clientes VALUES (?,?,?,?,?,?,?)",
            SAMPLE_CLIENTS
        )
    if c.execute("SELECT COUNT(*) FROM contratos").fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO contratos(id,panel_id,cliente_id,fecha_inicio,fecha_fin,tarifa_mensual,nombre_campana,notas) VALUES (?,?,?,?,?,?,?,?)",
            SAMPLE_CONTRACTS
        )

    conn.commit()
    conn.close()


def get_paneles_con_estado():
    """Retorna DataFrame de paneles con su contrato activo más reciente y estado calculado."""
    conn = get_conn()
    query = """
        SELECT
            p.id, p.nombre, p.latitud, p.longitud, p.distrito, p.direccion,
            p.tipo, p.cara, p.ancho_m, p.alto_m, p.nivel_trafico, p.precio_mensual,
            c.id          AS contrato_id,
            cl.empresa    AS cliente,
            c.fecha_inicio,
            c.fecha_fin,
            c.tarifa_mensual,
            c.nombre_campana,
            c.notas
        FROM paneles p
        LEFT JOIN contratos c  ON c.panel_id = p.id
            AND c.fecha_fin = (
                SELECT MAX(c2.fecha_fin) FROM contratos c2
                WHERE c2.panel_id = p.id AND c2.fecha_fin >= date('now')
            )
        LEFT JOIN clientes cl ON cl.id = c.cliente_id
        WHERE p.activo = 1
        ORDER BY p.distrito, p.nombre
    """
    import pandas as pd
    from datetime import date, timedelta
    df = pd.read_sql_query(query, conn)
    conn.close()

    today = date.today()

    def calc_status(row):
        if not row["fecha_fin"] or str(row["fecha_fin"]) == "nan":
            return "libre"
        try:
            end = date.fromisoformat(str(row["fecha_fin"]))
            if end < today:
                return "libre"
            elif (end - today).days <= 30:
                return "por_vencer"
            else:
                return "ocupado"
        except Exception:
            return "libre"

    df["estado"] = df.apply(calc_status, axis=1)
    df["dias_restantes"] = df["fecha_fin"].apply(
        lambda f: (date.fromisoformat(str(f)) - today).days if f and str(f) != "nan" else None
    )
    return df


def get_contratos():
    conn = get_conn()
    import pandas as pd
    df = pd.read_sql_query("""
        SELECT c.id, p.nombre AS panel, p.distrito, cl.empresa AS cliente,
               c.fecha_inicio, c.fecha_fin, c.tarifa_mensual, c.nombre_campana, c.notas
        FROM contratos c
        JOIN paneles  p  ON p.id = c.panel_id
        JOIN clientes cl ON cl.id = c.cliente_id
        ORDER BY c.fecha_fin
    """, conn)
    conn.close()
    return df


def get_clientes():
    conn = get_conn()
    import pandas as pd
    df = pd.read_sql_query("SELECT * FROM clientes ORDER BY empresa", conn)
    conn.close()
    return df


def insert_panel(nombre, lat, lng, distrito, direccion, tipo, cara, ancho, alto, trafico, precio):
    conn = get_conn()
    conn.execute(
        "INSERT INTO paneles(nombre,latitud,longitud,distrito,direccion,tipo,cara,ancho_m,alto_m,nivel_trafico,precio_mensual) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        (nombre, lat, lng, distrito, direccion, tipo, cara, ancho, alto, trafico, precio)
    )
    conn.commit(); conn.close()


def insert_contrato(panel_id, cliente_id, inicio, fin, tarifa, campana, notas):
    conn = get_conn()
    conn.execute(
        "INSERT INTO contratos(panel_id,cliente_id,fecha_inicio,fecha_fin,tarifa_mensual,nombre_campana,notas) VALUES(?,?,?,?,?,?,?)",
        (panel_id, cliente_id, str(inicio), str(fin), tarifa, campana, notas)
    )
    conn.commit(); conn.close()


def insert_cliente(empresa, ruc, contacto, email, telefono, sector):
    conn = get_conn()
    conn.execute(
        "INSERT INTO clientes(empresa,ruc,contacto,email,telefono,sector) VALUES(?,?,?,?,?,?)",
        (empresa, ruc, contacto, email, telefono, sector)
    )
    conn.commit(); conn.close()
