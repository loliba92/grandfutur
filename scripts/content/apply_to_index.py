"""
Applique les données générées (day_code + fragments, via generate_signs.py)
à index.html : met à jour, pour les 12 signes, le data-energy, la jauge
d'énergie, et les 4 catégories notées (score + texte). Les vibes de tête
(sign-vibe) sont réécrites à la main pour rester cohérentes avec la
nouvelle situation réelle du jour (voir NEW_VIBES ci-dessous) — c'est la
seule partie encore non mécanisée de ce premier passage ; Style du jour
et Conseil restent inchangés.

Usage : python3 apply_to_index.py 2026-09-07 /home/user/grandfutur/index.html
"""
import re
import sys

from generate_signs import generate, DOMAINS

def score_color(score):
    if score < 50:
        return "var(--score-low)"
    if score <= 80:
        return "var(--score-mid)"
    return "var(--score-high)"


# Vibes réécrites pour rester honnêtes avec le vrai code du jour du
# 2026-09-07 (Eau favorisée, Feu freiné, Terre/Air neutres). À la prochaine
# édition avec une configuration différente, ces phrases seront réécrites
# à nouveau (ou, plus tard, elles aussi tirées d'une bibliothèque par
# situation — hors scope de ce premier passage).
NEW_VIBES = {
    "belier": "Ton élan habituel est en retrait aujourd'hui — pas de quoi s'inquiéter, mais ce n'est pas le jour pour forcer un mouvement qui te coûterait d'habitude bien moins d'énergie.",
    "cancer": "Ton instinct est plus fiable que d'habitude aujourd'hui : ce que tu ressens chez les autres mérite d'être pris au sérieux, pas balayé.",
    "lion": "Ta présence prend moins de place que d'habitude aujourd'hui, et ce n'est pas une mauvaise chose : observer vaut mieux que forcer une entrée en scène.",
    "balance": "Une question en suspens depuis un moment peut avancer aujourd'hui, sans qu'il soit besoin de tout trancher d'un coup.",
    "sagittaire": "L'envie d'imprévu est toujours là, mais l'élan pour la suivre manque un peu aujourd'hui — note l'idée, tu la reprendras avec plus de force dans quelques jours.",
    "capricorne": "Un rythme stable te convient aujourd'hui : avance pas à pas sur un dossier de fond, sans attendre de résultat immédiat.",
    "poissons": "Ton instinct est particulièrement fiable aujourd'hui : ce qu'il te souffle mérite d'être suivi, même sans toutes les preuves à l'appui.",
}


def patch_sign_block(html, sign, data, vibe_text):
    # Isole le bloc <article ... data-sign="SIGN" ...> ... </article>
    block_re = re.compile(
        r'(<article class="sign-card" data-sign="' + sign + r'"[^>]*>)(.*?)(</article>)',
        re.S,
    )
    m = block_re.search(html)
    if not m:
        raise SystemExit(f"Bloc introuvable pour {sign}")
    open_tag, body, close_tag = m.group(1), m.group(2), m.group(3)

    # data-energy sur la balise <article>
    open_tag = re.sub(r'data-energy="\d+"', f'data-energy="{data["energy"]}"', open_tag)

    # Jauge d'énergie globale
    energy_color = score_color(data["energy"])
    body = re.sub(
        r'<div class="energy-ring" style="--pct:\d+; --ring-color:[^;]+; margin-left:auto;"><div class="energy-ring-inner"><span class="energy-ring-value">\d+%</span>',
        f'<div class="energy-ring" style="--pct:{data["energy"]}; --ring-color:{energy_color}; margin-left:auto;"><div class="energy-ring-inner"><span class="energy-ring-value">{data["energy"]}%</span>',
        body,
    )

    # Vibe (si une nouvelle version est fournie)
    if vibe_text:
        body = re.sub(
            r'(<p class="sign-vibe">).*?(</p>)',
            lambda mo: mo.group(1) + vibe_text + mo.group(2),
            body,
            count=1,
        )

    # Les 4 catégories, dans l'ordre où generate_signs.py les produit
    # (même ordre que DOMAINS), en remplaçant chaque bloc sign-cat
    # successivement.
    cat_re = re.compile(
        r'(<div class="sign-cat">\s*<span class="sign-cat-label">)[^<]+(</span>\s*<div class="sign-cat-body">\s*'
        r'<div class="stat" style="--accent: )[^;]+(;">\s*<span class="stat-value">)\d+%(</span><span class="stat-bar"><span class="stat-bar-fill" style="width:)\d+(%;"></span></span></div>\s*'
        r'<p class="sign-cat-text">)[^<]+(</p>)',
        re.S,
    )

    cats = iter(data["categories"])

    def repl_cat(mo):
        c = next(cats)
        color = score_color(c["score"])
        return (
            mo.group(1) + c["label"] + mo.group(2) + color + mo.group(3)
            + f'{c["score"]}%' + mo.group(4) + str(c["score"]) + mo.group(5)
            + c["text"] + mo.group(6)
        )

    body = cat_re.sub(repl_cat, body)

    return html[: m.start()] + open_tag + body + close_tag + html[m.end():]


def main():
    date_str = sys.argv[1]
    index_path = sys.argv[2]
    result = generate(date_str)

    with open(index_path, encoding="utf-8") as f:
        html = f.read()

    for sign, data in result["signs"].items():
        html = patch_sign_block(html, sign, data, NEW_VIBES.get(sign))

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

    print("OK — 12 signes mis à jour pour", date_str)
    for sign, data in result["signs"].items():
        print(f"  {sign}: {data['situation']} energy={data['energy']}")


if __name__ == "__main__":
    main()
