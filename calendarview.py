import streamlit as st
import pandas as pd
from utils import parse_dt, flag, can_predict, now_user
from database import read_df
from football_data_service import get_live_world_cup_matches

from streamlit_autorefresh import st_autorefresh


def get_match_display_status(row, user_tz, live_data=None):
    key = (row["home_team"], row["away_team"])

    if live_data and key in live_data:
        api_match = live_data[key]

        minute = api_match.get("minute")

        if minute is not None:
            return f"En vivo · {minute}'"

        match_dt = parse_dt(row["match_datetime"], user_tz)
        now = now_user(user_tz)
        elapsed = int((now - match_dt).total_seconds() // 60)

        if elapsed < 0:
            return match_dt.strftime("%H:%M")

        return f"En vivo · {elapsed}'"

    match_dt = parse_dt(row["match_datetime"], user_tz)

    if not pd.isna(row["home_score"]) and not pd.isna(row["away_score"]):
        return "Finalizado"

    if now_user(user_tz) < match_dt:
        return match_dt.strftime("%H:%M")

    return "En vivo"

def render_match_card(row, user_tz, live_data=None):
    key = (row["home_team"], row["away_team"])
    api_match = live_data.get(key) if live_data else None

    status_text = get_match_display_status(row, user_tz, live_data)

    if api_match:
        home_score = api_match.get("home_score")
        away_score = api_match.get("away_score")
    else:
        home_score = row["home_score"]
        away_score = row["away_score"]

    home_score = "-" if pd.isna(home_score) else int(home_score)
    away_score = "-" if pd.isna(away_score) else int(away_score)

    with st.container(border=True):
        c_top1, c_top2 = st.columns([2, 1])

        with c_top1:
            st.caption("Copa Mundial FIFA 2026")

        with c_top2:
            st.markdown(f"**{status_text}**")

        c1, c2, c3 = st.columns([2, 1, 2])

        with c1:
            st.markdown(f"## {flag(row['home_team'])}")
            st.markdown(f"**{row['home_team']}**")

        with c2:
            st.markdown(
                f"<h1 style='text-align:center;'>{home_score} - {away_score}</h1>",
                unsafe_allow_html=True
            )

        with c3:
            st.markdown(f"## {flag(row['away_team'])}")
            st.markdown(f"**{row['away_team']}**")

        st.caption(row["stage"])

def tab_calendar(user_tz):

    st_autorefresh(
        interval=60000,
        key="calendar_live_refresh"
    )

    st.subheader("Calendario de partidos")

    df = read_df("SELECT * FROM matches ORDER BY match_datetime ASC")

    if df.empty:
        st.info("No hay partidos registrados.")
        return

    df["fecha"] = df["match_datetime"].apply(
        lambda x: parse_dt(x, user_tz).strftime("%d/%m/%Y")
    )

    today = now_user(user_tz).strftime("%d/%m/%Y")
    today_matches = df[df["fecha"] == today].copy()

    if not today_matches.empty:
        st.markdown("### Partidos de hoy")

        try:
            live_data = get_live_world_cup_matches()
        except Exception:
            live_data = {}

        cols = st.columns(2)

        for idx, (_, row) in enumerate(today_matches.iterrows()):
            with cols[idx % 2]:
                render_match_card(row, user_tz, live_data)

    st.divider()

    st.markdown("### Calendario completo")

    df["hora"] = df["match_datetime"].apply(
        lambda x: parse_dt(x, user_tz).strftime("%H:%M")
    )

    df["partido"] = (
        df["home_team"].apply(lambda x: f"{flag(x)} {x}")
        + " vs "
        + df["away_team"].apply(lambda x: f"{flag(x)} {x}")
    )

    df["resultado"] = df.apply(
        lambda r: "Pendiente"
        if pd.isna(r["home_score"])
        else f"{int(r['home_score'])} - {int(r['away_score'])}",
        axis=1,
    )

    df["predicción"] = df["match_datetime"].apply(
        lambda x: "Abierta" if can_predict(x) else "Cerrada"
    )

    st.dataframe(
        df[[
            "fecha",
            "hora",
            "partido",
            "status",
            "resultado",
            "predicción",
        ]],
        use_container_width=True,
        hide_index=True,
    )