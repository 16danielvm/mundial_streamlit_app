from database import execute, read_df
from utils import now_utc
from datetime import datetime, date, time
import streamlit as st
from predictions import format_match
import pandas as pd
from config import ADMIN_PIN, ET, UTC
from football_data_service import update_results_from_api
from match_service import update_result
from auth import admin_reset_password


def add_match(home_team, away_team, match_date, match_time, stadium, stage):
    dt_utc = datetime.combine(match_date, match_time, tzinfo=ET).astimezone(UTC).isoformat()
    execute(
        """
        INSERT INTO matches(home_team, away_team, match_datetime, stadium, stage, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (home_team.strip(), away_team.strip(), dt_utc, stadium.strip(), stage.strip(), now_utc().isoformat()),
    )




def tab_admin(user_tz):
    st.subheader("Panel de administrador")
    pin = st.text_input("Clave de administrador", type="password")
    if pin != ADMIN_PIN:
        st.warning("Ingresa la clave de administrador para editar partidos y resultados.")
        return

    st.success("Acceso de administrador concedido.")
    st.info("Al añadir partidos manualmente, captura la hora oficial del Este de Estados Unidos.")

    st.markdown("### 🔄 Resultados automáticos")

    if st.button("Actualizar resultados desde Football-Data"):
        try:
            updated, skipped = update_results_from_api()

            if updated > 0:
                st.success(f"Se actualizaron {updated} partido(s) y se recalcularon los puntos.")
            else:
                st.info("No se encontraron partidos nuevos para actualizar.")

            if skipped:
                st.warning("Algunos partidos finalizados no se encontraron en tu base:")
                for match in skipped:
                    st.write(f"- {match}")

        except Exception as e:
            st.error("No se pudieron actualizar los resultados desde Football-Data.")
            st.error(str(e))

    st.divider()
    
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
    st.markdown("### 👥 Gestión de usuarios")

    users = read_df(
        """
        SELECT name, username
        FROM users
        ORDER BY name ASC
        """
    )

    if users.empty:
        st.info("No hay usuarios registrados.")
    else:
        user_options = {
            f"{row['name']} (@{row['username']})": row["username"]
            for _, row in users.iterrows()
        }

        selected_user = st.selectbox(
            "Selecciona un usuario",
            list(user_options.keys()),
            key="reset_password_user"
        )

        username_to_reset = user_options[selected_user]

        if st.button("Generar contraseña temporal"):
            ok, msg, temp_password = admin_reset_password(username_to_reset)

            if ok:
                st.success(msg)
                st.code(temp_password, language="text")
                st.info("Envía esta contraseña temporal al usuario. Luego podrá cambiarla en la pestaña Mi cuenta.")
            else:
                st.error(msg)

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
