"""
Calcule le "code du jour" : la position réelle de la Lune, de Mercure, de
Vénus et de Mars dans le zodiaque tropical, plus l'état rétrograde de
chacune. C'est du calcul astronomique pur (bibliothèque `ephem`, aucune
donnée externe à télécharger) — dans le même esprit que le calcul de
l'ascendant côté client : une vraie formule, pas une configuration
inventée à la main.

Le code du jour sert ensuite à déterminer, pour chaque signe et pour
chaque domaine (Amour, Argent & travail, Santé, Humeur), si son élément
est aujourd'hui "favorisé", "neutre" ou "freiné" — et donc quel panier de
phrases piocher dans fragments.py.

Chaque domaine n'est influencé que par les planètes qui le "gouvernent"
traditionnellement (DOMAIN_PLANETS), pas par les 4 à la fois — sinon
Mercure mal placé freinerait Amour et Santé exactement autant que
Argent & travail, ce qui n'a pas de sens (retour utilisateur du
7 septembre : « si Mercure influence mon humeur négativement, est-ce que
ce sera bien pris en compte dans la phrase Humeur ? » — la réponse était
non avant ce correctif, chaque domaine partageait le même verdict).

Usage :
    python3 day_code.py 2026-09-07
    python3 day_code.py            # date du jour
"""
import sys
import json
import math
import hashlib
from datetime import date

import ephem

ZODIAC_ORDER = [
    "belier", "taureau", "gemeaux", "cancer", "lion", "vierge",
    "balance", "scorpion", "sagittaire", "capricorne", "verseau", "poissons",
]
ELEMENT_OF = {
    "belier": "feu", "lion": "feu", "sagittaire": "feu",
    "taureau": "terre", "vierge": "terre", "capricorne": "terre",
    "gemeaux": "air", "balance": "air", "verseau": "air",
    "cancer": "eau", "scorpion": "eau", "poissons": "eau",
}

# Poids de chaque planète dans le calcul des éléments favorisés/freinés du
# jour : la Lune change de signe tous les ~2,5 jours (thème le plus
# "du jour"), Mars pousse à l'action, Mercure/Vénus sont plus posés.
PLANET_WEIGHT = {"lune": 2.0, "mars": 1.5, "mercure": 1.0, "venus": 1.0}

# Quelles planètes gouvernent quel domaine — attribution classique en
# astrologie (Vénus/amour, Mercure/communication, Mars/action, Lune/
# émotions et rythme du corps). Chaque domaine n'utilise que ses propres
# planètes pour son classement favorisé/neutre/freiné, jamais les 4 —
# c'est ce qui fait qu'une planète mal placée pèse vraiment plus sur son
# domaine que sur les autres, au lieu de peser pareil sur les 4 à la fois.
DOMAIN_PLANETS = {
    "Amour": ["venus", "lune"],
    "Argent": ["mercure", "mars"],
    "Santé": ["mars", "lune"],
    "Humeur": ["mercure", "lune"],
}


def _stable_pick(tied_elements, tie_key):
    """Choisit un élément parmi les ex-æquo, de façon stable (même clé ->
    même choix) plutôt que de toujours favoriser le premier du dict
    (feu) — sinon Feu gagnerait systématiquement les égalités."""
    if len(tied_elements) == 1:
        return tied_elements[0]
    idx = int(hashlib.md5(tie_key.encode("utf-8")).hexdigest(), 16) % len(tied_elements)
    return tied_elements[idx]


def rank_elements(weight, tie_key="rank"):
    """{élément: poids} -> {élément: favorise/neutre/freine}.

    Toujours UN SEUL élément favorisé et UN SEUL freiné, jamais plus —
    même en cas d'égalité à plusieurs (fréquent : dès qu'un domaine n'a
    qu'une ou deux planètes qui le gouvernent, la moitié des éléments
    peut se retrouver à 0). Sans cette règle, un jour où une planète
    domine peut freiner 3 signes sur 4 en même temps — vérifié et jugé
    trop dur le 7 septembre ("tu es sûr de tes % c'est super bas").
    Le reste (y compris les autres éléments à égalité) redevient neutre.
    """
    top_w = max(weight.values())
    bottom_w = min(weight.values())
    result = {el: "neutre" for el in weight}
    if top_w > bottom_w:
        top_candidates = [el for el, w in weight.items() if w == top_w]
        result[_stable_pick(top_candidates, tie_key + "|top")] = "favorise"
        bottom_candidates = [el for el, w in weight.items() if w == bottom_w]
        result[_stable_pick(bottom_candidates, tie_key + "|bottom")] = "freine"
    return result


def sign_of(lon_rad):
    deg = math.degrees(lon_rad) % 360
    return ZODIAC_ORDER[int(deg // 30)], deg


def is_retrograde(body_cls, d):
    """Rétrograde = la longitude écliptique diminue d'un jour sur l'autre."""
    p1 = body_cls()
    p1.compute(d)
    lon1 = math.degrees(ephem.Ecliptic(p1).lon) % 360
    p2 = body_cls()
    p2.compute(ephem.Date(d + 1))
    lon2 = math.degrees(ephem.Ecliptic(p2).lon) % 360
    delta = (lon2 - lon1 + 540) % 360 - 180
    return delta < 0


def compute_day_code(day_str=None):
    if day_str:
        y, m, dd = (int(x) for x in day_str.split("-"))
        d = ephem.Date(f"{y}/{m}/{dd} 12:00:00")  # midi UTC ~ après-midi Paris
    else:
        d = ephem.Date(ephem.now())

    bodies = {
        "lune": ephem.Moon,
        "mercure": ephem.Mercury,
        "venus": ephem.Venus,
        "mars": ephem.Mars,
    }

    planets = {}
    for name, cls in bodies.items():
        p = cls()
        p.compute(d)
        sign, deg = sign_of(ephem.Ecliptic(p).lon)
        planets[name] = {
            "signe": sign,
            "element": ELEMENT_OF[sign],
            "degre": round(deg, 2),
            "retrograde": is_retrograde(cls, d),
        }

    resolved_date = day_str or date.today().isoformat()

    # Poids cumulé de chaque élément aujourd'hui, toutes planètes
    # confondues — sert au thème général du jour (paragraphe d'intro),
    # pas au choix des phrases par domaine (voir domain_elements).
    weight = {"feu": 0.0, "terre": 0.0, "air": 0.0, "eau": 0.0}
    for name, info in planets.items():
        weight[info["element"]] += PLANET_WEIGHT[name]
    elements = rank_elements(weight, tie_key=resolved_date + "|global")

    # Même calcul, mais un jeu de poids séparé par domaine, restreint aux
    # planètes qui le gouvernent (DOMAIN_PLANETS) — c'est ce qui alimente
    # réellement fragments.py, domaine par domaine.
    domain_elements = {}
    for domain, ruling_planets in DOMAIN_PLANETS.items():
        dweight = {"feu": 0.0, "terre": 0.0, "air": 0.0, "eau": 0.0}
        for name in ruling_planets:
            dweight[planets[name]["element"]] += PLANET_WEIGHT[name]
        domain_elements[domain] = rank_elements(dweight, tie_key=resolved_date + "|" + domain)

    return {
        "date": resolved_date,
        "planetes": planets,
        "elements": elements,
        "domain_elements": domain_elements,
    }


if __name__ == "__main__":
    day_arg = sys.argv[1] if len(sys.argv) > 1 else None
    print(json.dumps(compute_day_code(day_arg), ensure_ascii=False, indent=2))
