"""
Reconstitue l'historique des énergies par signe sur une plage de dates
passées, en rejouant le moteur de contenu (day_code.py + fragments.py)
jour par jour — pas une invention : le code du jour est un vrai calcul
astronomique, on peut donc le recalculer pour hier comme pour aujourd'hui.

Ce n'est PAS un historique de ce qui a été réellement publié (le site
n'a qu'une édition réelle, le 7 septembre 2026) : c'est le signal
astronomique réel recalculé rétroactivement, pour donner tout de suite
de la matière au futur graphique d'évolution par profil (docs/BACKLOG.md,
section P3), plutôt que d'attendre que la routine quotidienne accumule
les jours un par un.

Usage :
    python3 build_history.py [nb_jours] [date_fin AAAA-MM-JJ]
    python3 build_history.py 90            # 90 jours avant aujourd'hui
    python3 build_history.py 90 2026-09-07 # 90 jours avant cette date
"""
import sys
import json
import pathlib
import datetime

from generate_signs import generate, ZODIAC_ORDER

HISTORY_PATH = pathlib.Path(__file__).resolve().parent.parent.parent / "data" / "historique-energie.json"


def build(days, end_date_str=None):
    end_date = (
        datetime.date.fromisoformat(end_date_str)
        if end_date_str
        else datetime.date.today()
    )
    history = {}
    if HISTORY_PATH.exists():
        history = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))

    for i in range(days, -1, -1):
        day = end_date - datetime.timedelta(days=i)
        day_str = day.isoformat()
        result = generate(day_str)
        history[day_str] = {sign: result["signs"][sign]["energy"] for sign in ZODIAC_ORDER}

    HISTORY_PATH.write_text(
        json.dumps(dict(sorted(history.items())), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"OK — {days + 1} jours écrits dans {HISTORY_PATH} (jusqu'au {end_date.isoformat()})")


if __name__ == "__main__":
    n_days = int(sys.argv[1]) if len(sys.argv) > 1 else 90
    end = sys.argv[2] if len(sys.argv) > 2 else None
    build(n_days, end)
