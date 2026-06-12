import streamlit as st
from database import read_df

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
