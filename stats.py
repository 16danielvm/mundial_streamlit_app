import streamlit as st
import pandas as pd
from database import read_df
from utils import parse_dt, flag
from mvp import get_daily_mvps

def calculate_streaks(points_list):
    best_positive = 0
    current_positive = 0

    worst_negative = 0
    current_negative = 0

    for points in points_list:
        if points > 0:
            current_positive += 1
            best_positive = max(best_positive, current_positive)
            current_negative = 0
        else:
            current_negative += 1
            worst_negative = max(worst_negative, current_negative)
            current_positive = 0

    return best_positive, worst_negative


def get_user_position(user_id):
    standings = read_df(
        """
        SELECT
            u.id AS user_id,
            COALESCE(SUM(p.points), 0) AS puntos,
            SUM(CASE WHEN p.points = 3 THEN 1 ELSE 0 END) AS exactos,
            SUM(CASE WHEN p.points = 1 THEN 1 ELSE 0 END) AS resultados,
            COUNT(p.id) AS predicciones
        FROM users u
        LEFT JOIN predictions p ON p.user_id = u.id
        WHERE u.username <> 'modeloxgb'
        GROUP BY u.id
        ORDER BY puntos DESC, exactos DESC, resultados DESC, predicciones DESC
        """
    )

    if standings.empty:
        return "-"

    standings.insert(0, "posicion", range(1, len(standings) + 1))
    row = standings[standings["user_id"] == user_id]

    if row.empty:
        return "-"

    return f"{int(row.iloc[0]['posicion'])}°"





def get_user_badges(user_id, user_tz):
    badges = []

    achievements = read_df(
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
          AND u.username <> 'modeloxgb'
        ORDER BY u.name, m.match_datetime ASC
        """
    )

    if achievements.empty:
        return badges

    exactos = (
        achievements[achievements["points"] == 3]
        .groupby("user_id")
        .size()
        .reset_index(name="valor")
        .sort_values("valor", ascending=False)
    )

    if not exactos.empty and int(exactos.iloc[0]["user_id"]) == int(user_id):
        badges.append("👑 Rey del Marcador")

    resumen = (
        achievements
        .groupby("user_id")
        .agg(
            predicciones=("points", "count"),
            aciertos=("points", lambda x: (x > 0).sum())
        )
        .reset_index()
    )
    resumen["porcentaje"] = resumen["aciertos"] / resumen["predicciones"] * 100
    resumen = resumen.sort_values(["porcentaje", "aciertos"], ascending=False)

    if not resumen.empty and int(resumen.iloc[0]["user_id"]) == int(user_id):
        badges.append("🎯 Nostradamus")

    mvps = get_daily_mvps(user_tz)

    if not mvps.empty:
        user_mvps = mvps[mvps["user_id"] == user_id]
        for _, row in user_mvps.iterrows():
            badges.append(f"⭐ MVP {row['fecha']}")

    return badges


def tab_my_stats(user_id, username, user_tz):
    st.subheader("📊 Mis estadísticas")

    if not user_id:
        st.warning("Primero inicia sesión para ver tus estadísticas.")
        return

    df = read_df(
        """
        SELECT
            m.home_team,
            m.away_team,
            m.match_datetime,
            p.predicted_home_score,
            p.predicted_away_score,
            m.home_score,
            m.away_score,
            p.points
        FROM predictions p
        JOIN matches m ON m.id = p.match_id
        WHERE p.user_id = %s
          AND m.home_score IS NOT NULL
          AND m.away_score IS NOT NULL
        ORDER BY m.match_datetime ASC
        """,
        (user_id,),
    )

    if df.empty:
        st.info("Aún no tienes partidos finalizados con predicciones.")
        return

    total_points = int(df["points"].sum())
    total_predictions = len(df)
    exactos = int((df["points"] == 3).sum())
    resultados = int((df["points"] == 1).sum())
    aciertos = int((df["points"] > 0).sum())
    accuracy = aciertos / total_predictions * 100
    best_streak, worst_streak = calculate_streaks(df["points"].tolist())
    position = get_user_position(user_id)

    mvps = get_daily_mvps(user_tz)
    user_mvps = 0 if mvps.empty else len(mvps[mvps["user_id"] == user_id])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🏆 Puntos totales", total_points)
    c2.metric("📈 Posición actual", position)
    c3.metric("🎯 Acierto", f"{accuracy:.1f}%")
    c4.metric("⭐ MVPs obtenidos", user_mvps)

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("👑 Marcadores exactos", exactos)
    c6.metric("⚽ Resultados acertados", resultados)
    c7.metric("🔥 Mejor racha", f"{best_streak} partidos")
    c8.metric("💀 Peor racha", f"{worst_streak} partidos")

    st.divider()

    badges = get_user_badges(user_id, user_tz)

    st.markdown("### 🏅 Medallas conseguidas")

    if badges:
        for badge in badges:
            st.success(badge)
    else:
        st.info("Aún no tienes medallas desbloqueadas.")

    st.divider()

    st.markdown("### 🥇 Distribución de resultados")

    dist = pd.DataFrame({
        "Resultado": ["3 puntos", "1 punto", "0 puntos"],
        "Cantidad": [
            int((df["points"] == 3).sum()),
            int((df["points"] == 1).sum()),
            int((df["points"] == 0).sum()),
        ]
    })

    st.bar_chart(dist.set_index("Resultado"))

    st.divider()

    st.markdown("### 📈 Evolución de puntos")

    df["fecha"] = df["match_datetime"].apply(
        lambda x: parse_dt(x, user_tz).strftime("%d/%m/%Y")
    )
    df["puntos_acumulados"] = df["points"].cumsum()

    evolution = df[["fecha", "puntos_acumulados"]].copy()
    evolution = evolution.groupby("fecha")["puntos_acumulados"].max().reset_index()

    st.line_chart(evolution.set_index("fecha"))

    st.divider()

    st.markdown("### 🏆 Récord personal")

    daily = (
        df.groupby("fecha")
        .agg(
            puntos=("points", "sum"),
            exactos=("points", lambda x: (x == 3).sum()),
            aciertos=("points", lambda x: (x > 0).sum()),
        )
        .reset_index()
        .sort_values(["puntos", "exactos", "aciertos"], ascending=False)
    )

    best_day = daily.iloc[0]

    st.metric(
        label=f"Mejor fecha: {best_day['fecha']}",
        value=f"{int(best_day['puntos'])} puntos",
        delta=f"{int(best_day['exactos'])} exactos | {int(best_day['aciertos'])} aciertos"
    )

    st.divider()

    st.markdown("### 🏟 Historial de predicciones")

    df["partido"] = (
        df["home_team"].apply(lambda x: f"{flag(x)} {x}")
        + " vs "
        + df["away_team"].apply(lambda x: f"{flag(x)} {x}")
    )

    df["predicción"] = (
        df["predicted_home_score"].astype(int).astype(str)
        + " - "
        + df["predicted_away_score"].astype(int).astype(str)
    )

    df["resultado"] = (
        df["home_score"].astype(int).astype(str)
        + " - "
        + df["away_score"].astype(int).astype(str)
    )

    history = df[[
        "fecha",
        "partido",
        "predicción",
        "resultado",
        "points"
    ]].rename(columns={"points": "puntos"})

    st.dataframe(history, use_container_width=True, hide_index=True)