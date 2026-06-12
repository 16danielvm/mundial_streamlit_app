import bcrypt
import psycopg2
import streamlit as st
from database import get_conn, execute
from utils import now_utc

def hash_password(password):
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(password, password_hash):
    password_bytes = password.encode("utf-8")
    hash_bytes = password_hash.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hash_bytes)

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