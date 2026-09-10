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
# 2026-09-10 (Terre favorisée — Lune ET Mercure en Vierge, double
# transit —, Feu freiné, Air et Eau neutres — Vénus en Balance, Mars en
# Cancer). À la prochaine édition avec une configuration différente, ces
# phrases seront réécrites à nouveau — pas de valeur par défaut : mieux
# vaut un rappel explicite ("Bloc introuvable") que de laisser une vibe
# de la veille en place.
VIBES = {
    "belier": "Mars, ta planète maîtresse, est en Cancer aujourd'hui : ton élan habituel doit ruser plutôt que foncer, et une question financière en suspens gagne à attendre un jour plus favorable. Écoute ton corps avant de le pousser encore, le mental tourne déjà à plein régime.",
    "taureau": "La Lune et Mercure traversent Vierge, un signe de Terre comme le tien : le terrain est particulièrement stable aujourd'hui, et ça se voit jusque dans ta présence, qui attire sans effort. Le corps suit bien aussi — une activité physique un peu plus longue que d'habitude passera comme une lettre à la poste.",
    "gemeaux": "L'Air reste neutre aujourd'hui pendant que Vénus le traverse en Balance : de quoi apporter un peu de grâce sociale sans rien bousculer côté cœur. L'irritabilité guette néanmoins, alors relis deux fois un message avant de l'envoyer.",
    "cancer": "Mars occupe ton signe aujourd'hui, ce qui aiguise ton sens pratique : un contact professionnel peut débloquer quelque chose si tu prends l'initiative plutôt que d'attendre. Le reste de la journée reste stable, sans pic ni creux particulier.",
    "lion": "Le Feu est freiné aujourd'hui, et ça se traduit surtout par moins de patience que d'habitude : le silence vaut parfois mieux qu'une phrase de trop, en amour comme en négociation. Pas la journée pour repousser tes limites physiques, même pour une bonne raison.",
    "vierge": "La Lune et Mercure occupent ton signe en même temps aujourd'hui, un double transit qui se sent nettement : une conversation que tu repousses depuis des jours peut enfin bien se passer. Belle énergie physique aussi — une activité qui te plaît vraiment en profitera pleinement.",
    "balance": "Vénus, ta planète maîtresse, traverse ton propre signe aujourd'hui sans rien bousculer de spectaculaire : tes efforts ne se voient pas encore, mais ils comptent. L'irritabilité guette en fin de journée, mieux vaut le savoir avant qu'un mot de trop parte.",
    "scorpion": "Ta lucidité financière est particulièrement nette aujourd'hui : un contact professionnel peut débloquer quelque chose si tu prends l'initiative. Côté cœur, rien de marquant, ce qui te laisse justement de la place pour le reste.",
    "sagittaire": "Le Feu est freiné aujourd'hui : le mental tourne à plein régime, pense à lever les yeux de l'écran de temps en temps. Une décision financière importante peut attendre un jour plus favorable, la patience paiera plus que la précipitation.",
    "capricorne": "Comme les deux autres signes de Terre, tu profites du double passage de la Lune et Mercure en Vierge aujourd'hui : dis ce que tu ressens plutôt que d'attendre que l'autre le devine, l'accueil sera bon. Curieux·se et bavard·e, les échanges te font du bien, et le corps suit sans effort.",
    "verseau": "Une journée neutre côté ciel, ce qui te laisse de la place pour tes propres idées plutôt que de suivre le mouvement. Sensible et tourné·e vers l'intérieur en fin de journée, inutile de te forcer à être sociable si l'envie n'y est pas.",
    "poissons": "Comme les autres signes d'Eau, tu vois plus clair que d'habitude sur un sujet financier : défends ta position dans une négociation, ton argumentaire tient la route aujourd'hui. Ce qui est solide dans ta vie n'a pas besoin d'être prouvé une fois de plus.",
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
