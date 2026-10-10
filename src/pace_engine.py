"""
Motor de Dinámica de Ritmo (Pace Projection Engine) y Análisis de Escenario de Carrera.
Evalúa cómo interactuarán los estilos de carrera de todos los participantes:
- Detecta 'Lone Speed' (Puntero solitario que puede ganar de punta a punta sin oposición).
- Detecta 'Pace Duel / Meltdown' (Pelea suicida en punta que destruye a los velocistas y beneficia a los rematadores).
- Detecta 'Honest Pace' (Ritmo normal favorable a los colocados / stalkers).
"""

from typing import List, Dict, Any


def project_race_pace(contenders: List[Dict[str, Any]], distance_furlongs: float, surface: str = 'D') -> Dict[str, Any]:
    """
    Analiza a todos los inscritos en conjunto para proyectar el ritmo de los primeros 400m/800m
    y determinar quién se beneficia tácticamente de la forma de la carrera.
    """
    if not contenders:
        return {
            "scenario": "MODERATE",
            "narrative": "Información insuficiente de participantes.",
            "favored_styles": ["P"],
            "pace_pressure_score": 50.0
        }

    # Contar estilos de carrera en el lote
    # E = Early (Puntero nato que busca la delantera inmediatamente)
    # P = Presser / Stalker (Corre colocado acechando a 1-3 cuerpos)
    # S = Sustained / Closer (Rematador desde el fondo)
    styles = [c.get("pace_style", "P") for c in contenders]
    num_early = styles.count("E")
    num_pressers = styles.count("P")
    num_closers = styles.count("S")

    # Extraer los caballos punteros
    frontrunners = [c["horse_name"] for c in contenders if c.get("pace_style") == "E"]

    # Evaluar el Escenario Táctico
    if num_early == 0:
        # Nadie quiere la punta: 'Paceless race' / 'False Pace'
        # Quien tome la iniciativa caminará en parciales muy lentos
        scenario = "FALSE_PACE"
        pace_pressure = 25.0
        favored_styles = ["E", "P"]
        narrative = (
            "⚠️ RITMO FALSIFICADO / MUY LENTO: No hay velocistas puros en el lote. "
            "Se proyectan parciales extremadamente cómodos en los primeros 800 metros. "
            "Quien tome la punta o corra segundo tendrá una ventaja táctica masiva. "
            "Los rematadores de fondo (Closers) estarán fuertemente perjudicados por falta de desgaste adelante."
        )

    elif num_early == 1:
        # 'LONE SPEED' (El escenario más rentable en carreras de USA)
        lone_horse = frontrunners[0]
        scenario = "LONE_SPEED"
        pace_pressure = 35.0
        favored_styles = ["E"]
        narrative = (
            f"🚀 PUNTERO SOLITARIO (LONE SPEED): #{lone_horse} es el único velocista nato registrado. "
            "Podrá comandar la carrera sin presión temprana, dosificando energías a su gusto. "
            "En hipódromos de USA, los punteros solitarios ganan con una efectividad superior al 45%. "
            f"Fuerte bonificación táctica para #{lone_horse}."
        )

    elif num_early == 2:
        # Duelo probable de punta
        scenario = "CONTESTED_PACE"
        pace_pressure = 70.0
        favored_styles = ["P", "S"]
        narrative = (
            f"⚔️ PRESIÓN TEMPRANA: Duelo de velocidad proyectado entre {' y '.join(frontrunners)}. "
            "Ambos buscarán el liderato desde la salida, provocando fraccionales vivos. "
            "Escenario ideal para caballos de paso intermedio (Pressers) colocados a 2-3 cuerpos "
            "listos para heredar la punta al entrar a la recta."
        )

    else:
        # 3 o más punteros: 'PACE MELTDOWN' (Guerra de velocidad / Colapso en punta)
        scenario = "PACE_COLLAPSE"
        pace_pressure = 95.0
        favored_styles = ["S", "P"]
        narrative = (
            f"🔥 GUERRA DE VELOCISTAS (PACE MELTDOWN): Hay {num_early} punteros agresivos peleando la delantera "
            f"({', '.join(frontrunners)}). "
            "Se anticipa un desgaste brutal y parciales suicidas en la primera mitad de la carrera. "
            "Los punteros probablemente colapsarán en los 250 metros finales. "
            "MÁXIMA VENTAJA PARA REMATADORES (CLOSERS) con remate demoledor desde el fondo."
        )

    return {
        "scenario": scenario,
        "pace_pressure_score": pace_pressure,
        "favored_styles": favored_styles,
        "num_early": num_early,
        "num_pressers": num_pressers,
        "num_closers": num_closers,
        "frontrunners": frontrunners,
        "narrative": narrative
    }


def compute_pace_adjustment(horse_style: str, pace_scenario: str) -> float:
    """
    Calcula los puntos de bonificación o penalización (+/-) que recibe cada caballo
    según si el escenario de carrera proyectado favorece o destruye su estilo natural.
    """
    if pace_scenario == "LONE_SPEED":
        if horse_style == "E":
            return +10.0  # Gran impulso al puntero solitario
        elif horse_style == "P":
            return +2.0
        else:
            return -8.0   # Penalizar a los rematadores lejanos (no habrá tren de carrera)

    elif pace_scenario == "FALSE_PACE":
        if horse_style in ["E", "P"]:
            return +6.0
        else:
            return -7.0

    elif pace_scenario == "PACE_COLLAPSE":
        if horse_style == "S":
            return +12.0  # Gran bonificación a los rematadores
        elif horse_style == "P":
            return +4.0
        else:
            return -10.0  # Castigo severo a los velocistas que se matarán en punta

    elif pace_scenario == "CONTESTED_PACE":
        if horse_style == "P":
            return +6.0
        elif horse_style == "S":
            return +5.0
        else:
            return -4.0

    # Escenario neutral
    return 0.0
