import psycopg2
import pandas as pd
import streamlit as st

def get_conn():
    try:
        return psycopg2.connect(st.secrets["DATABASE_URL"])
    except Exception as e:
        st.error("No se pudo conectar a la base de datos.")
        st.error(str(e))
        st.stop()


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