import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_db_connection, init_database
from src.speed_figures import calculate_speed_rating, calculate_pace_ratings


def seed_data():
    init_database()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Limpiar tablas existentes para empezar limpios
    cursor.execute("DELETE FROM today_entries;")
    cursor.execute("DELETE FROM race_results;")
    cursor.execute("DELETE FROM races;")
    cursor.execute("DELETE FROM tracks;")

    # 1. Insertar Hipódromos
    tracks = [
        ("GP", "Gulfstream Park", "FL", "USA"),
        ("SAR", "Saratoga", "NY", "USA"),
        ("CD", "Churchill Downs", "KY", "USA"),
        ("BEL", "Belmont Park", "NY", "USA"),
        ("DMR", "Del Mar", "CA", "USA")
    ]
    cursor.executemany("INSERT INTO tracks (code, name, state, country) VALUES (?, ?, ?, ?)", tracks)

    # 2. Insertar Carreras Históricas (Últimos meses para crear el historial de los caballos)
    historical_races = [
        # (race_id, track, date, race_num, distance, surface, condition, class, purse, status)
        ("GP_20260715_R05", "GP", "2026-07-15", 5, 6.0, "D", "FT", "MSW", 60000, "OFFICIAL"),
        ("GP_20260810_R07", "GP", "2026-08-10", 7, 6.5, "D", "FT", "ALW", 75000, "OFFICIAL"),
        ("GP_20260905_R06", "GP", "2026-09-05", 6, 7.0, "D", "FT", "OCL", 85000, "OFFICIAL"),
        ("SAR_20260801_R09", "SAR", "2026-08-01", 9, 7.0, "D", "FT", "G2", 250000, "OFFICIAL"),
        ("SAR_20260829_R08", "SAR", "2026-08-29", 8, 7.0, "D", "SY", "G1", 500000, "OFFICIAL"),
        ("CD_20260620_R08", "CD", "2026-06-20", 8, 6.5, "D", "FT", "ALW", 90000, "OFFICIAL"),
        ("GP_20260822_R04", "GP", "2026-08-22", 4, 7.5, "T", "FM", "ALW", 70000, "OFFICIAL"),
        ("GP_20260918_R08", "GP", "2026-09-18", 8, 7.0, "D", "FT", "ALW", 80000, "OFFICIAL"),
    ]
    cursor.executemany("""
        INSERT INTO races (race_id, track, race_date, race_number, distance_furlongs, surface, track_condition, race_class, purse, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, historical_races)

    # 3. Insertar Histórico de Resultados de los Caballos (Past Performances previas)
    # Lista de resultados: (race_id, horse, post, jockey, trainer, weight, finish, margin, final_time, frac2, frac4, odds)
    past_results = [
        # --- Caballo: "Speedy Lightning" (Puntero veloz de élite) ---
        ("GP_20260715_R05", "Speedy Lightning", 2, "Irad Ortiz Jr.", "Todd Pletcher", 118, 1, 0.0, 69.80, 22.10, 44.90, 1.8),
        ("GP_20260810_R07", "Speedy Lightning", 3, "Irad Ortiz Jr.", "Todd Pletcher", 121, 1, 0.0, 75.90, 22.30, 45.10, 2.1),
        ("SAR_20260829_R08", "Speedy Lightning", 1, "Irad Ortiz Jr.", "Todd Pletcher", 122, 2, 1.5, 83.10, 22.40, 45.30, 3.2),

        # --- Caballo: "Midnight Thunder" (Rematador con gran remate final) ---
        ("CD_20260620_R08", "Midnight Thunder", 5, "Tyler Gaffalione", "Chad Brown", 120, 3, 2.0, 76.50, 23.20, 46.50, 4.5),
        ("SAR_20260801_R09", "Midnight Thunder", 6, "Flavien Prat", "Chad Brown", 121, 2, 0.75, 82.80, 23.00, 46.10, 5.0),
        ("GP_20260918_R08", "Midnight Thunder", 4, "Tyler Gaffalione", "Chad Brown", 122, 1, 0.0, 82.20, 22.90, 45.80, 2.8),

        # --- Caballo: "Golden Empire" (Caballo consistente de clase media) ---
        ("GP_20260715_R05", "Golden Empire", 4, "Luis Saez", "Bill Mott", 118, 2, 2.5, 70.30, 22.40, 45.50, 5.2),
        ("GP_20260810_R07", "Golden Empire", 5, "Luis Saez", "Bill Mott", 120, 3, 3.0, 76.50, 22.60, 45.80, 6.1),
        ("GP_20260905_R06", "Golden Empire", 2, "Luis Saez", "Bill Mott", 120, 2, 1.0, 83.20, 22.50, 45.40, 4.8),

        # --- Caballo: "Iron Heart" (Caballo con altibajos, viene de descanso) ---
        ("CD_20260620_R08", "Iron Heart", 2, "Edgard Zayas", "Saffie Joseph Jr.", 118, 1, 0.0, 76.10, 22.50, 45.20, 3.8),
        ("GP_20260715_R05", "Iron Heart", 7, "Edgard Zayas", "Saffie Joseph Jr.", 121, 4, 5.0, 70.80, 22.60, 45.90, 4.0),

        # --- Caballo: "Storm Runner" (Buen rendimiento en grama, pasa a arena) ---
        ("GP_20260822_R04", "Storm Runner", 1, "Jose Ortiz", "Christophe Clement", 120, 1, 0.0, 89.20, 23.50, 47.10, 2.4),
        ("GP_20260918_R08", "Storm Runner", 2, "Jose Ortiz", "Christophe Clement", 121, 4, 4.5, 83.00, 23.00, 46.20, 7.5),

        # --- Caballo: "Silver Bullet" (Modesto, cuotas altas) ---
        ("GP_20260715_R05", "Silver Bullet", 1, "Paco Lopez", "Michael Yates", 118, 5, 8.0, 71.40, 22.70, 46.30, 15.0),
        ("GP_20260810_R07", "Silver Bullet", 2, "Paco Lopez", "Michael Yates", 119, 4, 6.0, 77.10, 22.80, 46.50, 18.0),
        ("GP_20260905_R06", "Silver Bullet", 6, "Paco Lopez", "Michael Yates", 120, 5, 7.0, 84.40, 23.10, 46.90, 22.0),
    ]

    for item in past_results:
        race_id, horse, post, jockey, trainer, weight, finish, margin, final_t, f2, f4, odds = item
        # Buscar distancia y superficie de esa carrera para calcular el speed rating casero exacto
        cursor.execute("SELECT distance_furlongs, surface, track_condition FROM races WHERE race_id = ?", (race_id,))
        r_info = cursor.fetchone()
        speed = calculate_speed_rating(
            final_time_sec=final_t,
            distance_furlongs=r_info["distance_furlongs"],
            surface=r_info["surface"],
            track_condition=r_info["track_condition"],
            lengths_behind=margin,
            weight_carried=weight
        )
        cursor.execute("""
            INSERT INTO race_results (
                race_id, horse_name, post_position, jockey, trainer, weight_carried,
                finish_position, lengths_behind, final_time_sec, fractional_2f_sec,
                fractional_4f_sec, speed_rating, official_odds
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (race_id, horse, post, jockey, trainer, weight, finish, margin, final_t, f2, f4, speed, odds))

    # 4. Insertar LA CARRERA DE HOY (La que vamos a pronosticar y generar PP)
    # Gulfstream Park, Carrera 8 de hoy: 7 Furlongs en Arena (Dirt), Bolsa $95,000
    today_race_id = "GP_20261010_R08"
    cursor.execute("""
        INSERT INTO races (race_id, track, race_date, race_number, distance_furlongs, surface, track_condition, race_class, purse, status)
        VALUES (?, 'GP', '2026-10-10', 8, 7.0, 'D', 'FT', 'AOC - Allowance Optional Claiming', 95000, 'SCHEDULED')
    """, (today_race_id,))

    # 5. Insertar Inscritos de Hoy (Entries con Morning Line Odds oficial)
    entries_today = [
        # (race_id, horse_name, post_position, jockey, trainer, weight, morning_line_odds)
        (today_race_id, "Speedy Lightning", 1, "Irad Ortiz Jr.", "Todd Pletcher", 122, 2.5),
        (today_race_id, "Midnight Thunder", 2, "Tyler Gaffalione", "Chad Brown", 122, 3.5),
        (today_race_id, "Golden Empire", 3, "Luis Saez", "Bill Mott", 120, 5.0),
        (today_race_id, "Iron Heart", 4, "Edgard Zayas", "Saffie Joseph Jr.", 118, 6.0),
        (today_race_id, "Storm Runner", 5, "Jose Ortiz", "Christophe Clement", 120, 8.0),
        (today_race_id, "Silver Bullet", 6, "Paco Lopez", "Michael Yates", 118, 20.0),
    ]

    cursor.executemany("""
        INSERT INTO today_entries (race_id, horse_name, post_position, jockey, trainer, weight, morning_line_odds)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, entries_today)

    conn.commit()
    conn.close()
    print("Base de datos poblada exitosamente con datos históricos y carrera de hoy.")


if __name__ == "__main__":
    seed_data()
