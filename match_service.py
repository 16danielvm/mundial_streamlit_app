from database import execute
from predictions import recalculate_match_points

def update_result(match_id, home_score, away_score):
    status = "Finalizado" if home_score is not None and away_score is not None else "Pendiente"
    execute(
        """
        UPDATE matches
        SET home_score = %s, away_score = %s, status = %s
        WHERE id = %s
        """,
        (home_score, away_score, status, match_id),
    )
    recalculate_match_points(match_id)