import streamlit as st
import pandas as pd
import plotly.express as px

from database import read_df
from utils import parse_dt

def show_position_evolution(user_tz):
    st.markdown("### 📈 Evolución de posiciones")
    st.caption("Cómo ha cambiado la posición de cada participante conforme avanzan los partidos.")

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
          AND u.username <> 'modeloxgb'
        ORDER BY m.match_datetime ASC
        """
    )

    if df.empty:
        st.info("Aún no hay suficientes resultados para mostrar la evolución de posiciones.")
        return

    df["fecha"] = df["match_datetime"].apply(
        lambda x: parse_dt(x, user_tz).strftime("%d/%m/%Y")
    )

    daily = (
        df.groupby(["fecha", "jugador"])
        .agg(
            puntos=("points", "sum"),
            exactos=("points", lambda x: (x == 3).sum()),
            resultados=("points", lambda x: (x == 1).sum()),
            predicciones=("points", "count"),
        )
        .reset_index()
    )

    fechas = sorted(daily["fecha"].unique(), key=lambda x: pd.to_datetime(x, dayfirst=True))
    jugadores = sorted(daily["jugador"].unique())

    acumulado = []

    for fecha in fechas:
        data_fecha = daily[daily["fecha"].isin(fechas[:fechas.index(fecha) + 1])]

        resumen = (
            data_fecha.groupby("jugador")
            .agg(
                puntos=("puntos", "sum"),
                exactos=("exactos", "sum"),
                resultados=("resultados", "sum"),
                predicciones=("predicciones", "sum"),
            )
            .reset_index()
        )

        for jugador in jugadores:
            if jugador not in resumen["jugador"].values:
                resumen = pd.concat([
                    resumen,
                    pd.DataFrame([{
                        "jugador": jugador,
                        "puntos": 0,
                        "exactos": 0,
                        "resultados": 0,
                        "predicciones": 0,
                    }])
                ], ignore_index=True)

        resumen = resumen.sort_values(
            ["puntos", "exactos", "resultados", "predicciones"],
            ascending=[False, False, False, False]
        ).reset_index(drop=True)

        resumen["posicion"] = range(1, len(resumen) + 1)
        resumen["fecha"] = fecha

        acumulado.append(resumen)

    evolution = pd.concat(acumulado, ignore_index=True)

    fig = px.line(
        evolution,
        x="fecha",
        y="posicion",
        color="jugador",
        markers=True,
        hover_data={
            "puntos": True,
            "exactos": True,
            "resultados": True,
            "predicciones": True,
            "posicion": True,
        },
    )

    fig.update_yaxes(
        autorange="reversed",
        title="Posición"
    )

    fig.update_xaxes(title="Fecha")

    fig.update_layout(
        height=500,
        legend_title_text="Participante",
        margin=dict(l=20, r=20, t=40, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)

def tab_standings(user_tz):
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
        WHERE u.username <> 'modeloxgb'
        GROUP BY u.id, u.name
        ORDER BY puntos DESC, marcadores_exactos DESC, resultados_acertados DESC, predicciones DESC
        """
    )

    if standings.empty:
        st.info("Todavía no hay participantes.")
        return

    standings.insert(0, "posición", range(1, len(standings) + 1))
    st.dataframe(standings, use_container_width=True, hide_index=True)
    st.divider()

    st.markdown("### 🤖 Rendimiento del predictor")

    model_standing = read_df(
        """
        SELECT
            u.name AS jugador,
            COALESCE(SUM(p.points), 0) AS puntos,
            COUNT(p.id) AS predicciones,
            SUM(CASE WHEN p.points = 3 THEN 1 ELSE 0 END) AS marcadores_exactos,
            SUM(CASE WHEN p.points = 1 THEN 1 ELSE 0 END) AS resultados_acertados
        FROM users u
        LEFT JOIN predictions p ON p.user_id = u.id
        WHERE u.username = 'modeloxgb'
        GROUP BY u.id, u.name
        """
    )

    if model_standing.empty:
        st.info("El predictor todavía no tiene predicciones registradas.")
    else:
        st.dataframe(model_standing, use_container_width=True, hide_index=True)

    st.divider()
    show_position_evolution(user_tz)

