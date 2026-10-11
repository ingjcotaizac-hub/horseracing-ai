"""
Módulo de Verificación, Liquidación y Aprendizaje Continuo (Settle & Learn).
Permite contrastar los resultados oficiales contra las predicciones guardadas,
calcular el ROI / Tasa de Acierto a Ganador (Win Only) y registrar el diagnóstico de aprendizaje.
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_db_connection


def record_race_result(
    race_id: str,
    actual_winner: str,
    actual_odds: float,
    second_place: str = "",
    third_place: str = "",
    race_notes: str = ""
):
    """
    Registra el resultado oficial de una carrera en la auditoría y calcula el acierto/ROI.
    CRITERIO ESTRICTO: El acierto es estrictamente a GANADOR (1er puesto). 
    Si el caballo recomendado no gana, es un fallo (derrota).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM predictions_audit WHERE race_id = ?", (race_id,))
    pred = cursor.fetchone()

    if not pred:
        print(f"No se encontró registro de predicción para {race_id}")
        conn.close()
        return False

    # Extraer el nombre limpio del Top Pick (ej. '#4 Lost Chord' -> 'Lost Chord')
    raw_top = pred["top_pick"]
    if " " in raw_top:
        top_pick_name = raw_top.split(" ", 1)[-1].strip()
    else:
        top_pick_name = raw_top.strip()

    winner_name = actual_winner.strip()

    # Extraer el nombre limpio de El Enemigo
    raw_enemy = pred["enemy_pick"] if "enemy_pick" in pred.keys() and pred["enemy_pick"] else ""
    enemy_name = raw_enemy.split(" ", 1)[-1].strip() if " " in raw_enemy else raw_enemy.strip()

    # Extraer el nombre limpio de la Bomba
    raw_bomb = pred["longshot_pick"] if "longshot_pick" in pred.keys() and pred["longshot_pick"] else ""
    bomb_name = raw_bomb.split(" ", 1)[-1].strip() if " " in raw_bomb else raw_bomb.strip()

    # Comprobar si acertamos el ganador de forma estricta (Top Pick Win Only)
    is_hit = 1 if (winner_name.lower() in top_pick_name.lower() or top_pick_name.lower() in winner_name.lower()) else 0

    # Comprobar si ganó El Enemigo (paridad)
    is_enemy_hit = 1 if (enemy_name and (winner_name.lower() in enemy_name.lower() or enemy_name.lower() in winner_name.lower())) else 0

    # Comprobar si la Bomba ganó o estuvo en pizarra
    is_bomb_hit = 1 if (bomb_name and (winner_name.lower() in bomb_name.lower() or bomb_name.lower() in winner_name.lower())) else 0

    # Comprobar Exacta
    is_exacta_hit = 0
    if second_place and (is_hit == 1 or is_enemy_hit == 1):
        if is_hit == 1 and enemy_name and (second_place.lower() in enemy_name.lower() or enemy_name.lower() in second_place.lower()):
            is_exacta_hit = 1
        elif is_enemy_hit == 1 and (second_place.lower() in top_pick_name.lower() or top_pick_name.lower() in second_place.lower()):
            is_exacta_hit = 1

    # Registrar pizarra solo como dato de referencia técnica
    in_the_money = 1 if (
        is_hit == 1 or 
        (second_place and top_pick_name.lower() in second_place.lower()) or 
        (third_place and top_pick_name.lower() in third_place.lower())
    ) else 0

    # Retorno financiero simulado sobre apuesta fija de $2 a Ganador (Win)
    if is_hit == 1:
        profit_loss = round(2.0 * actual_odds, 2)
    else:
        profit_loss = -2.00

    # Diagnóstico técnico de aprendizaje
    learning_notes = []
    if is_hit == 1:
        learning_notes.append(f"🏆 Acierto: Ganó el Top Pick ({top_pick_name}) a cuota {actual_odds:.1f}-1 (+${profit_loss:.2f}).")
    elif is_enemy_hit == 1:
        learning_notes.append(f"⚔️ Cobertura: Ganó El Enemigo ({enemy_name}) a cuota {actual_odds:.1f}-1 (Respaldo de alta paridad efectivo).")
    elif is_bomb_hit == 1:
        learning_notes.append(f"💣 Gran Sorpresa: Ganó la Bomba de valor ({bomb_name}) a cuota {actual_odds:.1f}-1.")
    else:
        learning_notes.append(f"❌ Fallo: El Top Pick ({top_pick_name}) no ganó. Ganador oficial: #{actual_winner} a {actual_odds:.1f}-1.")

    if is_exacta_hit == 1:
        learning_notes.append("🎯 Exacta Acertada en combinación Top Pick + Enemigo.")

    if race_notes:
        learning_notes.append(f"Análisis: {race_notes}")

    cursor.execute("""
        UPDATE predictions_audit
        SET status = 'EVALUATED',
            actual_winner = ?,
            actual_odds = ?,
            is_hit = ?,
            is_enemy_hit = ?,
            is_bomb_hit = ?,
            is_exacta_hit = ?,
            in_the_money = ?,
            profit_loss = ?,
            learning_notes = ?
        WHERE race_id = ?
    """, (
        actual_winner, actual_odds, is_hit, is_enemy_hit, is_bomb_hit, is_exacta_hit,
        in_the_money, profit_loss, " | ".join(learning_notes), race_id
    ))

    cursor.execute("""
        UPDATE races
        SET status = 'OFFICIAL'
        WHERE race_id = ?
    """, (race_id,))

    conn.commit()
    conn.close()
    print(f"Carrera {race_id} evaluada: TopHit={is_hit}, EnemyHit={is_enemy_hit}, Exacta={is_exacta_hit}, P/L=${profit_loss:+0.2f}")
    return True


def get_performance_summary() -> Dict[str, Any]:
    """Retorna las métricas globales acumuladas bajo criterio estricto de ganador (Win Only) y paridad."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM predictions_audit WHERE status = 'EVALUATED'")
    rows = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) as total_pending FROM predictions_audit WHERE status = 'PENDING'")
    pending_count = cursor.fetchone()["total_pending"]
    conn.close()

    total_evaluated = len(rows)
    if total_evaluated == 0:
        return {
            "total_evaluated": 0,
            "pending_count": pending_count,
            "wins": 0,
            "win_rate": 0.0,
            "enemy_wins": 0,
            "combined_wins": 0,
            "combined_win_rate": 0.0,
            "exacta_hits": 0,
            "losses": 0,
            "itm_rate": 0.0,
            "total_profit": 0.0,
            "roi_pct": 0.0
        }

    wins = sum(1 for r in rows if r["is_hit"] == 1)
    enemy_wins = sum(1 for r in rows if ("is_enemy_hit" in r.keys() and r["is_enemy_hit"] == 1))
    combined_wins = sum(1 for r in rows if (r["is_hit"] == 1 or ("is_enemy_hit" in r.keys() and r["is_enemy_hit"] == 1)))
    exacta_hits = sum(1 for r in rows if ("is_exacta_hit" in r.keys() and r["is_exacta_hit"] == 1))
    losses = total_evaluated - wins
    itms = sum(1 for r in rows if r["in_the_money"] == 1)
    total_pl = sum(r["profit_loss"] for r in rows)
    total_staked = total_evaluated * 2.0  # $2 apostados por carrera

    win_rate = round((wins / total_evaluated) * 100.0, 1)
    combined_win_rate = round((combined_wins / total_evaluated) * 100.0, 1)
    itm_rate = round((itms / total_evaluated) * 100.0, 1)
    roi_pct = round((total_pl / total_staked) * 100.0, 1)

    return {
        "total_evaluated": total_evaluated,
        "pending_count": pending_count,
        "wins": wins,
        "win_rate": win_rate,
        "enemy_wins": enemy_wins,
        "combined_wins": combined_wins,
        "combined_win_rate": combined_win_rate,
        "exacta_hits": exacta_hits,
        "losses": losses,
        "itms": itms,
        "itm_rate": itm_rate,
        "total_profit": round(total_pl, 2),
        "roi_pct": roi_pct
    }
