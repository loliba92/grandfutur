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
# 2026-09-11 (Eau favorisée — Vénus en Scorpion ET Mars en Cancer,
# deux planètes d'Eau en même temps —, Feu freiné (aucune planète n'y
# est aujourd'hui), Terre et Air neutres — Lune en Vierge, Mercure en
# Balance). À la prochaine édition avec une configuration différente, ces
# phrases seront réécrites à nouveau — pas de valeur par défaut : mieux
# vaut un rappel explicite ("Bloc introuvable") que de laisser une vibe
# de la veille en place.
VIBES = {
    "belier": "Mars, ta planète maîtresse, reste en Cancer aujourd'hui : ton énergie habituelle doit passer par la ruse plutôt que par la charge frontale, surtout si un sujet d'argent traîne depuis quelques jours. Le corps demande aussi plus de ménagement que d'habitude — une séance plus courte qu'à l'accoutumée ne sera pas du temps perdu.",
    "taureau": "Vénus, ta planète maîtresse, brille dans le Scorpion aujourd'hui sans rien t'apporter directement : la Terre reste dans un entre-deux stable, ni portée ni freinée. Le quotidien tourne normalement — une tâche répétitive avancera sans accroc si tu t'y tiens.",
    "gemeaux": "Mercure, ta planète maîtresse, traverse la Balance aujourd'hui : les échanges gagnent en diplomatie sans que ça bouscule grand-chose. Une conversation délicate peut se dérouler mieux que prévu si tu restes dans la nuance plutôt que dans la répartie facile.",
    "cancer": "Mars occupe ton signe aujourd'hui, ce qui aiguise ton sens pratique et ta capacité à protéger ce qui compte : une initiative professionnelle a de bonnes chances d'aboutir si tu la lances maintenant. Le corps répond bien aussi, à condition de canaliser cette énergie plutôt que de la laisser déborder en agacement.",
    "lion": "Sans planète de Feu pour te porter aujourd'hui, ton énergie habituelle tourne un peu au ralenti — rien d'inquiétant, juste de quoi ajuster le rythme. Une remarque un peu vive peut vite déraper en dispute si tu ne la retiens pas, mieux vaut compter jusqu'à dix avant de répondre.",
    "vierge": "Mercure, ta planète maîtresse, traverse la Balance aujourd'hui, un signe sociable qui te pousse à soigner tes formulations plutôt qu'à foncer droit au but. La Terre reste neutre, donc rien d'exceptionnel à attendre — un rendez-vous ordinaire se passera simplement bien.",
    "balance": "Vénus, ta planète maîtresse, traverse le Scorpion aujourd'hui : tes sentiments gagnent en intensité sans que ça se voie forcément de l'extérieur. L'Air reste neutre, donc pas de grand bouleversement — une discussion à cœur ouvert avec un proche fera plus de bien qu'une sortie improvisée.",
    "scorpion": "Vénus traverse ton signe aujourd'hui, ce qui rend tes sentiments plus lisibles que d'habitude sans les rendre plus fragiles pour autant. Une conversation financière ou intime que tu repousses depuis un moment a de bonnes chances de bien se passer si tu la lances toi-même.",
    "sagittaire": "Le Feu manque de carburant aujourd'hui, ce qui se traduit surtout par une impatience plus grande que d'habitude face à ce qui n'avance pas assez vite à ton goût. Une décision financière importante gagne à attendre demain plutôt qu'à être tranchée sous le coup de l'agacement.",
    "capricorne": "La Terre reste dans un entre-deux stable aujourd'hui, sans planète pour la porter ni la freiner particulièrement : une bonne journée pour avancer sur un dossier de fond sans attendre de reconnaissance immédiate. Le corps suit sans excès ni fatigue notable.",
    "verseau": "Une journée neutre côté ciel pour toi aujourd'hui, ce qui laisse le champ libre à tes propres priorités plutôt qu'à celles des autres. Un projet perso avance mieux en solo qu'en groupe, pas la peine de forcer une réunion qui peut attendre.",
    "poissons": "Comme les autres signes d'Eau, tu profites aujourd'hui de la présence de Vénus en Scorpion et de Mars en Cancer : ton intuition est plus fiable que ton mental pour trancher une question en suspens. Une décision financière qui te trottait dans la tête peut enfin se prendre, sans devoir tout justifier par la logique.",
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
