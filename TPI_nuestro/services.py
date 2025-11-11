# services.py
from models import SessionLocal, Score
from datetime import datetime

def save_score(name, score):
    session = SessionLocal()
    try:
        new_score = Score(name=name.strip()[:30], score=int(score), created_at=datetime.now())
        session.add(new_score)
        session.commit()
    finally:
        session.close()

def get_top(limit=20):
    session = SessionLocal()
    try:
        rows = (
            session.query(Score.name, Score.score, Score.created_at)
            .order_by(Score.score.desc(), Score.created_at.asc())
            .limit(limit)
            .all()
        )
        return [(r[0], r[1], r[2].strftime("%d/%m/%Y %H:%M:%S")) for r in rows]
    finally:
        session.close()
