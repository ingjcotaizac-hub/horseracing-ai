"""
Dashboard Web Interactivo en Streamlit para Pronósticos de Carreras USA.
Past Performances Propias, Dinámica de Ritmo, Auditoría de Predicciones y Aprendizaje Continuo.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
import json

# Configurar ruta del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import get_db_connection, init_database
from src.features import analyze_race_field, get_horse_past_performances
from src.predict_today import populate_and_predict_today
from src.settle_and_learn import get_performance_summary, record_race_result

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


def get_race_entries(race_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM today_entries WHERE race_id = ? ORDER BY post_position ASC", (race_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# 3. Sidebar (Navegación e Ingesta)
with st.sidebar:
    st.title("🏇 Horseracing AI")
    st.markdown("**Plataforma de Pronósticos USA**")
    st.markdown("---")

    nav_mode = st.radio(
        "Modo de Visualización:",
        [
            "🏇 Análisis y Pronóstico en Vivo",
            "📑 Gaceta de Past Performances (DRF)",
            "📊 Auditoría y Aprendizaje Continuo"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("### 🔄 Actualizar Carreras")

    if st.button("🚀 Sincronizar Clase A de Hoy", use_container_width=True):
        with st.spinner("Descargando y analizando cartelera completa de hoy (39 carreras)..."):
            res = populate_and_predict_today()
            st.success(f"¡{len(res)} carreras analizadas y guardadas para auditoría!")
            st.rerun()

    available_races = get_available_races()

    if nav_mode in ["🏇 Análisis y Pronóstico en Vivo", "📑 Gaceta de Past Performances (DRF)"]:
        if not available_races:
            st.warning("No hay carreras programadas. Pulsa arriba para sincronizar.")
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
        if curr_race['surface'] == 'T':
            st.write(f"**Baranda (Rail):** {curr_race.get('rail_distance_feet', 0)} ft")
        st.write(f"**Bolsa (Purse):** ${curr_race['purse']:,.0f}" if curr_race['purse'] else "N/A")


# =========================================================================
# VISTA 1: AUDITORÍA Y APRENDIZAJE CONTINUO
# =========================================================================
if nav_mode == "📊 Auditoría y Aprendizaje Continuo":
    st.title("📊 Panel de Auditoría y Aprendizaje Continuo")
    st.caption("Registro inmutable de todas las predicciones emitidas, métricas de acierto y retroalimentación iterativa.")

    # 1. Métricas Globales Acumuladas
    summary = get_performance_summary()
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    with kpi1:
        st.metric("Carreras Evaluadas", summary["total_evaluated"])
    with kpi2:
        st.metric("Acierto a Ganador (Win %)", f"{summary['win_rate']}%")
    with kpi3:
        st.metric("Top 3 en Pizarra (ITM %)", f"{summary['itm_rate']}%")
    with kpi4:
        st.metric("Retorno Financiero (ROI)", f"{summary['roi_pct']:+.1f}%")
    with kpi5:
        st.metric("Carreras Pendientes Hoy", summary["pending_count"], delta_color="normal")

    st.markdown("---")

    # 2. Pestañas de Gestión
    tab_pending, tab_history, tab_settle = st.tabs([
        "⏳ Predicciones de Hoy (En Espera de Resultados)",
        "✅ Historial Auditado y Diagnóstico",
        "📝 Liquidar Carrera Oficialmente (Para Mañana)"
    ])

    conn = get_db_connection()
    cursor = conn.cursor()

    with tab_pending:
        st.subheader("📋 Predicciones Oficiales Emitidas para Hoy (Sábado 10 de Octubre)")
        cursor.execute("SELECT * FROM predictions_audit WHERE status = 'PENDING' ORDER BY race_date DESC, track ASC, race_number ASC")
        pending_rows = [dict(r) for r in cursor.fetchall()]

        if not pending_rows:
            st.info("No hay predicciones pendientes. Haz clic en 'Sincronizar Clase A de Hoy' en la barra lateral.")
        else:
            filter_track = st.selectbox(
                "Filtrar por Hipódromo:",
                ["Todos los Hipódromos", "Keeneland (KEE)", "Gulfstream Park (GP)", "Santa Anita Park (SA)", "Belmont at the Big A (BAQ)"]
            )
            track_prefix_map = {
                "Keeneland (KEE)": "KEE",
                "Gulfstream Park (GP)": "GP",
                "Santa Anita Park (SA)": "SA",
                "Belmont at the Big A (BAQ)": "BAQ"
            }
            if filter_track in track_prefix_map:
                pending_rows = [r for r in pending_rows if r["track"] == track_prefix_map[filter_track]]

            st.caption(f"Mostrando **{len(pending_rows)}** carreras en espera de resultados oficiales.")
            p_data = []
            for r in pending_rows:
                p_data.append({
                    "Hipódromo": r["track"],
                    "Fecha": r["race_date"],
                    "Carrera #": r["race_number"],
                    "Clase": r["race_class"],
                    "Dist / Sup": f"{r['distance_furlongs']}f {r['surface']}",
                    "⭐ Top Pick (A Ganar)": f"{r['top_pick']} ({r['top_pick_odds']:.1f}-1)",
                    "🔥 Apuesta de Valor (+EV)": f"{r['value_pick']} ({r['value_pick_odds']:.1f}-1)" if r.get("value_pick_odds") else r["value_pick"],
                    "Ritmo Proyectado": r["pace_scenario"],
                    "Exacta Box Sugerida": r["exacta_box"],
                    "Registrado el": r["created_at"]
                })
            st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)

    with tab_history:
        st.subheader("🏁 Historial de Carreras Evaluadas y Lecciones Aprendidas")
        cursor.execute("SELECT * FROM predictions_audit WHERE status = 'EVALUATED' ORDER BY race_date DESC, race_number DESC")
        history_rows = [dict(r) for r in cursor.fetchall()]

        if not history_rows:
            st.info("Aún no hay carreras evaluadas.")
        else:
            h_data = []
            for r in history_rows:
                res_badge = "🏆 ACIERTO GANADOR" if r["is_hit"] == 1 else ("🥈 TOP 3 (ITM)" if r["in_the_money"] == 1 else "❌ NO ACERTADO")
                h_data.append({
                    "Carrera": f"{r['track']} R{r['race_number']} ({r['race_date']})",
                    "Top Pick Elegido": r["top_pick"],
                    "Ganador Real": f"{r['actual_winner']} ({r['actual_odds']:.1f}-1)",
                    "Resultado": res_badge,
                    "Retorno ($2 Win)": f"${r['profit_loss']:+.2f}",
                    "Diagnóstico y Aprendizaje": r["learning_notes"]
                })
            st.dataframe(pd.DataFrame(h_data), use_container_width=True, hide_index=True)

    with tab_settle:
        st.subheader("📝 Registrar Resultados Oficiales de Carreras")
        cursor.execute("SELECT race_id, track, race_date, race_number, top_pick FROM predictions_audit WHERE status = 'PENDING'")
        settle_options = {f"{r['track']} Carrera #{r['race_number']} ({r['race_date']}) - Top Pick: {r['top_pick']}": r["race_id"] for r in cursor.fetchall()}

        if not settle_options:
            st.success("¡No hay carreras pendientes por liquidar!")
        else:
            with st.form("form_settle"):
                selected_settle_label = st.selectbox("Selecciona la carrera a verificar:", list(settle_options.keys()))
                sel_race_id = settle_options[selected_settle_label]

                col_w1, col_w2 = st.columns(2)
                with col_w1:
                    winner_name = st.text_input("Nombre del Caballo Ganador Oficial:")
                    winner_odds = st.number_input("Dividendo Final del Ganador (ej. 2.50 = 5/2):", min_value=0.1, value=2.5, step=0.1)
                with col_w2:
                    second_horse = st.text_input("Segundo Lugar (opcional):")
                    notes_txt = st.text_input("Notas de aprendizaje (ej. 'Puntero solitario dominó', etc.):")

                submit_btn = st.form_submit_button("Guardar Resultado y Actualizar Estadísticas")
                if submit_btn:
                    if not winner_name:
                        st.error("Por favor ingresa el nombre del ganador.")
                    else:
                        record_race_result(sel_race_id, winner_name, winner_odds, second_place=second_horse, race_notes=notes_txt)
                        st.success("¡Resultado registrado con éxito y métricas actualizadas!")
                        st.rerun()

    conn.close()


# =========================================================================
# VISTA 2: GACETA DE PAST PERFORMANCES (ESTILO BRISNET / DRF)
# =========================================================================
elif nav_mode == "📑 Gaceta de Past Performances (DRF)":
    entries = get_race_entries(selected_race_id)
    if not entries:
        st.warning("No hay participantes registrados para esta carrera.")
        st.stop()

    st.title("📑 Gaceta Oficial de Carreras (Past Performances)")
    st.subheader(f"{curr_race['track_name']} — Carrera #{curr_race['race_number']}")
    surface_map = {"D": "Arena (Dirt)", "T": "Grama (Turf)", "A": "Tapeta / Sintética"}

    col_hdr1, col_hdr2, col_hdr3, col_hdr4 = st.columns(4)
    with col_hdr1:
        st.metric("Distancia", f"{curr_race['distance_furlongs']} Furlongs", f"~{int(curr_race['distance_furlongs']*201.16)} m")
    with col_hdr2:
        st.metric("Superficie", surface_map.get(curr_race['surface'], curr_race['surface']), f"Pista: {curr_race['track_condition']}")
    with col_hdr3:
        st.metric("Bolsa (Purse)", f"${curr_race['purse']:,.0f}" if curr_race['purse'] else "N/A", f"Clase: {curr_race['race_class']}")
    with col_hdr4:
        st.metric("Participantes", f"{len(entries)} Ejemplares", f"Baranda: {curr_race.get('rail_distance_feet', 0)} ft")

    st.markdown("---")

    # 1. Tabla Resumen de Inscritos
    st.markdown("### 📋 Nómina Oficial y Conexiones")
    roster_rows = []
    for e in entries:
        works = json.loads(e.get("workouts_json") or "[]")
        work_display = "Sin registro reciente"
        if works:
            w = works[0]
            bullet = " 🎯 BULLET" if w.get("rank", 99) <= 2 else ""
            work_display = f"{w['distance_furlongs']}f en {w['time_seconds']}s ({w.get('rank', '-')}/{w.get('total_workers', '-')}){bullet}"

        roster_rows.append({
            "PP": e["post_position"],
            "Ejemplar": e["horse_name"],
            "ML Odds": f"{e['morning_line_odds']:.1f}-1",
            "Jinete": e["jockey"],
            "Entrenador": e["trainer"],
            "Peso (lbs)": e["weight"],
            "Aperos": e.get("equipment") or "Normal",
            "Medicación": e.get("medication") or "Ninguna",
            "Último Ejercicio": work_display
        })

    st.dataframe(pd.DataFrame(roster_rows), use_container_width=True, hide_index=True)

    st.markdown("---")

    # 2. Selector o Vista de Past Performances
    st.markdown("### 🔍 Fichas Detalladas de Actuaciones Anteriores (Running Lines)")

    horse_names = [e["horse_name"] for e in entries]
    view_filter = st.radio(
        "Modo de Lectura:",
        ["📖 Ver Todos los Ejemplares (Gaceta Completa)", "🎯 Inspeccionar Ejemplar Individual"],
        horizontal=True
    )

    if view_filter == "🎯 Inspeccionar Ejemplar Individual":
        chosen_horse = st.selectbox("Selecciona Ejemplar a Estudiar:", horse_names)
        displayed_entries = [e for e in entries if e["horse_name"] == chosen_horse]
    else:
        displayed_entries = entries

    for e in displayed_entries:
        h_name = e["horse_name"]
        pps = get_horse_past_performances(h_name, before_date=curr_race["race_date"])
        works = json.loads(e.get("workouts_json") or "[]")

        bullet_badge = " 🎯 [BULLET WORKOUT]" if works and works[0].get("rank", 99) <= 2 else ""
        eq_badge = f" | Aperos: {e['equipment']}" if e.get("equipment") else ""

        with st.container():
            st.markdown(f"""
            <div style="background-color: #1E293B; padding: 12px 18px; border-radius: 8px; border-left: 6px solid #3B82F6; margin-top: 15px; margin-bottom: 8px;">
                <h4 style="margin: 0; color: #FFFFFF;">
                    #{e['post_position']} <b>{h_name}</b> &nbsp;
                    <span style="font-size: 14px; color: #93C5FD;">(ML: {e['morning_line_odds']:.1f}-1)</span>
                    <span style="font-size: 13px; color: #34D399; font-weight: bold;">{bullet_badge}</span>
                </h4>
                <div style="font-size: 13px; color: #CBD5E1; margin-top: 5px;">
                    <b>Jinete:</b> {e['jockey']} &nbsp;|&nbsp; 
                    <b>Entrenador:</b> {e['trainer']} &nbsp;|&nbsp; 
                    <b>Peso:</b> {e['weight']} lbs &nbsp;|&nbsp; 
                    <b>Medicación:</b> {e.get('medication', 'Lasix')}{eq_badge}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Aprontes matutinos
            if works:
                w_str_list = []
                for w in works:
                    rank_str = f"({w.get('rank', '-')}/{w.get('total_workers', '-')})" if "rank" in w else ""
                    b_mark = " 🎯 BULLET" if w.get("rank", 99) <= 2 else ""
                    w_str_list.append(f"📅 {w['date']}: {w['distance_furlongs']}f en {w['time_seconds']}s {rank_str}{b_mark}")
                st.caption(f"**Ejercicios Matutinos (Breezes):** {' | '.join(w_str_list)}")

            # Tabla de actuaciones pasadas
            if not pps:
                st.info("ℹ️ Sin actuaciones previas oficiales registradas (Ejemplar Debutante).")
            else:
                pp_display = []
                for p in pps:
                    pos_str = "🥇 1º (Ganó)" if p["finish_position"] == 1 else f"{p['finish_position']}º (+{p['lengths_behind']} cpos)"
                    speed_str = f"{p['speed_rating']:.1f}" if p.get("speed_rating") else "N/A"
                    time_str = f"{p['final_time_sec']:.2f}s" if p.get("final_time_sec") else "N/A"
                    pp_display.append({
                        "Fecha": p["race_date"],
                        "Hipódromo": p["track"],
                        "Distancia": f"{p['distance_furlongs']}f",
                        "Sup": p["surface"],
                        "Pista": p["track_condition"],
                        "Clase": p["race_class"],
                        "Llegada": pos_str,
                        "Tiempo": time_str,
                        "Speed Figure (Beyer/Brisnet)": speed_str,
                        "Jinete": p["jockey"],
                        "Dividendo": f"{p['official_odds']:.1f}-1"
                    })
                st.dataframe(pd.DataFrame(pp_display), use_container_width=True, hide_index=True)


# =========================================================================
# VISTA 3: ANÁLISIS Y PRONÓSTICO EN VIVO
# =========================================================================
elif nav_mode == "🏇 Análisis y Pronóstico en Vivo":
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

    st.title(f"{curr_race['track_name']} — Carrera #{curr_race['race_number']}")
    surface_map = {"D": "Arena (Dirt)", "T": "Grama (Turf)", "A": "Tapeta / Sintética"}
    st.caption(f"**Clase:** {curr_race['race_class']} | **Distancia:** {curr_race['distance_furlongs']} Furlongs | **Superficie:** {surface_map.get(curr_race['surface'], curr_race['surface'])} ({curr_race['track_condition']})")

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

    # Tabla General
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

        work_badge = "🎯 BULLET" if p.get("has_bullet_workout") else f"{p.get('workout_score', 60):.0f} pts"
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

    # Gráficos
    st.subheader("📊 Análisis Táctico y Estrategia de Apuestas")
    tab1, tab2, tab3 = st.tabs([
        "⚡ Comparativa de Velocidad", 
        "⚔️ Simulador de Ritmo (Pace Battle)", 
        "🎯 Boletos y Estrategia Sugerida"
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
        fig_pace = px.scatter(
            x=[p["horse_name"] for p in ranked],
            y=[p.get("pace_adjustment", 0) for p in ranked],
            color=[p["pace_style"] for p in ranked],
            size=[p["composite_score"] for p in ranked],
            labels={"x": "Ejemplar", "y": "Ajuste por Ritmo (+/- Puntos)", "color": "Estilo"},
            title=f"Impacto del Escenario de Ritmo ({pace['scenario']}) en cada Participante",
            template="plotly_dark",
            height=380
        )
        fig_pace.add_hline(y=0, line_dash="dash", line_color="gray")
        st.plotly_chart(fig_pace, use_container_width=True)

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

    st.markdown("---")

    # Past Performances
    st.subheader("📑 Fichas de Past Performance y Aprontes Matutinos")
    for p in profiles:
        pps = p["past_performances"]
        bullet_label = "🎯 [BULLET WORKOUT]" if p.get("has_bullet_workout") else ""
        with st.expander(f"#{p['post_position']} **{p['horse_name']}** | Pace: {p['pace_style']} | Rating: {p['composite_score']} {bullet_label}"):
            st.markdown(f"**Último Ejercicio:** {p.get('last_workout', 'N/A')} | **Estado:** {p.get('workout_verdict', 'Normal')}")
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
