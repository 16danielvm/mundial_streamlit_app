import streamlit as st
from database import read_df
from utils import parse_dt
import pandas as pd


def tab_achievements():
    st.subheader("🏅 Medallas y logros")
    st.caption("Reconocimientos especiales según el rendimiento de los participantes.")

    finished_predictions = read_df(
        """
        SELECT 
            u.name AS jugador,
            p.points,
            p.predicted_home_score,
            p.predicted_away_score,
            m.match_datetime
        FROM predictions p
        JOIN users u ON u.id = p.user_id
        JOIN matches m ON m.id = p.match_id
        WHERE m.home_score IS NOT NULL
          AND m.away_score IS NOT NULL
        ORDER BY u.name, m.match_datetime ASC
        """
    )

    if finished_predictions.empty:
        st.info("Aún no hay partidos finalizados con predicciones para calcular logros.")
        return

    col1, col2, col3 = st.columns(3)
    col4, col5 = st.columns(2)

    # 👑 Rey del Marcador
    exactos = (
        finished_predictions[finished_predictions["points"] == 3]
        .groupby("jugador")
        .size()
        .reset_index(name="valor")
        .sort_values("valor", ascending=False)
    )

    with col1:
        st.markdown("### 👑 Rey del Marcador")
        st.caption("Participante con más marcadores exactos acertados.")
        if exactos.empty:
            st.info("Todavía no hay marcadores exactos.")
        else:
            row = exactos.iloc[0]
            st.metric(row["jugador"], f"{int(row['valor'])} exactos")

    # 🎯 Nostradamus
    resumen = (
        finished_predictions
        .groupby("jugador")
        .agg(
            predicciones=("points", "count"),
            aciertos=("points", lambda x: (x > 0).sum())
        )
        .reset_index()
    )
    resumen["valor"] = resumen["aciertos"] / resumen["predicciones"] * 100
    resumen = resumen.sort_values(["valor", "aciertos"], ascending=False)

    with col2:
        st.markdown("### 🎯 Nostradamus")
        st.caption("Mayor porcentaje de predicciones que sumaron puntos.")
        row = resumen.iloc[0]
        st.metric(row["jugador"], f"{row['valor']:.1f}% de acierto")

    # 🔥 Enrachado
    best_streaks = []

    for jugador, group in finished_predictions.groupby("jugador"):
        current = 0
        best = 0

        for points in group["points"]:
            if points > 0:
                current += 1
                best = max(best, current)
            else:
                current = 0

        best_streaks.append({
            "jugador": jugador,
            "valor": best
        })

    streaks_df = pd.DataFrame(best_streaks).sort_values("valor", ascending=False)

    with col3:
        st.markdown("### 🔥 Enrachado")
        st.caption("Mayor racha de partidos consecutivos sumando puntos.")
        row = streaks_df.iloc[0]
        if row["valor"] == 0:
            st.info("Todavía nadie tiene racha positiva.")
        else:
            st.metric(row["jugador"], f"{int(row['valor'])} partidos")

    # 💀 Mufa Oficial
    worst_streaks = []

    for jugador, group in finished_predictions.groupby("jugador"):
        current = 0
        worst = 0

        for points in group["points"]:
            if points == 0:
                current += 1
                worst = max(worst, current)
            else:
                current = 0

        worst_streaks.append({
            "jugador": jugador,
            "valor": worst
        })

    mufa_df = pd.DataFrame(worst_streaks).sort_values("valor", ascending=False)

    with col4:
        st.markdown("### 💀 Mufa Oficial")
        st.caption("Mayor racha de partidos consecutivos sin sumar puntos.")
        row = mufa_df.iloc[0]
        if row["valor"] == 0:
            st.info("Todavía nadie desbloquea esta tragedia.")
        else:
            st.metric(row["jugador"], f"{int(row['valor'])} partidos")
    
    # 🫏 0 Ball Knowledge
    zero_ball = (
        finished_predictions
        .groupby("jugador")
        .agg(
            partidos=("points", "count"),
            aciertos=("points", lambda x: (x > 0).sum())
        )
        .reset_index()
        .sort_values(["aciertos", "partidos"], ascending=True)
    )

    with col5:
        st.markdown("### 🫏 0 Ball Knowledge")
        st.caption("Participante con menos partidos acertados. El fútbol definitivamente no es lo suyo.")
        row = zero_ball.iloc[0]
        st.metric(row["jugador"], f"{int(row['aciertos'])} aciertos")

