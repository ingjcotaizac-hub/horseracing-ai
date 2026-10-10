"""
Motor de Cambios de Aperos, Medicación y Sesgo de Pista (Equipment & Track Bias Engine).
Evalúa factores críticos de alta rentabilidad en hipódromos de USA:
- Gringolas / Anteojeras (Blinkers ON / OFF).
- Medicación (First Time Lasix).
- Posición de la Baranda en Grama (Rail Placement) y Sesgo de Gatera (Post Bias).
- Cambio positivo de jinete (Jockey Upgrade).
"""

from typing import Dict, Any


def evaluate_equipment_and_angles(
    equipment: str = "",
    medication: str = "",
    jockey_change: bool = False,
    is_second_start_off_layoff: bool = False,
    is_maiden: bool = False
) -> Dict[str, Any]:
    """
    Evalúa los ángulos profesionales más efectivos en carreras de EE. UU.
    """
    equipment_score = 0.0
    flags = []

    eq_upper = (equipment or "").upper()
    med_upper = (medication or "").upper()

    # 1. Gringolas Puestas (Blinkers ON) - Uno de los ángulos más fuertes en USA
    if "BLINKERS ON" in eq_upper or "B_ON" in eq_upper:
        if is_maiden or is_second_start_off_layoff:
            equipment_score += 8.0
            flags.append("🔥 BLINKERS ON (Alta efectividad en 2ª carrera / Maiden)")
        else:
            equipment_score += 5.0
            flags.append("⚡ BLINKERS ON (Mayor concentración y enfoque)")

    # 2. Gringolas Quitadas (Blinkers OFF)
    elif "BLINKERS OFF" in eq_upper or "B_OFF" in eq_upper:
        equipment_score += 3.0
        flags.append("🕊️ BLINKERS OFF (Mayor relajación para rematar)")

    # 3. Medicación: Primerizo con Lasix (First Time Lasix - FTL)
    if "FIRST" in med_upper and "LASIX" in med_upper:
        equipment_score += 6.0
        flags.append("💉 1ª VEZ CON LASIX (Previene sangrado pulmonar)")

    # 4. Cambio positivo de Jinete (Jockey Upgrade)
    if jockey_change:
        equipment_score += 4.0
        flags.append("🏇 CAMBIO POSITIVO DE JINETE (Monta de élite asignada)")

    # 5. Segunda carrera tras descanso (2nd off layoff)
    if is_second_start_off_layoff:
        equipment_score += 4.0
        flags.append("📈 2ª CARRERA TRAS DESCANSO (Forma en ascenso)")

    return {
        "equipment_score": round(equipment_score, 1),
        "flags": flags
    }


def evaluate_track_bias(
    post_position: int,
    total_field: int,
    surface: str,
    distance_furlongs: float,
    rail_feet: int = 0,
    track_condition: str = 'FT'
) -> Dict[str, Any]:
    """
    Evalúa el sesgo de la pista (Track Bias) y posición de cajón según el estado de la pista y la baranda.
    """
    bias_score = 0.0
    notes = []

    # 1. Pistas de Grama (Turf) con la baranda corrida hacia afuera (Rail out > 15-20 pies)
    # En Santa Anita, Gulfstream y Del Mar, la baranda afuera hace las curvas cerradas
    # y penaliza severamente a caballos que viajan abiertos (gateras exteriores).
    if surface.upper() == 'T':
        if rail_feet >= 15:
            if post_position <= 3:
                bias_score += 5.0
                notes.append(f"Baranda a {rail_feet} pies: Enorme ventaja pegado a la baranda interna (Gateras 1-3)")
            elif post_position >= 8:
                bias_score -= 6.0
                notes.append(f"Baranda a {rail_feet} pies: Fuerte penalización por recorrido abierto en las curvas")
        else:
            # Baranda a 0 pies (True rail): más neutral
            notes.append("Baranda a 0 pies: Condiciones justas para todos")

    # 2. Pistas de Arena rápida (Dirt FT) en sprints (<= 7f)
    elif surface.upper() == 'D' and distance_furlongs <= 7.0:
        if track_condition in ['SY', 'MY']:
            # Pista encharcada o con barro: el puntero no recibe arena en la cara
            if post_position <= 4:
                bias_score += 4.0
                notes.append("Pista encharcada: Ventaja a la velocidad interna para evitar salpicaduras")

    return {
        "bias_score": round(bias_score, 1),
        "bias_notes": notes
    }
