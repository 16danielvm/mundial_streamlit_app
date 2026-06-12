import requests
import streamlit as st

from database import read_df
from match_service import update_result


TEAM_NAME_MAP = {
    "Mexico": "México",
    "South Africa": "Sudáfrica",
    "South Korea": "República de Corea",
    "Korea Republic": "República de Corea",
    "Czechia": "República Checa",
    "Canada": "Canadá",
    "Bosnia-Herzegovina": "Bosnia y Herzegovina",
    "United States": "Estados Unidos",
    "Paraguay": "Paraguay",
    "Qatar": "Catar",
    "Switzerland": "Suiza",
    "Brazil": "Brasil",
    "Morocco": "Marruecos",
    "Haiti": "Haití",
    "Scotland": "Escocia",
    "Australia": "Australia",
    "Turkey": "Turquía",
    "Germany": "Alemania",
    "Curaçao": "Curazao",
    "Netherlands": "Países Bajos",
    "Japan": "Japón",
    "Ivory Coast": "Costa de Marfil",
    "Ecuador": "Ecuador",
    "Sweden": "Suecia",
    "Tunisia": "Túnez",
    "Spain": "España",
    "Cape Verde": "Cabo Verde",
    "Belgium": "Bélgica",
    "Egypt": "Egipto",
    "Saudi Arabia": "Arabia Saudí",
    "Uruguay": "Uruguay",
    "Iran": "RI de Irán",
    "New Zealand": "Nueva Zelanda",
    "France": "Francia",
    "Senegal": "Senegal",
    "Iraq": "Irak",
    "Norway": "Noruega",
    "Argentina": "Argentina",
    "Algeria": "Argelia",
    "Austria": "Austria",
    "Jordan": "Jordania",
    "Portugal": "Portugal",
    "DR Congo": "RD Congo",
    "England": "Inglaterra",
    "Croatia": "Croacia",
    "Ghana": "Ghana",
    "Panama": "Panamá",
    "Uzbekistan": "Uzbekistán",
    "Colombia": "Colombia",
}

def football_data_headers():
    return {
        "X-Auth-Token": st.secrets["FOOTBALL_API_KEY"]
    }


def get_world_cup_matches():
    url = "https://api.football-data.org/v4/competitions/WC/matches"

    response = requests.get(
        url,
        headers=football_data_headers(),
        timeout=20
    )

    response.raise_for_status()
    return response.json()


def map_team_name(api_name):
    return TEAM_NAME_MAP.get(api_name, api_name)

def update_results_from_api():
    data = get_world_cup_matches()
    api_matches = data.get("matches", [])

    updated = 0
    skipped = []

    for item in api_matches:
        if item.get("status") != "FINISHED":
            continue

        home_api = item["homeTeam"]["name"]
        away_api = item["awayTeam"]["name"]

        home_team = map_team_name(home_api)
        away_team = map_team_name(away_api)

        home_score = item["score"]["fullTime"]["home"]
        away_score = item["score"]["fullTime"]["away"]

        if home_score is None or away_score is None:
            continue

        match = read_df(
            """
            SELECT id, home_score, away_score
            FROM matches
            WHERE home_team = %s
              AND away_team = %s
            """,
            (home_team, away_team),
        )

        if match.empty:
            skipped.append(f"{home_api} vs {away_api}")
            continue

        match_id = int(match.iloc[0]["id"])

        update_result(match_id, int(home_score), int(away_score))
        updated += 1

    return updated, skipped