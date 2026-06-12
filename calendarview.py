import streamlit as st
import pandas as pd
from utils import parse_dt, flag, can_predict
from database import read_df

def tab_calendar(user_tz):
    st.subheader("Calendario de partidos")
    df = read_df("SELECT * FROM matches ORDER BY match_datetime ASC")
    if df.empty:
        st.info("No hay partidos registrados.")
        return

    df["fecha"] = df["match_datetime"].apply(lambda x: parse_dt(x, user_tz).strftime("%d/%m/%Y"))
    df["hora"] = df["match_datetime"].apply(lambda x: parse_dt(x, user_tz).strftime("%H:%M"))
    df["partido"] = (
        df["home_team"].apply(lambda x: f"{flag(x)} {x}")
        + " vs "
        + df["away_team"].apply(lambda x: f"{flag(x)} {x}")
    )
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