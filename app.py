import streamlit as st

from matches_seed import init_db
from utils import get_browser_timezone, now_user
from auth import sidebar_auth
from predictions import tab_predictions, tab_all_predictions
from calendarview import tab_calendar
from standings import tab_standings
from admin import tab_admin
from achievements import tab_achievements
from mvp import tab_daily_mvp
from stats import tab_my_stats
from account import tab_account


st.set_page_config(
    page_title="Quiniela Mundial 2026",
    page_icon="⚽",
    layout="wide",
)


def main_header(user_tz, user_tz_name):
    st.title("⚽ Quiniela Mundial 2026 sin pample")
    st.caption("Predice marcadores, suma puntos y mira quién manda en la tabla. Sin VAR para excusas.")
    st.info(
        f"Horario detectado: {user_tz_name}. "
        f"Hora actual: {now_user(user_tz).strftime('%d/%m/%Y %H:%M:%S')}. "
        "Los partidos se guardan internamente en UTC."
    )


def main():
    init_db()

    user_tz, user_tz_name = get_browser_timezone()
    main_header(user_tz, user_tz_name)

    user_id, username = sidebar_auth()

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "⚽ Predicciones",
        "📅 Calendario",
        "🏆 Clasificación",
        "👀 Predicciones de todos",
        "🏅 Logros",
        "⭐ MVP",
        "📊 Mis estadísticas",
        "⚙️ Mi cuenta",
        "👑 Admin",
])

    with tab1:
        tab_predictions(user_id, username, user_tz)

    with tab2:
        tab_calendar(user_tz)

    with tab3:
        tab_standings()

    with tab4:
        tab_all_predictions(user_tz)

    with tab5:
        tab_achievements()

    with tab6:
        tab_daily_mvp(user_tz)

    with tab7:
        tab_my_stats(user_id, username, user_tz)

    with tab8:
        tab_account(user_id, username)

    with tab9:
        tab_admin(user_tz)


if __name__ == "__main__":
    main()
