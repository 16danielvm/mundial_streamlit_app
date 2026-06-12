# import sqlite3
import psycopg2
from datetime import datetime, date, time
from pathlib import Path
import bcrypt
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pandas as pd
import streamlit as st
from streamlit_js_eval import streamlit_js_eval


ET = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")
DEFAULT_TZ_NAME = "America/Mexico_City"
DEFAULT_TZ = ZoneInfo(DEFAULT_TZ_NAME)
ADMIN_PIN = st.secrets.get("ADMIN_PIN", "Control16")

st.set_page_config(
    page_title="Quiniela Mundial 2026",
    page_icon="⚽",
    layout="wide",
)


def get_conn():
    try:
        return psycopg2.connect(st.secrets["DATABASE_URL"])
    except Exception as e:
        st.error("No se pudo conectar a la base de datos.")
        st.error(str(e))
        st.stop()


def now_utc():
    return datetime.now(UTC)


def now_user(user_tz):
    return datetime.now(user_tz)

def hash_password(password):
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(password, password_hash):
    password_bytes = password.encode("utf-8")
    hash_bytes = password_hash.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hash_bytes)


def et_to_utc(year, month, day, hour, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=ET).astimezone(UTC).isoformat()


def get_browser_timezone():
    tz_name = streamlit_js_eval(
        js_expressions="Intl.DateTimeFormat().resolvedOptions().timeZone",
        key="browser_timezone",
    )

    if tz_name:
        try:
            return ZoneInfo(tz_name), tz_name
        except ZoneInfoNotFoundError:
            pass
        except Exception:
            pass

    return DEFAULT_TZ, DEFAULT_TZ_NAME


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL
    )
    """
)

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS matches (
            id SERIAL PRIMARY KEY,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            match_datetime TIMESTAMPTZ NOT NULL,
            stadium TEXT,
            stage TEXT,
            status TEXT NOT NULL DEFAULT 'Pendiente',
            home_score INTEGER,
            away_score INTEGER,
            created_at TIMESTAMPTZ NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            match_id INTEGER NOT NULL REFERENCES matches(id),
            predicted_home_score INTEGER NOT NULL,
            predicted_away_score INTEGER NOT NULL,
            points INTEGER DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL,
            UNIQUE(user_id, match_id)
        )
        """
    )

    conn.commit()
    seed_matches(conn)
    conn.close()


def seed_matches(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM matches")
    count = cur.fetchone()[0]
    if count > 0:
        return

    now = now_utc().isoformat()

    matches = [
        # Jueves, 11 de junio 2026
        ("México", "Sudáfrica", et_to_utc(2026, 6, 11, 15), "Estadio Ciudad de México", "Grupo A"),
        ("República de Corea", "República Checa", et_to_utc(2026, 6, 11, 22), "Estadio Guadalajara", "Grupo A"),

        # Viernes, 12 de junio 2026
        ("Canadá", "Bosnia y Herzegovina", et_to_utc(2026, 6, 12, 15), "Estadio Toronto", "Grupo B"),
        ("Estados Unidos", "Paraguay", et_to_utc(2026, 6, 12, 21), "Estadio Los Ángeles", "Grupo D"),

        # Sábado, 13 de junio 2026
        ("Catar", "Suiza", et_to_utc(2026, 6, 13, 15), "Estadio Bahía de San Francisco", "Grupo B"),
        ("Brasil", "Marruecos", et_to_utc(2026, 6, 13, 18), "Estadio Nueva York Nueva Jersey", "Grupo C"),
        ("Haití", "Escocia", et_to_utc(2026, 6, 13, 21), "Estadio Boston", "Grupo C"),
        ("Australia", "Turquía", et_to_utc(2026, 6, 13, 0), "Estadio BC Place Vancouver", "Grupo D"),

        # Domingo, 14 de junio 2026
        ("Alemania", "Curazao", et_to_utc(2026, 6, 14, 13), "Estadio Houston", "Grupo E"),
        ("Países Bajos", "Japón", et_to_utc(2026, 6, 14, 16), "Estadio Dallas", "Grupo F"),
        ("Costa de Marfil", "Ecuador", et_to_utc(2026, 6, 14, 19), "Estadio Filadelfia", "Grupo E"),
        ("Suecia", "Túnez", et_to_utc(2026, 6, 14, 22), "Estadio Monterrey", "Grupo F"),

        # Lunes, 15 de junio 2026
        ("España", "Cabo Verde", et_to_utc(2026, 6, 15, 12), "Estadio Atlanta", "Grupo H"),
        ("Bélgica", "Egipto", et_to_utc(2026, 6, 15, 15), "Estadio Seattle", "Grupo G"),
        ("Arabia Saudí", "Uruguay", et_to_utc(2026, 6, 15, 18), "Estadio Miami", "Grupo H"),
        ("RI de Irán", "Nueva Zelanda", et_to_utc(2026, 6, 15, 21), "Estadio Los Ángeles", "Grupo G"),

        # Martes, 16 de junio 2026
        ("Francia", "Senegal", et_to_utc(2026, 6, 16, 15), "Estadio Nueva York Nueva Jersey", "Grupo I"),
        ("Irak", "Noruega", et_to_utc(2026, 6, 16, 18), "Estadio Boston", "Grupo I"),
        ("Argentina", "Argelia", et_to_utc(2026, 6, 16, 21), "Estadio Kansas City", "Grupo J"),
        ("Austria", "Jordania", et_to_utc(2026, 6, 16, 0), "Estadio Bahía de San Francisco", "Grupo J"),

        # Miércoles, 17 de junio 2026
        ("Portugal", "RD Congo", et_to_utc(2026, 6, 17, 13), "Estadio Houston", "Grupo K"),
        ("Inglaterra", "Croacia", et_to_utc(2026, 6, 17, 16), "Estadio Dallas", "Grupo L"),
        ("Ghana", "Panamá", et_to_utc(2026, 6, 17, 19), "Estadio Toronto", "Grupo L"),
        ("Uzbekistán", "Colombia", et_to_utc(2026, 6, 17, 22), "Estadio Ciudad de México", "Grupo K"),

        # Jueves, 18 de junio 2026
        ("República Checa", "Sudáfrica", et_to_utc(2026, 6, 18, 12), "Estadio Atlanta", "Grupo A"),
        ("Suiza", "Bosnia y Herzegovina", et_to_utc(2026, 6, 18, 15), "Estadio Los Ángeles", "Grupo B"),
        ("Canadá", "Catar", et_to_utc(2026, 6, 18, 18), "Estadio BC Place Vancouver", "Grupo B"),
        ("México", "República de Corea", et_to_utc(2026, 6, 18, 21), "Estadio Guadalajara", "Grupo A"),

        # Viernes, 19 de junio 2026
        ("Estados Unidos", "Australia", et_to_utc(2026, 6, 19, 15), "Estadio Seattle", "Grupo D"),
        ("Escocia", "Marruecos", et_to_utc(2026, 6, 19, 18), "Estadio Boston", "Grupo C"),
        ("Brasil", "Haití", et_to_utc(2026, 6, 19, 21), "Estadio Filadelfia", "Grupo C"),
        ("Turquía", "Paraguay", et_to_utc(2026, 6, 19, 0), "Estadio Bahía de San Francisco", "Grupo D"),

        # Sábado, 20 de junio 2026
        ("Países Bajos", "Suecia", et_to_utc(2026, 6, 20, 13), "Estadio Houston", "Grupo F"),
        ("Alemania", "Costa de Marfil", et_to_utc(2026, 6, 20, 16), "Estadio Toronto", "Grupo E"),
        ("Ecuador", "Curazao", et_to_utc(2026, 6, 20, 22), "Estadio Kansas City", "Grupo E"),
        ("Túnez", "Japón", et_to_utc(2026, 6, 20, 0), "Estadio Monterrey", "Grupo F"),

        # Domingo, 21 de junio 2026
        ("España", "Arabia Saudí", et_to_utc(2026, 6, 21, 12), "Estadio Atlanta", "Grupo H"),
        ("Bélgica", "Irán", et_to_utc(2026, 6, 21, 15), "Estadio Los Ángeles", "Grupo G"),
        ("Uruguay", "Cabo Verde", et_to_utc(2026, 6, 21, 18), "Estadio Miami", "Grupo H"),
        ("Nueva Zelanda", "Egipto", et_to_utc(2026, 6, 21, 21), "Estadio BC Place Vancouver", "Grupo G"),

        # Lunes, 22 de junio 2026
        ("Argentina", "Austria", et_to_utc(2026, 6, 22, 13), "Estadio Dallas", "Grupo J"),
        ("Francia", "Irak", et_to_utc(2026, 6, 22, 17), "Estadio Filadelfia", "Grupo I"),
        ("Noruega", "Senegal", et_to_utc(2026, 6, 22, 20), "Estadio Nueva York Nueva Jersey", "Grupo I"),
        ("Jordania", "Argelia", et_to_utc(2026, 6, 22, 23), "Estadio Bahía de San Francisco", "Grupo J"),

        # Martes, 23 de junio 2026
        ("Portugal", "Uzbekistán", et_to_utc(2026, 6, 23, 13), "Estadio Houston", "Grupo K"),
        ("Inglaterra", "Ghana", et_to_utc(2026, 6, 23, 16), "Estadio Boston", "Grupo L"),
        ("Panamá", "Croacia", et_to_utc(2026, 6, 23, 19), "Estadio Toronto", "Grupo L"),
        ("Colombia", "RD Congo", et_to_utc(2026, 6, 23, 22), "Estadio Guadalajara", "Grupo K"),

        # Miércoles, 24 de junio 2026
        ("Suiza", "Canadá", et_to_utc(2026, 6, 24, 15), "Estadio BC Place Vancouver", "Grupo B"),
        ("Bosnia y Herzegovina", "Catar", et_to_utc(2026, 6, 24, 15), "Estadio Seattle", "Grupo B"),
        ("Escocia", "Brasil", et_to_utc(2026, 6, 24, 18), "Estadio Miami", "Grupo C"),
        ("Marruecos", "Haití", et_to_utc(2026, 6, 24, 18), "Estadio Atlanta", "Grupo C"),
        ("República Checa", "México", et_to_utc(2026, 6, 24, 21), "Estadio Ciudad de México", "Grupo A"),
        ("Sudáfrica", "República de Corea", et_to_utc(2026, 6, 24, 21), "Estadio Monterrey", "Grupo A"),

        # Jueves, 25 de junio 2026
        ("Curazao", "Costa de Marfil", et_to_utc(2026, 6, 25, 16), "Estadio Filadelfia", "Grupo E"),
        ("Ecuador", "Alemania", et_to_utc(2026, 6, 25, 16), "Estadio Nueva York Nueva Jersey", "Grupo E"),
        ("Japón", "Suecia", et_to_utc(2026, 6, 25, 19), "Estadio Dallas", "Grupo F"),
        ("Túnez", "Países Bajos", et_to_utc(2026, 6, 25, 19), "Estadio Kansas City", "Grupo F"),
        ("Turquía", "Estados Unidos", et_to_utc(2026, 6, 25, 22), "Estadio Los Ángeles", "Grupo D"),
        ("Paraguay", "Australia", et_to_utc(2026, 6, 25, 22), "Estadio Bahía de San Francisco", "Grupo D"),

        # Viernes, 26 de junio 2026
        ("Noruega", "Francia", et_to_utc(2026, 6, 26, 15), "Estadio Boston", "Grupo I"),
        ("Senegal", "Irak", et_to_utc(2026, 6, 26, 15), "Estadio Toronto", "Grupo I"),
        ("Cabo Verde", "Arabia Saudí", et_to_utc(2026, 6, 26, 20), "Estadio Houston", "Grupo H"),
        ("Uruguay", "España", et_to_utc(2026, 6, 26, 20), "Estadio Guadalajara", "Grupo H"),
        ("Egipto", "Irán", et_to_utc(2026, 6, 26, 23), "Estadio Seattle", "Grupo G"),
        ("Nueva Zelanda", "Bélgica", et_to_utc(2026, 6, 26, 23), "Estadio BC Place Vancouver", "Grupo G"),

        # Sábado, 27 de junio 2026
        ("Panamá", "Inglaterra", et_to_utc(2026, 6, 27, 17), "Estadio Nueva York Nueva Jersey", "Grupo L"),
        ("Croacia", "Ghana", et_to_utc(2026, 6, 27, 17), "Estadio Filadelfia", "Grupo L"),
        ("Colombia", "Portugal", et_to_utc(2026, 6, 27, 19, 30), "Estadio Miami", "Grupo K"),
        ("RD Congo", "Uzbekistán", et_to_utc(2026, 6, 27, 19, 30), "Estadio Atlanta", "Grupo K"),
        ("Argelia", "Austria", et_to_utc(2026, 6, 27, 22), "Estadio Kansas City", "Grupo J"),
        ("Jordania", "Argentina", et_to_utc(2026, 6, 27, 22), "Estadio Dallas", "Grupo J"),
    ]

    cur.executemany(
        """
        INSERT INTO matches(home_team, away_team, match_datetime, stadium, stage, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        [(h, a, dt, stadium, stage, now) for h, a, dt, stadium, stage in matches],
    )

    conn.commit()


def read_df(query, params=()):
    conn = get_conn()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def execute(query, params=()):
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute(query, params)
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()


def parse_dt(dt_value, user_tz):
    if isinstance(dt_value, datetime):
        return dt_value.astimezone(user_tz)

    return datetime.fromisoformat(str(dt_value)).astimezone(user_tz)


def can_predict(match_datetime_text):
    match_dt_utc = datetime.fromisoformat(match_datetime_text).astimezone(UTC)
    return now_utc() < match_dt_utc


def register_user(name, username, password):
    name = name.strip()
    username = username.strip().lower()
    password = password.strip()

    if not name or not username or not password:
        return False, "Todos los campos son obligatorios."

    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres."

    password_hash = hash_password(password)

    try:
        execute(
            """
            INSERT INTO users(name, username, password_hash, created_at)
            VALUES (%s, %s, %s, %s)
            """,
            (name, username, password_hash, now_utc().isoformat()),
        )
        return True, "Usuario registrado correctamente. Ahora puedes iniciar sesión."

    except psycopg2.IntegrityError:
        return False, "Ese nombre de usuario ya existe. Elige otro."


def login_user(username, password):
    username = username.strip().lower()
    password = password.strip()

    if not username or not password:
        return False, "Ingresa usuario y contraseña."

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, name, username, password_hash
        FROM users
        WHERE username = %s
        """,
        (username,),
    )
    user = cur.fetchone()
    conn.close()

    if not user:
        return False, "Usuario o contraseña incorrectos."

    user_id, name, username, password_hash = user

    if not verify_password(password, password_hash):
        return False, "Usuario o contraseña incorrectos."

    st.session_state["user_id"] = user_id
    st.session_state["name"] = name
    st.session_state["username"] = username

    return True, f"Bienvenido, {name}."


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
    return f"{row['home_team']} vs {row['away_team']} — {dt.strftime('%d/%m/%Y %H:%M')}"


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


def main_header(user_tz, user_tz_name):
    st.title("⚽ Quiniela Mundial 2026")
    st.caption("Predice marcadores, suma puntos y mira quién manda en la tabla. Sin VAR para excusas.")
    st.info(
        f"Horario detectado: {user_tz_name}. "
        f"Hora actual: {now_user(user_tz).strftime('%d/%m/%Y %H:%M:%S')}. "
        "Los partidos se guardan internamente en UTC."
    )


def sidebar_auth():
    st.sidebar.header("Cuenta")

    if "user_id" in st.session_state:
        st.sidebar.success(f"Sesión iniciada como: {st.session_state['name']}")

        if st.sidebar.button("Cerrar sesión"):
            st.session_state.pop("user_id", None)
            st.session_state.pop("name", None)
            st.session_state.pop("username", None)
            st.rerun()

        return st.session_state["user_id"], st.session_state["name"]

    auth_mode = st.sidebar.radio(
        "Acceso",
        ["Iniciar sesión", "Crear cuenta"]
    )

    if auth_mode == "Iniciar sesión":
        username = st.sidebar.text_input("Usuario")
        password = st.sidebar.text_input("Contraseña", type="password")

        if st.sidebar.button("Entrar"):
            ok, msg = login_user(username, password)
            if ok:
                st.sidebar.success(msg)
                st.rerun()
            else:
                st.sidebar.error(msg)

    else:
        name = st.sidebar.text_input("Nombre visible", placeholder="Ej. Daniel")
        username = st.sidebar.text_input("Usuario", placeholder="Ej. daniel16")
        password = st.sidebar.text_input("Contraseña", type="password")
        confirm_password = st.sidebar.text_input("Confirmar contraseña", type="password")

        if st.sidebar.button("Crear cuenta"):
            if password != confirm_password:
                st.sidebar.error("Las contraseñas no coinciden.")
            else:
                ok, msg = register_user(name, username, password)
                if ok:
                    st.sidebar.success(msg)
                else:
                    st.sidebar.error(msg)

    return None, None


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
    col1.metric("Local", match["home_team"])
    col2.metric("Visitante", match["away_team"])
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


def tab_calendar(user_tz):
    st.subheader("Calendario de partidos")
    df = read_df("SELECT * FROM matches ORDER BY match_datetime ASC")
    if df.empty:
        st.info("No hay partidos registrados.")
        return

    df["fecha"] = df["match_datetime"].apply(lambda x: parse_dt(x, user_tz).strftime("%d/%m/%Y"))
    df["hora"] = df["match_datetime"].apply(lambda x: parse_dt(x, user_tz).strftime("%H:%M"))
    df["partido"] = df["home_team"] + " vs " + df["away_team"]
    df["resultado"] = df.apply(
        lambda r: "Pendiente" if pd.isna(r["home_score"]) else f"{int(r['home_score'])} - {int(r['away_score'])}",
        axis=1,
    )
    df["predicción"] = df["match_datetime"].apply(lambda x: "Abierta" if can_predict(x) else "Cerrada")

    st.dataframe(
        df[["fecha", "hora", "stage", "partido", "stadium", "status", "resultado", "predicción"]],
        use_container_width=True,
        hide_index=True,
    )


def tab_standings():
    st.subheader("Tabla de clasificación")
    standings = read_df(
        """
        SELECT
            u.name AS jugador,
            COALESCE(SUM(p.points), 0) AS puntos,
            COUNT(p.id) AS predicciones,
            SUM(CASE WHEN p.points = 3 THEN 1 ELSE 0 END) AS marcadores_exactos,
            SUM(CASE WHEN p.points = 1 THEN 1 ELSE 0 END) AS resultados_acertados
        FROM users u
        LEFT JOIN predictions p ON p.user_id = u.id
        GROUP BY u.id, u.name
        ORDER BY puntos DESC, marcadores_exactos DESC, resultados_acertados DESC, predicciones DESC
        """
    )

    if standings.empty:
        st.info("Todavía no hay participantes.")
        return

    standings.insert(0, "posición", range(1, len(standings) + 1))
    st.dataframe(standings, use_container_width=True, hide_index=True)


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


def main():
    init_db()
    user_tz, user_tz_name = get_browser_timezone()
    main_header(user_tz, user_tz_name)
    user_id, username = sidebar_auth()

    tab1, tab2, tab3, tab4 = st.tabs([
        "⚽ Predicciones",
        "📅 Calendario",
        "🏆 Clasificación",
        "👑 Admin",
    ])

    with tab1:
        tab_predictions(user_id, username, user_tz)
    with tab2:
        tab_calendar(user_tz)
    with tab3:
        tab_standings()
    with tab4:
        tab_admin(user_tz)


if __name__ == "__main__":
    main()
