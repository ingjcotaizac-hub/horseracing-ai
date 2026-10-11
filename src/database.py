import sqlite3
import os
from typing import Optional

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "horseracing.db")


def get_db_connection() -> sqlite3.Connection:
    """Retorna una conexión a la base de datos SQLite."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    """Crea las tablas del esquema si no existen."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Tabla de Hipódromos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tracks (
        code TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        state TEXT NOT NULL,
        country TEXT DEFAULT 'USA'
    );
    """)

    # 2. Tabla de Carreras
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS races (
        race_id TEXT PRIMARY KEY,
        track TEXT NOT NULL,
        race_date TEXT NOT NULL,
        race_number INTEGER NOT NULL,
        distance_furlongs REAL NOT NULL,
        surface TEXT NOT NULL,         -- 'D' (Dirt), 'T' (Turf), 'A' (All-Weather)
        track_condition TEXT NOT NULL, -- 'FT' (Fast), 'SY' (Sloppy), 'FM' (Firm), 'GD' (Good)
        race_class TEXT NOT NULL,      -- 'MSW', 'CLM', 'ALW', 'STK', 'G1', 'G2', 'G3'
        purse REAL,
        rail_distance_feet REAL DEFAULT 0, -- Distancia de la baranda en grama (ej. 0, 15, 20, 30 pies)
        status TEXT DEFAULT 'SCHEDULED', -- 'SCHEDULED', 'OFFICIAL'
        FOREIGN KEY (track) REFERENCES tracks(code)
    );
    """)

    # 3. Tabla de Histórico de Resultados (Para calcular las Past Performances)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS race_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        race_id TEXT NOT NULL,
        horse_name TEXT NOT NULL,
        post_position INTEGER,
        jockey TEXT NOT NULL,
        trainer TEXT NOT NULL,
        weight_carried INTEGER,
        finish_position INTEGER,
        lengths_behind REAL,           -- 0.0 si ganó; ej. 2.5 si llegó a 2 cuerpos y medio
        final_time_sec REAL,           -- Tiempo oficial en segundos
        fractional_2f_sec REAL,        -- Tiempo primer fraccional (400m / 1/4 milla)
        fractional_4f_sec REAL,        -- Tiempo segundo fraccional (800m / 1/2 milla)
        speed_rating REAL,             -- Speed Figure casero calculado
        official_odds REAL,            -- Dividendo de cierre (ej. 3.5 = 7/2)
        FOREIGN KEY (race_id) REFERENCES races(race_id)
    );
    """)

    # 4. Tabla de Inscritos de Hoy (Entries para pronóstico)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS today_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        race_id TEXT NOT NULL,
        horse_name TEXT NOT NULL,
        post_position INTEGER NOT NULL,
        jockey TEXT NOT NULL,
        trainer TEXT NOT NULL,
        weight INTEGER NOT NULL,
        morning_line_odds REAL NOT NULL, -- Cuota inicial (ej. 2.0 = 2/1, 5.0 = 5/1)
        equipment TEXT DEFAULT '',       -- 'Blinkers ON', 'Blinkers OFF', etc.
        medication TEXT DEFAULT '',      -- 'Lasix', 'First Time Lasix', etc.
        jockey_change INTEGER DEFAULT 0, -- 1 si hubo cambio positivo de jinete
        workouts_json TEXT DEFAULT '[]', -- Historial de aprontes matutinos en JSON
        FOREIGN KEY (race_id) REFERENCES races(race_id)
    );
    """)

    # 5. Tabla de Auditoría y Aprendizaje Continuo de Predicciones
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        race_id TEXT UNIQUE NOT NULL,
        track TEXT NOT NULL,
        race_date TEXT NOT NULL,
        race_number INTEGER NOT NULL,
        distance_furlongs REAL NOT NULL,
        surface TEXT NOT NULL,
        race_class TEXT,
        top_pick TEXT NOT NULL,
        top_pick_odds REAL,
        top_pick_score REAL,
        value_pick TEXT,
        value_pick_odds REAL,
        longshot_pick TEXT,
        pace_scenario TEXT,
        pace_pressure REAL,
        exacta_box TEXT,
        created_at TEXT NOT NULL,
        status TEXT DEFAULT 'PENDING',  -- 'PENDING', 'EVALUATED'
        actual_winner TEXT,
        actual_odds REAL,
        is_hit INTEGER,                 -- 1 si ganó el Top Pick, 0 si no
        in_the_money INTEGER,           -- 1 si llegó 1º, 2º o 3º
        profit_loss REAL,               -- Retorno neto sobre apuesta de $2 Win
        learning_notes TEXT
    );
    """)

    # Migraciones seguras para bases de datos existentes
    try:
        cursor.execute("ALTER TABLE races ADD COLUMN rail_distance_feet REAL DEFAULT 0;")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE today_entries ADD COLUMN equipment TEXT DEFAULT '';")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE today_entries ADD COLUMN medication TEXT DEFAULT '';")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE today_entries ADD COLUMN jockey_change INTEGER DEFAULT 0;")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE today_entries ADD COLUMN workouts_json TEXT DEFAULT '[]';")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE today_entries ADD COLUMN is_scratched INTEGER DEFAULT 0;")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE predictions_audit ADD COLUMN enemy_pick TEXT DEFAULT '';")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE predictions_audit ADD COLUMN enemy_odds REAL DEFAULT NULL;")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE predictions_audit ADD COLUMN parity_level TEXT DEFAULT 'STANDOUT';")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE predictions_audit ADD COLUMN parity_reason TEXT DEFAULT '';")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE predictions_audit ADD COLUMN scratch_status TEXT DEFAULT 'ACTIVE';")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE predictions_audit ADD COLUMN is_enemy_hit INTEGER DEFAULT 0;")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE predictions_audit ADD COLUMN is_bomb_hit INTEGER DEFAULT 0;")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE predictions_audit ADD COLUMN is_exacta_hit INTEGER DEFAULT 0;")
    except Exception:
        pass

    # Índices para consultas ultrarrápidas de historial
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_horse_name ON race_results(horse_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_race_date ON races(race_date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_entries_race ON today_entries(race_id);")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_entries_unique ON today_entries(race_id, horse_name);")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_database()
    print(f"Base de datos inicializada en: {DB_PATH}")
