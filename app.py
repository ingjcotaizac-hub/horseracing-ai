"""
Dashboard Web Interactivo en Streamlit para Pronósticos de Carreras USA.
Past Performances Propias, Dinámica de Ritmo (Pace), Aprontes (Workouts), Aperos y Detección de Valor (+EV).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Configurar ruta del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import get_db_connection, init_database
from src.features import analyze_race_field, get_horse_past_performances
from src.ingest_live import ingest_weekend_cards
from src.load_today_race import load_october_9_race
from src.load_race_5 import load_race_5

# 1. Configuración de Página
st.set_page_config(
    page_title="Horseracing AI - USA Predictor",
    page_icon="🏇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .metric-card {
        background-color: #1E293B;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #334155;
        text-align: center;
        color: white;
    }
    .top-pick-badge {
        background-color: #10B981;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: bold;
    }
    .value-badge {
        background-color: #3B82F6;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: bold;
    }
    .longshot-badge {
        background-color: #8B5CF6;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: bold;
    }
    .pace-banner {
        background-color: #0F172A;
        border-left: 5px solid #F59E0B;
        padding: 14px;
        border-radius: 6px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 2. Inicializar BD
init_database()


def get_available_races():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.race_id, r.race_date, r.race_number, r.distance_furlongs, r.surface, 
               r.race_class, r.purse, r.track_condition, r.rail_distance_feet, 
               t.name as track_name, t.code as track_code
        FROM races r
        JOIN tracks t ON r.track = t.code
        WHERE r.status = 'SCHEDULED'
        ORDER BY r.race_date DESC, r.track ASC, r.race_number ASC
    """)
    races = cursor.fetchall()
    conn.close()
    return [dict(r) for r in races]


# 3. Sidebar (Controles e Ingesta)
with st.sidebar:
    st.title("🏇 Horseracing AI")
    st.markdown("**Plataforma de Pronósticos USA (Nivel Profesional)**")
    st.markdown("---")

    # Acciones de carga
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔄 Carreras Hoy (09 Oct)", use_container_width=True):
            load_october_9_race()
            load_race_5()
            st.success("¡Carreras del 09 de Octubre cargadas!")
            st.rerun()
    with col_btn2:
        if st.button("📅 Fin de Semana", use_container_width=True):
            ingest_weekend_cards()
            st.success("¡Fin de semana cargado!")
            st.rerun()

    available_races = get_available_races()

    if not available_races:
        st.warning("No hay carreras programadas. Haz clic arriba para cargar.")
        st.stop()

    race_options = {
        f"{r['track_name']} - Carr. #{r['race_number']} ({r['race_date']})": r["race_id"]
        for r in available_races
    }

    selected_label = st.selectbox("Selecciona Hipódromo y Carrera:", list(race_options.keys()))
    selected_race_id = race_options[selected_label]

    curr_race = next(r for r in available_races if r["race_id"] == selected_race_id)

    st.markdown("---")
    st.markdown("### ℹ️ Condiciones de Pista")
    st.write(f"**Hipódromo:** {curr_race['track_name']} ({curr_race['track_code']})")
    st.write(f"**Fecha:** {curr_race['race_date']}")
    st.write(f"**Distancia:** {curr_race['distance_furlongs']} Furlongs (~{int(curr_race['distance_furlongs']*201.16)} m)")
    surface_map = {"D": "Arena (Dirt)", "T": "Grama (Turf)", "A": "Tapeta / Sintética"}
    st.write(f"**Superficie:** {surface_map.get(curr_race['surface'], curr_race['surface'])}")
    st.write(f"**Pista:** {curr_race['track_condition']}")
    rail_f = curr_race.get('rail_distance_feet', 0)
    if curr_race['surface'] == 'T':
        st.write(f"**Baranda (Rail):** {rail_f} pies")
    st.write(f"**Bolsa (Purse):** ${curr_race['purse']:,.0f}" if curr_race['purse'] else "N/A")


# 4. Procesar la Carrera con el Motor Avanzado (analyze_race_field)
analysis = analyze_race_field(selected_race_id)

if not analysis:
    st.error("Error al procesar el análisis de la carrera.")
    st.stop()

race_info = analysis["race"]
pace = analysis["pace_analysis"]
profiles = analysis["profiles"]
ranked = analysis["ranked_profiles"]
top_pick = analysis["top_pick"]
value_pick = analysis["value_pick"]
longshot_pick = analysis["longshot_pick"]


# 5. Encabezado Principal y Diagnóstico Táctico de Ritmo
st.title(f"{curr_race['track_name']} — Carrera #{curr_race['race_number']}")
st.caption(f"**Clase:** {curr_race['race_class']} | **Distancia:** {curr_race['distance_furlongs']} Furlongs | **Superficie:** {surface_map.get(curr_race['surface'], curr_race['surface'])} ({curr_race['track_condition']})")

# BANNER DE RITMO Y DINÁMICA DE CARRERA
scenario_colors = {
    "LONE_SPEED": "🚀 ESCENARIO: PUNTERO SOLITARIO (LONE SPEED)",
    "PACE_COLLAPSE": "🔥 ESCENARIO: GUERRA EN PUNTA (PACE MELTDOWN)",
    "CONTESTED_PACE": "⚔️ ESCENARIO: RITMO EXIGENTE / DISPUTADO",
    "FALSE_PACE": "⚠️ ESCENARIO: RITMO MUY LENTO / FALSIFICADO"
}
scenario_title = scenario_colors.get(pace["scenario"], "⚖️ ESCENARIO: RITMO MODERADO")

st.markdown(f"""
<div class="pace-banner">
    <h4 style="margin: 0 0 8px 0; color: #F59E0B;">{scenario_title}</h4>
    <p style="margin: 0; font-size: 15px; color: #E2E8F0;">{pace['narrative']}</p>
    <div style="margin-top: 10px; font-size: 13px; color: #94A3B8;">
        <b>Presión de Ritmo Temprano:</b> {pace['pace_pressure_score']}/100 &nbsp;|&nbsp;
        <b>Velocistas (E):</b> {pace['num_early']} &nbsp;|&nbsp;
        <b>Colocados (P):</b> {pace['num_pressers']} &nbsp;|&nbsp;
        <b>Rematadores (S):</b> {pace['num_closers']}
    </div>
</div>
""", unsafe_allow_html=True)

# TARJETAS DE SELECCIÓN
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <span class="top-pick-badge">⭐ TOP PICK</span>
        <h3 style="margin: 8px 0;">#{top_pick['post_position']} {top_pick['horse_name']}</h3>
        <p style="margin: 0; color: #94A3B8;">Índice: <b>{top_pick['composite_score']}</b> | Cuota: <b>{top_pick['morning_line_odds']}-1</b></p>
        <small style="color: #6EE7B7;">Estilo: {top_pick['pace_style']} (Ajuste: {top_pick.get('pace_adjustment', 0):+0.1f} pts)</small>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if value_pick:
        st.markdown(f"""
        <div class="metric-card">
            <span class="value-badge">🔥 VALOR (+EV)</span>
            <h3 style="margin: 8px 0;">#{value_pick['post_position']} {value_pick['horse_name']}</h3>
            <p style="margin: 0; color: #94A3B8;">Índice: <b>{value_pick['composite_score']}</b> | Cuota: <b>{value_pick['morning_line_odds']}-1</b></p>
            <small style="color: #93C5FD;">Estilo: {value_pick['pace_style']} (Ajuste: {value_pick.get('pace_adjustment', 0):+0.1f} pts)</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""<div class="metric-card"><span class="value-badge">VALOR</span><p style="margin-top:12px;">Sin divergencia notable</p></div>""", unsafe_allow_html=True)

with col3:
    if longshot_pick:
        st.markdown(f"""
        <div class="metric-card">
            <span class="longshot-badge">💣 SORPRESA</span>
            <h3 style="margin: 8px 0;">#{longshot_pick['post_position']} {longshot_pick['horse_name']}</h3>
            <p style="margin: 0; color: #94A3B8;">Índice: <b>{longshot_pick['composite_score']}</b> | Cuota: <b>{longshot_pick['morning_line_odds']}-1</b></p>
            <small style="color: #C4B5FD;">Estilo: {longshot_pick['pace_style']}</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""<div class="metric-card"><span class="longshot-badge">SORPRESA</span><p style="margin-top:12px;">Cuadro compacto</p></div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <span style="background-color:#475569; color:white; padding:4px 8px; border-radius:4px; font-weight:bold;">PAR TIME</span>
        <h3 style="margin: 8px 0;">{curr_race['distance_furlongs']} Furlongs</h3>
        <p style="margin: 0; color: #94A3B8;">Pista: <b>{curr_race['track_condition']}</b> | <b>{len(profiles)} Contendientes</b></p>
        <small style="color: #CBD5E1;">Baranda: {curr_race.get('rail_distance_feet', 0)} ft</small>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 6. Tabla Multidimensional de Contendientes
st.subheader("📋 Tabla General de Contendientes (Factores Completos)")

table_data = []
for p in ranked:
    if p["horse_name"] == top_pick["horse_name"]:
        verd = "⭐ TOP PICK"
    elif value_pick and p["horse_name"] == value_pick["horse_name"]:
        verd = "🔥 VALOR +EV"
    elif longshot_pick and p["horse_name"] == longshot_pick["horse_name"]:
        verd = "💣 LONGSHOT"
    elif p["composite_score"] >= (top_pick["composite_score"] - 5.0):
        verd = "CONTENDER"
    else:
        verd = "OUTSIDER"

    # Badges de aprontes
    work_badge = "🎯 BULLET" if p.get("has_bullet_workout") else f"{p.get('workout_score', 60):.0f} pts"

    # Aperos
    eq_str = ", ".join(p.get("equipment_flags", [])) if p.get("equipment_flags") else "Estándar"

    table_data.append({
        "PP": p["post_position"],
        "Ejemplar": p["horse_name"],
        "ML": f"{p['morning_line_odds']:.1f}-1",
        "Índice Final": p["composite_score"],
        "Pace": p["pace_style"],
        "Ajuste Ritmo": f"{p.get('pace_adjustment', 0):+0.1f}",
        "Speed Última": p["last_speed"],
        "Speed Ponderada": p["weighted_speed"],
        "Aprontes": work_badge,
        "Descanso": f"{p['layoff_days']} d",
        "Jockey": f"{p['jockey']} ({p['jockey_win_pct']}%)",
        "Trainer": f"{p['trainer']} ({p['trainer_win_pct']}%)",
        "Ángulos / Aperos": eq_str,
        "Veredicto": verd
    })

df = pd.DataFrame(table_data)
st.dataframe(
    df,
    column_config={
        "Índice Final": st.column_config.ProgressColumn(
            "Índice Final",
            format="%.1f",
            min_value=30,
            max_value=110,
        ),
    },
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# 7. Gráficos Interactivos y Pestañas Analíticas
st.subheader("📊 Análisis Táctico y Estrategia de Apuestas")

tab1, tab2, tab3, tab4 = st.tabs([
    "⚡ Comparativa de Velocidad", 
    "⚔️ Simulador de Ritmo (Pace Battle)", 
    "🎯 Boletos y Estrategia Sugerida",
    "🏇 Auditoría de Resultados de Ayer"
])

with tab1:
    fig_speed = go.Figure()
    fig_speed.add_trace(go.Bar(
        x=[p["horse_name"] for p in ranked],
        y=[p["weighted_speed"] for p in ranked],
        name="Speed Ponderada",
        marker_color="#3B82F6"
    ))
    fig_speed.add_trace(go.Bar(
        x=[p["horse_name"] for p in ranked],
        y=[p["best_speed"] for p in ranked],
        name="Mejor Speed Histórica",
        marker_color="#10B981"
    ))
    fig_speed.update_layout(
        title="Speed Figures Propios (Normalizados por Distancia)",
        barmode='group',
        yaxis_title="Puntos de Velocidad",
        xaxis_title="Ejemplar",
        template="plotly_dark",
        height=380
    )
    st.plotly_chart(fig_speed, use_container_width=True)

with tab2:
    # Scatter plot: Estilo vs Ajuste de Ritmo
    style_nums = {"E": 1, "P": 2, "S": 3}
    fig_pace = px.scatter(
        x=[p["horse_name"] for p in ranked],
        y=[p.get("pace_adjustment", 0) for p in ranked],
        color=[p["pace_style"] for p in ranked],
        size=[p["composite_score"] for p in ranked],
        labels={"x": "Ejemplar", "y": "Ajuste por Ritmo de Carrera (+/- Puntos)", "color": "Estilo"},
        title=f"Impacto del Escenario de Ritmo ({pace['scenario']}) en cada Participante",
        template="plotly_dark",
        height=380
    )
    fig_pace.add_hline(y=0, line_dash="dash", line_color="gray")
    st.plotly_chart(fig_pace, use_container_width=True)
    st.caption("Los puntos por encima de 0 reciben ventaja táctica del ritmo proyectado; los puntos por debajo se ven perjudicados por el desgaste temprano.")

with tab3:
    st.markdown("#### 🎫 Jugadas Recomendadas por el Modelo")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.info(f"""
        **Directas (Win / Place):**
        * **1ª Opción (A Ganar):** #{top_pick['post_position']} **{top_pick['horse_name']}** (Índice {top_pick['composite_score']})
        {f"* **Apuesta de Valor (+EV):** #{value_pick['post_position']} **{value_pick['horse_name']}** (Cuota {value_pick['morning_line_odds']}-1)" if value_pick else ""}
        """)
    with col_t2:
        top_3_names = [f"#{p['post_position']} {p['horse_name']}" for p in ranked[:3]]
        st.success(f"""
        **Jugadas Combinadas (Exóticas):**
        * **Exacta Box (Top 2-3):** Combinar {", ".join(top_3_names[:2])}
        * **Trifecta Clave:** Clave #{top_pick['post_position']} en 1º puesto con {", ".join(top_3_names[1:])} en 2º y 3º.
        """)

with tab4:
    st.markdown("#### 🔍 Auditoría de las Carreras de Ayer (09 de Octubre):")
    st.markdown("""
    * **Carrera #8 de Santa Anita (6.5f Arena):**
      * **Pronóstico del Modelo:** ⭐ **TOP PICK: #1 Fractious** (Joel Rosario / Doug O'Neill).
      * **Resultado Oficial:** **¡FRACTIOUS GANÓ LA CARRERA (1º Lugar)!** 🏆.
      * **Peligro detectado:** El modelo marcó a *#8 Magic Wave* como vulnerable por gatera y conexiones; terminó 7º.
    
    * **Carrera #5 de Santa Anita (1 Milla Grama):**
      * **Resultado Oficial:** Ganó **Little Hidden Port (ARG)** montada por **Joel Rosario** y entrenada por **John W. Sadler**.
      * **Lección cuantitativa aprendida:** En carreras de grama con baranda adentro, la yunta *John Sadler + Joel Rosario* y el sesgo de pista interna fueron determinantes.
    """)

st.markdown("---")

# 8. Desglose Detallado Carrera por Carrera (Past Performances)
st.subheader("📑 Fichas de Past Performance y Aprontes Matutinos")

for p in profiles:
    pps = p["past_performances"]
    bullet_label = "🎯 [BULLET WORKOUT]" if p.get("has_bullet_workout") else ""
    with st.expander(f"#{p['post_position']} **{p['horse_name']}** | Pace: {p['pace_style']} | Rating: {p['composite_score']} {bullet_label}"):
        st.markdown(f"**Último Ejercicio Registrado:** {p.get('last_workout', 'N/A')} | **Estado:** {p.get('workout_verdict', 'Normal')}")
        if p.get("equipment_flags"):
            st.markdown(f"**Aperos & Ángulos:** {', '.join(p['equipment_flags'])}")
        
        if not pps:
            st.write("Sin carreras previas registradas (Debutante).")
        else:
            pp_rows = []
            for r in pps:
                margin = "Ganó" if r["finish_position"] == 1 else f"+{r['lengths_behind']} cpos"
                pp_rows.append({
                    "Fecha": r["race_date"],
                    "Hipódromo": r["track"],
                    "Distancia / Superficie": f"{r['distance_furlongs']}f {r['surface']}",
                    "Condición": r["track_condition"],
                    "Clase": r["race_class"],
                    "Llegó": f"{r['finish_position']}º",
                    "Margen": margin,
                    "Tiempo Oficial": f"{r['final_time_sec']:.2f}s" if r.get("final_time_sec") else "N/A",
                    "Speed Figure": r["speed_rating"],
                    "Jinete": r["jockey"],
                    "Cuota Pagada": f"{r['official_odds']} - 1"
                })
            st.dataframe(pd.DataFrame(pp_rows), hide_index=True, use_container_width=True)
