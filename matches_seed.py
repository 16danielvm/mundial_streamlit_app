from database import get_conn
from utils import now_utc, et_to_utc

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL
    )
    """
)

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS matches (
            id SERIAL PRIMARY KEY,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            match_datetime TIMESTAMPTZ NOT NULL,
            stadium TEXT,
            stage TEXT,
            status TEXT NOT NULL DEFAULT 'Pendiente',
            home_score INTEGER,
            away_score INTEGER,
            created_at TIMESTAMPTZ NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            match_id INTEGER NOT NULL REFERENCES matches(id),
            predicted_home_score INTEGER NOT NULL,
            predicted_away_score INTEGER NOT NULL,
            points INTEGER DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL,
            UNIQUE(user_id, match_id)
        )
        """
    )

    conn.commit()
    seed_matches(conn)
    conn.close()


def seed_matches(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM matches")
    count = cur.fetchone()[0]
    if count > 0:
        return

    now = now_utc().isoformat()

    matches = [
        # Jueves, 11 de junio 2026
        ("México", "Sudáfrica", et_to_utc(2026, 6, 11, 15), "Estadio Ciudad de México", "Grupo A"),
        ("República de Corea", "República Checa", et_to_utc(2026, 6, 11, 22), "Estadio Guadalajara", "Grupo A"),

        # Viernes, 12 de junio 2026
        ("Canadá", "Bosnia y Herzegovina", et_to_utc(2026, 6, 12, 15), "Estadio Toronto", "Grupo B"),
        ("Estados Unidos", "Paraguay", et_to_utc(2026, 6, 12, 21), "Estadio Los Ángeles", "Grupo D"),

        # Sábado, 13 de junio 2026
        ("Catar", "Suiza", et_to_utc(2026, 6, 13, 15), "Estadio Bahía de San Francisco", "Grupo B"),
        ("Brasil", "Marruecos", et_to_utc(2026, 6, 13, 18), "Estadio Nueva York Nueva Jersey", "Grupo C"),
        ("Haití", "Escocia", et_to_utc(2026, 6, 13, 21), "Estadio Boston", "Grupo C"),
        ("Australia", "Turquía", et_to_utc(2026, 6, 14, 0), "Estadio BC Place Vancouver", "Grupo D"),

        # Domingo, 14 de junio 2026
        ("Alemania", "Curazao", et_to_utc(2026, 6, 14, 13), "Estadio Houston", "Grupo E"),
        ("Países Bajos", "Japón", et_to_utc(2026, 6, 14, 16), "Estadio Dallas", "Grupo F"),
        ("Costa de Marfil", "Ecuador", et_to_utc(2026, 6, 14, 19), "Estadio Filadelfia", "Grupo E"),
        ("Suecia", "Túnez", et_to_utc(2026, 6, 14, 22), "Estadio Monterrey", "Grupo F"),

        # Lunes, 15 de junio 2026
        ("España", "Cabo Verde", et_to_utc(2026, 6, 15, 12), "Estadio Atlanta", "Grupo H"),
        ("Bélgica", "Egipto", et_to_utc(2026, 6, 15, 15), "Estadio Seattle", "Grupo G"),
        ("Arabia Saudí", "Uruguay", et_to_utc(2026, 6, 15, 18), "Estadio Miami", "Grupo H"),
        ("RI de Irán", "Nueva Zelanda", et_to_utc(2026, 6, 15, 21), "Estadio Los Ángeles", "Grupo G"),

        # Martes, 16 de junio 2026
        ("Francia", "Senegal", et_to_utc(2026, 6, 16, 15), "Estadio Nueva York Nueva Jersey", "Grupo I"),
        ("Irak", "Noruega", et_to_utc(2026, 6, 16, 18), "Estadio Boston", "Grupo I"),
        ("Argentina", "Argelia", et_to_utc(2026, 6, 16, 21), "Estadio Kansas City", "Grupo J"),
        ("Austria", "Jordania", et_to_utc(2026, 6, 17, 0), "Estadio Bahía de San Francisco", "Grupo J"),

        # Miércoles, 17 de junio 2026
        ("Portugal", "RD Congo", et_to_utc(2026, 6, 17, 13), "Estadio Houston", "Grupo K"),
        ("Inglaterra", "Croacia", et_to_utc(2026, 6, 17, 16), "Estadio Dallas", "Grupo L"),
        ("Ghana", "Panamá", et_to_utc(2026, 6, 17, 19), "Estadio Toronto", "Grupo L"),
        ("Uzbekistán", "Colombia", et_to_utc(2026, 6, 17, 22), "Estadio Ciudad de México", "Grupo K"),

        # Jueves, 18 de junio 2026
        ("República Checa", "Sudáfrica", et_to_utc(2026, 6, 18, 12), "Estadio Atlanta", "Grupo A"),
        ("Suiza", "Bosnia y Herzegovina", et_to_utc(2026, 6, 18, 15), "Estadio Los Ángeles", "Grupo B"),
        ("Canadá", "Catar", et_to_utc(2026, 6, 18, 18), "Estadio BC Place Vancouver", "Grupo B"),
        ("México", "República de Corea", et_to_utc(2026, 6, 18, 21), "Estadio Guadalajara", "Grupo A"),

        # Viernes, 19 de junio 2026
        ("Estados Unidos", "Australia", et_to_utc(2026, 6, 19, 15), "Estadio Seattle", "Grupo D"),
        ("Escocia", "Marruecos", et_to_utc(2026, 6, 19, 18), "Estadio Boston", "Grupo C"),
        ("Brasil", "Haití", et_to_utc(2026, 6, 19, 21), "Estadio Filadelfia", "Grupo C"),
        ("Turquía", "Paraguay", et_to_utc(2026, 6, 20, 0), "Estadio Bahía de San Francisco", "Grupo D"),

        # Sábado, 20 de junio 2026
        ("Países Bajos", "Suecia", et_to_utc(2026, 6, 20, 13), "Estadio Houston", "Grupo F"),
        ("Alemania", "Costa de Marfil", et_to_utc(2026, 6, 20, 16), "Estadio Toronto", "Grupo E"),
        ("Ecuador", "Curazao", et_to_utc(2026, 6, 20, 22), "Estadio Kansas City", "Grupo E"),
        ("Túnez", "Japón", et_to_utc(2026, 6, 21, 0), "Estadio Monterrey", "Grupo F"),

        # Domingo, 21 de junio 2026
        ("España", "Arabia Saudí", et_to_utc(2026, 6, 21, 12), "Estadio Atlanta", "Grupo H"),
        ("Bélgica", "Irán", et_to_utc(2026, 6, 21, 15), "Estadio Los Ángeles", "Grupo G"),
        ("Uruguay", "Cabo Verde", et_to_utc(2026, 6, 21, 18), "Estadio Miami", "Grupo H"),
        ("Nueva Zelanda", "Egipto", et_to_utc(2026, 6, 21, 21), "Estadio BC Place Vancouver", "Grupo G"),

        # Lunes, 22 de junio 2026
        ("Argentina", "Austria", et_to_utc(2026, 6, 22, 13), "Estadio Dallas", "Grupo J"),
        ("Francia", "Irak", et_to_utc(2026, 6, 22, 17), "Estadio Filadelfia", "Grupo I"),
        ("Noruega", "Senegal", et_to_utc(2026, 6, 22, 20), "Estadio Nueva York Nueva Jersey", "Grupo I"),
        ("Jordania", "Argelia", et_to_utc(2026, 6, 22, 23), "Estadio Bahía de San Francisco", "Grupo J"),

        # Martes, 23 de junio 2026
        ("Portugal", "Uzbekistán", et_to_utc(2026, 6, 23, 13), "Estadio Houston", "Grupo K"),
        ("Inglaterra", "Ghana", et_to_utc(2026, 6, 23, 16), "Estadio Boston", "Grupo L"),
        ("Panamá", "Croacia", et_to_utc(2026, 6, 23, 19), "Estadio Toronto", "Grupo L"),
        ("Colombia", "RD Congo", et_to_utc(2026, 6, 23, 22), "Estadio Guadalajara", "Grupo K"),

        # Miércoles, 24 de junio 2026
        ("Suiza", "Canadá", et_to_utc(2026, 6, 24, 15), "Estadio BC Place Vancouver", "Grupo B"),
        ("Bosnia y Herzegovina", "Catar", et_to_utc(2026, 6, 24, 15), "Estadio Seattle", "Grupo B"),
        ("Escocia", "Brasil", et_to_utc(2026, 6, 24, 18), "Estadio Miami", "Grupo C"),
        ("Marruecos", "Haití", et_to_utc(2026, 6, 24, 18), "Estadio Atlanta", "Grupo C"),
        ("República Checa", "México", et_to_utc(2026, 6, 24, 21), "Estadio Ciudad de México", "Grupo A"),
        ("Sudáfrica", "República de Corea", et_to_utc(2026, 6, 24, 21), "Estadio Monterrey", "Grupo A"),

        # Jueves, 25 de junio 2026
        ("Curazao", "Costa de Marfil", et_to_utc(2026, 6, 25, 16), "Estadio Filadelfia", "Grupo E"),
        ("Ecuador", "Alemania", et_to_utc(2026, 6, 25, 16), "Estadio Nueva York Nueva Jersey", "Grupo E"),
        ("Japón", "Suecia", et_to_utc(2026, 6, 25, 19), "Estadio Dallas", "Grupo F"),
        ("Túnez", "Países Bajos", et_to_utc(2026, 6, 25, 19), "Estadio Kansas City", "Grupo F"),
        ("Turquía", "Estados Unidos", et_to_utc(2026, 6, 25, 22), "Estadio Los Ángeles", "Grupo D"),
        ("Paraguay", "Australia", et_to_utc(2026, 6, 25, 22), "Estadio Bahía de San Francisco", "Grupo D"),

        # Viernes, 26 de junio 2026
        ("Noruega", "Francia", et_to_utc(2026, 6, 26, 15), "Estadio Boston", "Grupo I"),
        ("Senegal", "Irak", et_to_utc(2026, 6, 26, 15), "Estadio Toronto", "Grupo I"),
        ("Cabo Verde", "Arabia Saudí", et_to_utc(2026, 6, 26, 20), "Estadio Houston", "Grupo H"),
        ("Uruguay", "España", et_to_utc(2026, 6, 26, 20), "Estadio Guadalajara", "Grupo H"),
        ("Egipto", "Irán", et_to_utc(2026, 6, 26, 23), "Estadio Seattle", "Grupo G"),
        ("Nueva Zelanda", "Bélgica", et_to_utc(2026, 6, 26, 23), "Estadio BC Place Vancouver", "Grupo G"),

        # Sábado, 27 de junio 2026
        ("Panamá", "Inglaterra", et_to_utc(2026, 6, 27, 17), "Estadio Nueva York Nueva Jersey", "Grupo L"),
        ("Croacia", "Ghana", et_to_utc(2026, 6, 27, 17), "Estadio Filadelfia", "Grupo L"),
        ("Colombia", "Portugal", et_to_utc(2026, 6, 27, 19, 30), "Estadio Miami", "Grupo K"),
        ("RD Congo", "Uzbekistán", et_to_utc(2026, 6, 27, 19, 30), "Estadio Atlanta", "Grupo K"),
        ("Argelia", "Austria", et_to_utc(2026, 6, 27, 22), "Estadio Kansas City", "Grupo J"),
        ("Jordania", "Argentina", et_to_utc(2026, 6, 27, 22), "Estadio Dallas", "Grupo J"),
    ]

    cur.executemany(
        """
        INSERT INTO matches(home_team, away_team, match_datetime, stadium, stage, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        [(h, a, dt, stadium, stage, now) for h, a, dt, stadium, stage in matches],
    )

    conn.commit()