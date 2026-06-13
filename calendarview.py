import streamlit as st
import pandas as pd
from utils import parse_dt, flag, can_predict, now_user
from database import read_df



def get_match_display_status(row, user_tz):
    match_dt = parse_dt(row["match_datetime"], user_tz)
    now = now_user(user_tz)

    if not pd.isna(row["home_score"]) and not pd.isna(row["away_score"]):
        return "Finalizado"

    if now < match_dt:
        return match_dt.strftime("%H:%M")

    elapsed = int((now - match_dt).total_seconds() // 60)

    if elapsed <= 45:
        return f"En vivo · {elapsed}'"

    if elapsed <= 60:
        return "Descanso"

    if elapsed <= 105:
        return f"En vivo · {elapsed - 15}'"

    return "En vivo"

def render_match_card(row, user_tz):
    status_text = get_match_display_status(row, user_tz)

    home_score = "-" if pd.isna(row["home_score"]) else int(row["home_score"])
    away_score = "-" if pd.isna(row["away_score"]) else int(row["away_score"])

    if status_text == "Finalizado":
        status_color = "#94a3b8"
    elif "En vivo" in status_text:
        status_color = "#22c55e"
    else:
        status_color = "#38bdf8"

    st.markdown(
        f"""
        <div style="
            background:#111827;
            border:1px solid #263244;
            border-radius:18px;
            padding:18px;
            margin-bottom:16px;
            color:white;
        ">
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                margin-bottom:14px;
                color:#cbd5e1;
                font-size:13px;
            ">
                <span>Copa Mundial FIFA 2026</span>
                <span style="color:{status_color}; font-weight:700;">{status_text}</span>
            </div>

            <div style="
                display:grid;
                grid-template-columns:1fr auto 1fr;
                align-items:center;
                gap:14px;
                text-align:center;
            ">
                <div>
                    <div style="font-size:34px;">{flag(row["home_team"])}</div>
                    <div style="font-size:16px; margin-top:6px;">{row["home_team"]}</div>
                </div>

                <div style="
                    font-size:34px;
                    font-weight:700;
                    white-space:nowrap;
                ">
                    {home_score} - {away_score}
                </div>

                <div>
                    <div style="font-size:34px;">{flag(row["away_team"])}</div>
                    <div style="font-size:16px; margin-top:6px;">{row["away_team"]}</div>
                </div>
            </div>

            <div style="
                text-align:center;
                margin-top:14px;
                color:#94a3b8;
                font-size:13px;
            ">
                {row["stage"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def tab_calendar(user_tz):
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

        cols = st.columns(2)

        for idx, (_, row) in enumerate(today_matches.iterrows()):
            with cols[idx % 2]:
                render_match_card(row, user_tz)

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