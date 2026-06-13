from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import streamlit as st

FLAGS = {
    "México": "🇲🇽",
    "Estados Unidos": "🇺🇸",
    "Canadá": "🇨🇦",
    "Argentina": "🇦🇷",
    "Brasil": "🇧🇷",
    "España": "🇪🇸",
    "Francia": "🇫🇷",
    "Alemania": "🇩🇪",
    "Japón": "🇯🇵",
    "Colombia": "🇨🇴",
    "Inglaterra": "💂‍♀️",
    "Portugal": "🇵🇹",
    "Croacia": "🇭🇷",
    "Marruecos": "🇲🇦",
    "Australia": "🇦🇺",
    "Paraguay": "🇵🇾",
    "Uruguay": "🇺🇾",
    "Egipto": "🇪🇬",
    "Suecia": "🇸🇪",
    "Suiza": "🇨🇭",
    "Países Bajos": "🇳🇱",
    "Arabia Saudí": "🇸🇦",
    "República de Corea": "🇰🇷",
    "República Checa": "🇨🇿",
    "Sudáfrica": "🇿🇦",
    "Catar": "🇶🇦",
    "Bosnia y Herzegovina": "🇧🇦",
    "Haití": "🇭🇹",
    "Escocia": "Escocia",
    "Curazao": "🇨🇼",
    "Costa de Marfil": "🇨🇮",
    "Ecuador": "🇪🇨",
    "Túnez": "🇹🇳",
    "Bélgica": "🇧🇪",
    "RI de Irán": "🇮🇷",
    "Nueva Zelanda": "🇳🇿",
    "Senegal": "🇸🇳",
    "Irak": "🇮🇶",
    "Argelia": "🇩🇿",
    "Austria": "🇦🇹",
    "Jordania": "🇯🇴",
    "RD Congo": "🇨🇩",
    "Ghana": "🇬🇭",
    "Panamá": "🇵🇦",
    "Uzbekistán": "🇺🇿",
    "Cabo Verde": "🇨🇻",
    "Noruega": "🇳🇴",
    "Turquía": "🇹🇷"
}

ET = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")
DEFAULT_TZ_NAME = "America/Mexico_City"
DEFAULT_TZ = ZoneInfo(DEFAULT_TZ_NAME)
ADMIN_PIN = st.secrets["ADMIN_PIN"]