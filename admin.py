from database import execute, read_df
from utils import now_utc
from datetime import datetime, date, time
import streamlit as st
from predictions import recalculate_match_points, format_match
import pandas as pd
from config import ADMIN_PIN, ET, UTC


def add_match(home_team, away_team, match_date, match_time, stadium, stage):
    dt_utc = datetime.combine(match_date, match_time, tzinfo=ET).astimezone(UTC).isoformat()
    execute(
        """
        INSERT INTO matches(home_team, away_team, match_datetime, stadium, stage, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (home_team.strip(), away_team.strip(), dt_utc, stadium.strip(), stage.strip(), now_utc().isoformat()),
    )


def update_result(match_id, home_score, away_score):
    status = "Finalizado" if home_score is not None and away_score is not None else "Pendiente"
    execute(
        """
        UPDATE matches
        SET home_score = %s, away_score = %s, status = %s
        WHERE id = %s
        """,
        (home_score, away_score, status, match_id),
    )
    recalculate_match_points(match_id)

def tab_admin(user_tz):
    st.subheader("Panel de administrador")
    pin = st.text_input("Clave de administrador", type="password")
    if pin != ADMIN_PIN:
        st.warning("Ingresa la clave de administrador para editar partidos y resultados.")
        return

    st.success("Acceso de administrador concedido.")
    st.info("Al añadir partidos manualmente, captura la hora oficial del Este de Estados Unidos.")

    st.markdown("### Añadir partido")
    with st.form("add_match_form"):
        c1, c2 = st.columns(2)
        home = c1.text_input("Equipo local")
        away = c2.text_input("Equipo visitante")
        c3, c4 = st.columns(2)
        m_date = c3.date_input("Fecha oficial ET", value=date(2026, 6, 11))
        m_time = c4.time_input("Hora oficial ET", value=time(19, 0))
        stadium = st.text_input("Estadio", value="Por definir")
        stage = st.text_input("Grupo/Fase", value="Grupo A")
        submitted = st.form_submit_button("Añadir partido")

    if submitted:
        if not home.strip() or not away.strip():
            st.error("Debes escribir ambos equipos.")
        else:
            add_match(home, away, m_date, m_time, stadium, stage)
            st.success("Partido añadido correctamente.")
            st.rerun()

    st.divider()
    st.markdown("### Capturar resultado real")
    matches = read_df("SELECT * FROM matches ORDER BY match_datetime ASC")
    if matches.empty:
        st.info("No hay partidos registrados.")
        return

    options = {format_match(row, user_tz): int(row["id"]) for _, row in matches.iterrows()}
    selected = st.selectbox("Partido", list(options.keys()), key="admin_match_select")
    match_id = options[selected]
    match = matches[matches["id"] == match_id].iloc[0]

    current_home = 0 if pd.isna(match["home_score"]) else int(match["home_score"])
    current_away = 0 if pd.isna(match["away_score"]) else int(match["away_score"])

    with st.form("result_form"):
        c1, c2 = st.columns(2)
        real_home = c1.number_input(f"Goles {match['home_team']}", min_value=0, max_value=30, value=current_home, step=1)
        real_away = c2.number_input(f"Goles {match['away_team']}", min_value=0, max_value=30, value=current_away, step=1)
        submitted_result = st.form_submit_button("Guardar resultado y recalcular puntos")

    if submitted_result:
        update_result(match_id, int(real_home), int(real_away))
        st.success("Resultado guardado y puntos recalculados.")
        st.rerun()

    st.divider()
    st.markdown("### Datos crudos")
    with st.expander("Ver predicciones registradas"):
        preds = read_df(
            """
            SELECT u.name AS jugador,
                   m.home_team || ' vs ' || m.away_team AS partido,
                   p.predicted_home_score || ' - ' || p.predicted_away_score AS prediccion,
                   p.points AS puntos,
                   p.updated_at AS actualizado_utc
            FROM predictions p
            JOIN users u ON u.id = p.user_id
            JOIN matches m ON m.id = p.match_id
            ORDER BY p.updated_at DESC
            """
        )
        st.dataframe(preds, use_container_width=True, hide_index=True)
