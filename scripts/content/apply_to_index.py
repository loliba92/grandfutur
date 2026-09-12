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
# 2026-09-12 (Air favorisé — Lune ET Mercure en Balance, deux planètes
# d'Air en même temps —, Terre freinée (aucune planète n'y est
# aujourd'hui), Feu et Eau neutres — Vénus en Scorpion, Mars en Cancer).
# À la prochaine édition avec une configuration différente, ces phrases
# seront réécrites à nouveau — pas de valeur par défaut : mieux vaut un
# rappel explicite ("Bloc introuvable") que de laisser une vibe de la
# veille en place.
VIBES = {
    "belier": "Mars, ta planète maîtresse, reste en Cancer aujourd'hui, loin de ton terrain habituel : le corps répond correctement mais sans excès, une séance de sport ordinaire suffira très bien. Un sujet d'argent en suspens n'a pas besoin d'être tranché aujourd'hui — le classer peut attendre demain sans rien perdre.",
    "taureau": "Vénus, ta planète maîtresse, brille dans le Scorpion sans rien t'apporter directement, et sans planète de Terre pour te porter aujourd'hui, ton élément reste freiné : une négociation professionnelle gagnerait à être reportée si tu en as la possibilité. Le corps demande à être ménagé plutôt que poussé, une pause dans l'après-midi vaut mieux qu'un rythme tenu d'une traite.",
    "gemeaux": "Mercure, ta planète maîtresse, traverse la Balance aux côtés de la Lune aujourd'hui, une configuration rare qui aiguise à la fois ton mental et ta justesse relationnelle. Une conversation professionnelle délicate a de bonnes chances de bien tourner si tu la lances toi-même plutôt que d'attendre qu'elle vienne à toi.",
    "cancer": "La Lune traverse la Balance aujourd'hui, un peu loin de ton élément habituel, mais Mars reste dans ton signe et continue d'aiguiser ton sens pratique : une initiative professionnelle lancée aujourd'hui a de bonnes chances d'aboutir. Le corps suit normalement, sans besoin de forcer le rythme.",
    "lion": "Sans planète de Feu pour te porter aujourd'hui, ton énergie habituelle tourne un peu au ralenti, ce qui n'empêche pas d'avancer, juste à un rythme plus posé. Une remarque un peu vive au bureau peut vite déraper en dispute si tu ne la retiens pas, mieux vaut la garder pour toi jusqu'à demain.",
    "vierge": "Mercure, ta planète maîtresse, traverse la Balance aujourd'hui aux côtés de la Lune, ce qui t'aide à soigner tes formulations, mais ton élément reste freiné faute de planète pour le porter : un dossier administratif avancera mieux si tu le fractionnes en petites étapes plutôt que de vouloir le boucler d'un coup. Le mental tourne vite, pense à lever les yeux de l'écran de temps en temps.",
    "balance": "Vénus, ta planète maîtresse, traverse le Scorpion aujourd'hui pendant que la Lune et Mercure occupent ton propre signe : une configuration rare qui te met en position de force, autant sur le plan du cœur que des mots. Une demande que tu portes depuis un moment a de bonnes chances d'être entendue si tu la formules aujourd'hui plutôt que de la garder pour toi.",
    "scorpion": "Vénus traverse ton signe aujourd'hui, ce qui rend tes sentiments plus lisibles que d'habitude, mais ton élément reste dans un entre-deux stable, ni porté ni freiné par le reste du ciel. Un rythme de travail habituel te convient très bien aujourd'hui, pas besoin d'en faire plus pour que ça avance.",
    "sagittaire": "Le Feu manque de carburant aujourd'hui, sans planète pour le porter, ce qui se traduit surtout par une impatience plus grande que d'habitude face à ce qui n'avance pas assez vite à ton goût. Une décision financière importante gagne à attendre demain plutôt qu'à être tranchée sous le coup de l'agacement.",
    "capricorne": "La Terre ne reçoit aucune planète aujourd'hui, ce qui te prive un peu de ton carburant habituel sans rien freiner de dramatique : un dossier de fond avancera normalement si tu ne cherches pas de reconnaissance immédiate. Le corps suit sans excès ni fatigue notable, une journée pour tenir le rythme plutôt que l'accélérer.",
    "verseau": "Lune et Mercure traversent la Balance aujourd'hui, un signe d'Air comme le tien, ce qui nourrit directement ton besoin d'échanger et de voir large. Un projet perso gagnera à être partagé aujourd'hui plutôt que gardé pour toi, les retours que tu recevras seront plus utiles que d'habitude.",
    "poissons": "Vénus en Scorpion et Mars en Cancer, deux planètes d'Eau comme toi, gardent ton élément dans un entre-deux stable — ni porté ni freiné. Une intuition sur un sujet financier mérite d'être notée aujourd'hui même si tu ne comptes pas agir tout de suite, elle pourrait se révéler juste dans quelques jours.",
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
