import streamlit as st
from database import read_df
from utils import parse_dt
import pandas as pd


def tab_daily_mvp(user_tz):
    st.subheader("⭐ MVP de la jornada")
    st.caption("Jugador con mejor rendimiento en cada día de partidos.")

    df = read_df(
        """
        SELECT
            u.name AS jugador,
            p.points,
            m.match_datetime
        FROM predictions p
        JOIN users u ON u.id = p.user_id
        JOIN matches m ON m.id = p.match_id
        WHERE m.home_score IS NOT NULL
          AND m.away_score IS NOT NULL
        ORDER BY m.match_datetime ASC
        """
    )

    if df.empty:
        st.info("Aún no hay partidos finalizados para calcular MVP por fecha.")
        return

    df["fecha"] = df["match_datetime"].apply(
        lambda x: parse_dt(x, user_tz).strftime("%d/%m/%Y")
    )

    resumen = (
        df.groupby(["fecha", "jugador"])
        .agg(
            puntos=("points", "sum"),
            predicciones=("points", "count"),
            exactos=("points", lambda x: (x == 3).sum()),
            aciertos=("points", lambda x: (x > 0).sum()),
        )
        .reset_index()
    )

    fechas = sorted(resumen["fecha"].unique())

    for fecha in fechas:
        dia = resumen[resumen["fecha"] == fecha].copy()

        dia = dia.sort_values(
            ["puntos", "exactos", "aciertos", "predicciones"],
            ascending=[False, False, False, True]
        )

        mejor = dia.iloc[0]

        ganadores = dia[
            (dia["puntos"] == mejor["puntos"]) &
            (dia["exactos"] == mejor["exactos"]) &
            (dia["aciertos"] == mejor["aciertos"]) &
            (dia["predicciones"] == mejor["predicciones"])
        ]

        st.markdown(f"### ⭐ MVP {fecha}")

        if len(ganadores) == 1:
            row = ganadores.iloc[0]
            st.metric(
                label=row["jugador"],
                value=f"{int(row['puntos'])} puntos",
                delta=f"{int(row['exactos'])} exactos | {int(row['aciertos'])} aciertos"
            )
        else:
            nombres = ", ".join(ganadores["jugador"].tolist())
            st.warning(f"Empate MVP: {nombres}")
            st.dataframe(
                ganadores[["jugador", "puntos", "exactos", "aciertos", "predicciones"]],
                use_container_width=True,
                hide_index=True
            )

        with st.expander("Ver tabla completa de la fecha"):
            st.dataframe(
                dia[["jugador", "puntos", "exactos", "aciertos", "predicciones"]],
                use_container_width=True,
                hide_index=True
            )

        st.divider()

def get_daily_mvps(user_tz):
    df = read_df(
        """
        SELECT
            u.id AS user_id,
            u.name AS jugador,
            p.points,
            m.match_datetime
        FROM predictions p
        JOIN users u ON u.id = p.user_id
        JOIN matches m ON m.id = p.match_id
        WHERE m.home_score IS NOT NULL
          AND m.away_score IS NOT NULL
        ORDER BY m.match_datetime ASC
        """
    )

    if df.empty:
        return pd.DataFrame()

    df["fecha"] = df["match_datetime"].apply(
        lambda x: parse_dt(x, user_tz).strftime("%d/%m/%Y")
    )

    resumen = (
        df.groupby(["fecha", "user_id", "jugador"])
        .agg(
            puntos=("points", "sum"),
            predicciones=("points", "count"),
            exactos=("points", lambda x: (x == 3).sum()),
            aciertos=("points", lambda x: (x > 0).sum()),
        )
        .reset_index()
    )

    winners = []

    for fecha in sorted(resumen["fecha"].unique()):
        dia = resumen[resumen["fecha"] == fecha].copy()

        dia = dia.sort_values(
            ["puntos", "exactos", "aciertos", "predicciones"],
            ascending=[False, False, False, True]
        )

        mejor = dia.iloc[0]

        ganadores = dia[
            (dia["puntos"] == mejor["puntos"]) &
            (dia["exactos"] == mejor["exactos"]) &
            (dia["aciertos"] == mejor["aciertos"]) &
            (dia["predicciones"] == mejor["predicciones"])
        ]

        winners.append(ganadores)

    return pd.concat(winners, ignore_index=True) if winners else pd.DataFrame()