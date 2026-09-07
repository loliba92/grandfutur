"""
Assemble le contenu des 4 domaines notés (Amour, Argent & travail, Santé,
Humeur) pour les 12 signes d'un jour donné, à partir :
- du code du jour (day_code.py — vraies positions planétaires) ;
- de la bibliothèque de phrases (fragments.py).

La sélection est déterministe (hash stable de date+signe+domaine), pas
aléatoire : relancer le script pour la même date donne toujours le même
résultat, ce qui est indispensable pour que "Copier l'horoscope" et la
page affichée disent la même chose, et pour que régénérer l'archive d'un
jour passé ne la change pas.

Usage :
    python3 generate_signs.py 2026-09-07
"""
import sys
import json
import hashlib

from day_code import compute_day_code, ZODIAC_ORDER, ELEMENT_OF
from fragments import FRAGMENTS, BASE_SCORE

DOMAINS = ["Amour", "Argent & travail", "Santé", "Humeur"]


def stable_int(key):
    return int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16)


def pick_and_score(date_str, sign, domain, situation):
    bucket = FRAGMENTS[domain][situation]
    idx = stable_int(f"{date_str}|{sign}|{domain}|pick") % len(bucket)
    jitter = (stable_int(f"{date_str}|{sign}|{domain}|jitter") % 13) - 6  # -6..+6
    score = max(0, min(100, BASE_SCORE[situation] + jitter))
    return bucket[idx], score


def generate(date_str):
    day_code = compute_day_code(date_str)
    signs_out = {}
    for sign in ZODIAC_ORDER:
        element = ELEMENT_OF[sign]
        # Situation générale du signe (toutes planètes confondues) : sert
        # au thème d'ensemble (paragraphe d'intro, phrase "vibe"), pas au
        # choix des phrases par domaine — voir domain_elements plus bas,
        # chaque domaine a sa propre situation, pas forcément la même.
        situation = day_code["elements"][element]
        categories = []
        scores = []
        for domain in DOMAINS:
            domain_situation = day_code["domain_elements"][domain][element]
            text, score = pick_and_score(date_str, sign, domain, domain_situation)
            categories.append({
                "label": domain,
                "situation": domain_situation,
                "score": score,
                "text": text,
            })
            scores.append(score)
        energy = round(sum(scores) / len(scores))
        signs_out[sign] = {
            "element": element,
            "situation": situation,
            "energy": energy,
            "categories": categories,
        }
    return {"date": date_str, "day_code": day_code, "signs": signs_out}


if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    result = generate(date_arg)
    print(json.dumps(result, ensure_ascii=False, indent=2))
