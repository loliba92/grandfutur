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
# 2026-09-09 (Feu favorisé — Lune en Lion —, Terre freinée — Mercure en
# Vierge —, Air et Eau neutres — Vénus en Balance, Mars en Cancer). À la
# prochaine édition avec une configuration différente, ces phrases seront
# réécrites à nouveau — pas de valeur par défaut : mieux vaut un rappel
# explicite ("Bloc introuvable") que de laisser une vibe de la veille en
# place.
VIBES = {
    "belier": "Ton énergie repart plus vite que prévu aujourd'hui, portée par la Lune en Lion : bon moment pour attaquer le dossier que tu remets depuis lundi plutôt que d'attendre le suivant. Cette assurance se voit aussi côté cœur, où elle attire plus qu'elle n'intimide.",
    "taureau": "Mercure en Vierge alourdit un peu le mental aujourd'hui, sans rien enlever à ta stabilité de fond. Une tâche répétitive avance quand même, à condition de lever les yeux de l'écran de temps en temps.",
    "gemeaux": "Une journée sans grand relief, ni portée ni freinée par le ciel du jour : c'est le moment d'observer plutôt que de réagir, y compris dans une discussion qui pourrait s'envenimer. Relis deux fois un message avant de l'envoyer, l'inattention guette plus qu'un vrai désaccord.",
    "cancer": "Mars occupe ton signe aujourd'hui, ce qui aiguise ton sens pratique sur une question d'argent ou d'organisation en suspens. La même énergie tourne vite en fatigue mentale si tu ne la canalises pas : une discussion sensible attendra mieux demain qu'aujourd'hui.",
    "lion": "La Lune traverse ton signe aujourd'hui, et ça se sent : une conversation que tu retardais depuis des jours a de bonnes chances d'aboutir. Canalise ce trop-plein d'énergie dans un seul projet plutôt que de courir plusieurs lièvres à la fois.",
    "vierge": "Mercure occupe ton signe aujourd'hui, ce qui aiguise ton sens du détail au travail — la même précision peut se retourner contre toi si tu la tournes vers l'intérieur. Une petite tension s'installe : une vraie pause, pas un simple café, suffira à la désamorcer.",
    "balance": "Vénus traverse ton signe aujourd'hui sans bousculer grand-chose : une présence stable suffit, pas besoin de mettre en scène ce que tu ressens pour que ça compte. Côté argent, évite de promettre plus que tu ne pourras tenir dans les jours qui viennent.",
    "scorpion": "Ta lucidité financière ou pratique est particulièrement nette aujourd'hui : avance sur ce qui traîne, la clarté est là. Côté émotions en revanche, tu es un peu à fleur de peau — mieux vaut prévenir ton entourage qu'espérer que ça passe inaperçu.",
    "sagittaire": "L'énergie est à son maximum aujourd'hui, portée par une Lune complice en Lion : les échanges, au travail comme en famille, te font plus de bien que d'habitude. Reprends une habitude que tu avais laissée filer, le terrain est favorable.",
    "capricorne": "L'élan collectif du jour ne te porte pas particulièrement, et ce n'est pas un problème : ton rythme de fond n'a jamais eu besoin d'un coup de pouce astral pour avancer. Continue ce qui est déjà lancé plutôt que d'ouvrir un nouveau chantier, et évite de repousser tes limites physiques aujourd'hui.",
    "verseau": "Une journée neutre, presque silencieuse côté ciel, ce qui te laisse justement de la place pour tes propres idées. Une petite marche ou un rituel simple entretient ce que tu as construit ces derniers jours, sans qu'il soit besoin d'en faire plus.",
    "poissons": "Comme les autres signes d'Eau, tu vois plus clair que d'habitude sur un sujet pratique ou financier resté en suspens : profites-en pour trancher. L'irritabilité guette côté cœur, mieux vaut choisir tes mots que les laisser filer.",
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
