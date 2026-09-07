"""
Applique les données générées (day_code + fragments, via generate_signs.py)
à index.html : met à jour, pour les 12 signes, le data-energy, la jauge
d'énergie, et les 4 catégories notées (score + texte). Style du jour et
Conseil ("boiteux, aucun lien" — retour utilisateur du 7 septembre : texte
fixe par signe, jamais raccord à la situation réelle du jour) ont été
retirés définitivement, voir ARCHITECTURE.md § Historique.

Le paragraphe "vibe" (résumé en une phrase, .sign-vibe, affiché sous la
jauge d'Énergie de chaque carte famille) reste réécrit à la main pour
rester cohérent avec la vraie situation du jour (voir VIBES ci-dessous) —
c'est la seule partie encore non mécanisée de ce premier passage.

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
# à nouveau — pas de valeur par défaut : mieux vaut un rappel explicite
# ("Bloc introuvable") que de laisser une vibe de la veille en place.
VIBES = {
    "belier": "Ton élan habituel est en retrait aujourd'hui — pas de quoi s'inquiéter, mais ce n'est pas le jour pour forcer un mouvement qui te coûterait d'habitude bien moins d'énergie. Laisse venir plutôt que de pousser, surtout sur un dossier qui traîne depuis un moment.",
    "taureau": "Rien de spectaculaire en vue aujourd'hui, et c'est tant mieux : ce calme sert un travail de fond qui paiera plus tard. Une tâche répétitive avancera plus vite que prévu si tu t'y tiens sans chercher de raccourci.",
    "gemeaux": "Les mots viennent facilement aujourd'hui : bon moment pour rappeler quelqu'un que tu as un peu laissé de côté. Une conversation en tête-à-tête portera plus loin qu'un message groupé.",
    "cancer": "Ton instinct est plus fiable que d'habitude aujourd'hui : ce que tu ressens chez les autres mérite d'être pris au sérieux, pas balayé. Une décision qui traînait peut enfin se prendre, presque sans effort.",
    "lion": "Ta présence prend moins de place que d'habitude aujourd'hui, et ce n'est pas une mauvaise chose : observer vaut mieux que forcer une entrée en scène. Un projet personnel avance mieux mené en silence qu'annoncé trop tôt.",
    "vierge": "Ranger un coin de ta vie, au sens propre ou au figuré, va te libérer plus d'énergie que prévu. Une petite mise à jour vaut mieux qu'une remise à plat complète aujourd'hui.",
    "balance": "Une question en suspens depuis un moment peut avancer aujourd'hui, sans qu'il soit besoin de tout trancher d'un coup. Un compromis simple suffira, pas besoin de la solution parfaite.",
    "scorpion": "Ta lucidité est plus aiguisée que d'habitude, inutile de la garder seulement pour toi aujourd'hui. Ce que tu perçois sous la surface d'une situation mérite d'être dit, avec tact.",
    "sagittaire": "L'envie d'imprévu est toujours là, mais l'élan pour la suivre manque un peu aujourd'hui — note l'idée, tu la reprendras avec plus de force dans quelques jours. Un plan modeste tenu jusqu'au bout vaut mieux qu'un grand projet lancé à moitié.",
    "capricorne": "Un rythme stable te convient aujourd'hui : avance pas à pas sur un dossier de fond, sans attendre de résultat immédiat. Un objectif à long terme se rapproche, même si rien ne le montre encore.",
    "verseau": "Ta différence surprend d'abord, puis finit par convaincre ceux qui t'écoutent jusqu'au bout. Une idée qui sort du cadre trouvera son public si tu prends le temps de l'expliquer.",
    "poissons": "Ton instinct est particulièrement fiable aujourd'hui : ce qu'il te souffle mérite d'être suivi, même sans toutes les preuves à l'appui. Un moment de calme, même court, suffira à remettre tes idées en ordre.",
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
    # successivement. data-situation exposé sur la balise : lu par le JS
    # (readCardData) pour re-piocher une phrase personnalisée par décan
    # dans la carte famille, sans avoir à recalculer le code du jour
    # côté client (voir ARCHITECTURE.md § Décan et quotidien).
    # [^>]* entre le groupe 1 et le groupe 2 : tolère un data-situation
    # déjà présent d'une exécution précédente (sinon le regex ne matche
    # plus du tout à la 2e régénération, et les catégories ne sont plus
    # remplacées — bug rencontré et corrigé le 7 septembre, silencieux :
    # aucune erreur, juste l'ancien texte qui reste affiché).
    cat_re = re.compile(
        r'(<div class="sign-cat")[^>]*(>\s*<span class="sign-cat-label">)[^<]+(</span>\s*<div class="sign-cat-body">\s*'
        r'<div class="stat" style="--accent: )[^;]+(;">\s*<span class="stat-value">)\d+%(</span><span class="stat-bar"><span class="stat-bar-fill" style="width:)\d+(%;"></span></span></div>\s*'
        r'<p class="sign-cat-text">)[^<]+(</p>)',
        re.S,
    )

    cats = iter(data["categories"])

    def repl_cat(mo):
        c = next(cats)
        color = score_color(c["score"])
        situation_attr = ' data-situation="' + c["situation"] + '"' if c.get("situation") else ''
        return (
            mo.group(1) + situation_attr + mo.group(2) + c["label"] + mo.group(3) + color + mo.group(4)
            + f'{c["score"]}%' + mo.group(5) + str(c["score"]) + mo.group(6)
            + c["text"] + mo.group(7)
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
        html = patch_sign_block(html, sign, data, VIBES.get(sign))

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

    print("OK — 12 signes mis à jour pour", date_str)
    for sign, data in result["signs"].items():
        print(f"  {sign}: {data['situation']} energy={data['energy']}")


if __name__ == "__main__":
    main()
