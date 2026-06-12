from database import get_conn, read_df, execute
from utils import now_utc, parse_dt, can_predict, flag
import streamlit as st


def result_type(home, away):
    if home > away:
        return "home"
    if home < away:
        return "away"
    return "draw"


def calculate_points(pred_home, pred_away, real_home, real_away):
    if real_home is None or real_away is None:
        return 0
    if pred_home == real_home and pred_away == real_away:
        return 3
    if result_type(pred_home, pred_away) == result_type(real_home, real_away):
        return 1
    return 0



def recalculate_match_points(match_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT home_score, away_score FROM matches WHERE id = %s", (match_id,))
    match = cur.fetchone()
    if not match or match[0] is None or match[1] is None:
        conn.close()
        return

    real_home, real_away = match
    cur.execute(
        "SELECT id, predicted_home_score, predicted_away_score FROM predictions WHERE match_id = %s",
        (match_id,),
    )
    predictions = cur.fetchall()

    for pred_id, pred_home, pred_away in predictions:
        points = calculate_points(pred_home, pred_away, real_home, real_away)
        cur.execute("UPDATE predictions SET points = %s WHERE id = %s", (points, pred_id))

    conn.commit()
    conn.close()


def upsert_prediction(user_id, match_id, pred_home, pred_away):
    match = read_df("SELECT * FROM matches WHERE id = %s", (match_id,))
    if match.empty:
        return False, "El partido no existe."

    row = match.iloc[0]
    if not can_predict(row["match_datetime"]):
        return False, "Este partido ya inició. No se pueden registrar ni modificar predicciones."

    timestamp = now_utc().isoformat()
    execute(
        """
        INSERT INTO predictions(user_id, match_id, predicted_home_score, predicted_away_score, points, created_at, updated_at)
        VALUES (%s, %s, %s, %s, 0, %s, %s)
        ON CONFLICT(user_id, match_id)
        DO UPDATE SET
            predicted_home_score = excluded.predicted_home_score,
            predicted_away_score = excluded.predicted_away_score,
            updated_at = excluded.updated_at
        """,
        (user_id, match_id, pred_home, pred_away, timestamp, timestamp),
    )
    return True, "Predicción guardada correctamente."


def format_match(row, user_tz):
    dt = parse_dt(row["match_datetime"], user_tz)
    return (
        f"{flag(row['home_team'])} {row['home_team']} "
        f"vs "
        f"{flag(row['away_team'])} {row['away_team']} "
        f"— {dt.strftime('%d/%m/%Y %H:%M')}"
    )

def tab_predictions(user_id, username, user_tz):
    st.subheader("Registrar predicción")

    if not user_id:
        st.warning("Primero inicia sesión para registrar predicciones.")
        return

    matches = read_df("SELECT * FROM matches ORDER BY match_datetime ASC")
    if matches.empty:
        st.warning("Todavía no hay partidos registrados.")
        return

    options = {format_match(row, user_tz): int(row["id"]) for _, row in matches.iterrows()}
    selected_label = st.selectbox("Selecciona un partido", list(options.keys()))
    match_id = options[selected_label]
    match = matches[matches["id"] == match_id].iloc[0]

    locked = not can_predict(match["match_datetime"])
    dt = parse_dt(match["match_datetime"], user_tz)

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Local",
        f"{flag(match['home_team'])} {match['home_team']}"
    )

    col2.metric(
        "Visitante",
        f"{flag(match['away_team'])} {match['away_team']}"
    )
    col3.metric("Inicio", dt.strftime("%d/%m/%Y %H:%M"))

    if locked:
        st.error("Predicciones cerradas para este partido.")
    else:
        st.success("Predicciones abiertas.")

    existing = read_df(
        "SELECT * FROM predictions WHERE user_id = %s AND match_id = %s",
        (user_id, match_id),
    )

    default_home = int(existing.iloc[0]["predicted_home_score"]) if not existing.empty else 0
    default_away = int(existing.iloc[0]["predicted_away_score"]) if not existing.empty else 0

    with st.form("prediction_form"):
        c1, c2 = st.columns(2)
        pred_home = c1.number_input(f"Goles {match['home_team']}", min_value=0, max_value=30, value=default_home, step=1)
        pred_away = c2.number_input(f"Goles {match['away_team']}", min_value=0, max_value=30, value=default_away, step=1)
        submitted = st.form_submit_button("Guardar predicción", disabled=locked)

    if submitted:
        ok, msg = upsert_prediction(user_id, match_id, int(pred_home), int(pred_away))
        if ok:
            st.success(msg)
        else:
            st.error(msg)

    st.divider()
    st.subheader("Mis predicciones")
    my_preds = read_df(
        """
        SELECT m.home_team || ' vs ' || m.away_team AS partido,
               m.match_datetime AS fecha,
               p.predicted_home_score || ' - ' || p.predicted_away_score AS prediccion,
               CASE
                    WHEN m.home_score IS NULL THEN 'Pendiente'
                    ELSE m.home_score || ' - ' || m.away_score
               END AS resultado_real,
               p.points AS puntos
        FROM predictions p
        JOIN matches m ON m.id = p.match_id
        WHERE p.user_id = %s
        ORDER BY m.match_datetime ASC
        """,
        (user_id,),
    )
    if not my_preds.empty:
        my_preds["fecha"] = my_preds["fecha"].apply(lambda x: parse_dt(x, user_tz).strftime("%d/%m/%Y %H:%M"))
        st.dataframe(my_preds, use_container_width=True, hide_index=True)
    else:
        st.info("Aún no has registrado predicciones.")

def tab_all_predictions(user_tz):
    st.subheader("Predicciones de todos")

    matches = read_df("SELECT * FROM matches ORDER BY match_datetime ASC")

    options = {format_match(row, user_tz): int(row["id"]) for _, row in matches.iterrows()}
    selected = st.selectbox("Selecciona un partido", list(options.keys()), key="all_predictions_match")
    match_id = options[selected]
    match = matches[matches["id"] == match_id].iloc[0]

    if can_predict(match["match_datetime"]):
        st.warning("Las predicciones de este partido se mostrarán cuando inicie el partido.")
        return

    preds = read_df(
        """
        SELECT 
            u.name AS jugador,
            p.predicted_home_score || ' - ' || p.predicted_away_score AS prediccion,
            p.points AS puntos
        FROM predictions p
        JOIN users u ON u.id = p.user_id
        WHERE p.match_id = %s
        ORDER BY u.name ASC
        """,
        (match_id,),
    )

    if preds.empty:
        st.info("Nadie registró predicción para este partido.")
    else:
        st.dataframe(preds, use_container_width=True, hide_index=True)