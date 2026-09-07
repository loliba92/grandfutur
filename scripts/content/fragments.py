"""
Bibliothèque de phrases réutilisables pour les 4 domaines notés (Amour,
Argent & travail, Santé, Humeur). Chaque domaine a 3 paniers — favorise /
neutre / freine — remplis une fois pour toutes ; generate_signs.py y
pioche une phrase par signe et par jour selon le code du jour
(day_code.py), au lieu qu'on les réécrive à la main chaque matin.

Écrire de nouvelles variantes dans un panier existant n'a aucun impact
sur le reste du système — c'est le principal intérêt de cette
architecture : l'investissement (écrire des phrases) est ponctuel, la
sélection quotidienne est gratuite et automatique.
"""

FRAGMENTS = {
    "Amour": {
        "favorise": [
            "Une occasion de te rapprocher de quelqu'un se présente — ne la laisse pas filer.",
            "Dis ce que tu ressens plutôt que d'attendre que l'autre le devine.",
            "Une conversation que tu repousses depuis des jours peut enfin se faire, et bien se passer.",
            "Ta présence attire sans que tu aies à forcer quoi que ce soit.",
            "Un geste simple aujourd'hui compte plus que tu ne le penses pour la personne en face.",
            "C'est le bon moment pour relancer quelqu'un que tu as un peu laissé de côté.",
        ],
        "neutre": [
            "Rien de marquant côté cœur aujourd'hui, ce qui te laisse de la place pour le reste.",
            "Une présence stable te suffit, pas besoin de grande scène.",
            "Tu avances sur ce terrain-là au même rythme que d'habitude.",
            "Pas de tension ni d'élan particulier — une journée ordinaire, ce qui n'est pas rien.",
            "Ce qui est solide le reste ; ce qui doit attendre peut attendre encore un peu.",
            "Tu n'as ni besoin de convaincre ni d'être convaincu·e aujourd'hui.",
        ],
        "freine": [
            "Une discussion sensible attendra demain — tu n'as pas l'énergie pour la mener sereinement.",
            "Évite de tirer des conclusions hâtives sur ce que quelqu'un vient de dire.",
            "Tu as moins de patience que d'habitude : le silence vaut parfois mieux qu'une phrase de trop.",
            "Ce n'est pas le jour pour trancher une question affective en suspens.",
            "Un malentendu peut vite prendre des proportions inutiles — vérifie avant de t'énerver.",
            "Garde tes distances si une conversation commence à tourner en rond.",
        ],
    },
    "Argent & travail": {
        "favorise": [
            "Défends ta position dans une négociation, ton argumentaire tient la route aujourd'hui.",
            "C'est le bon jour pour présenter un dossier que tu gardais pour toi.",
            "Une opportunité inattendue mérite d'être prise au sérieux, même si elle sort du cadre.",
            "Avance sur ce qui traîne : tu as la clarté qui te manquait ces derniers jours.",
            "Un contact professionnel peut débloquer quelque chose si tu prends l'initiative.",
            "Ton sens pratique évite une erreur que d'autres n'ont pas vue venir.",
        ],
        "neutre": [
            "Continue ce qui est déjà lancé plutôt que d'ouvrir un nouveau chantier aujourd'hui.",
            "Rien de spectaculaire, mais le travail de fond avance normalement.",
            "Une journée pour exécuter plus que pour décider.",
            "Tes efforts ne se voient pas encore, mais ils comptent.",
            "Reste concentré·e sur une seule chose plutôt que d'en commencer trois.",
            "Ni avancée ni recul notable — le terrain reste stable.",
        ],
        "freine": [
            "Reporte une négociation tendue si tu en as la possibilité aujourd'hui.",
            "Relis deux fois ce que tu es sur le point d'envoyer avant de cliquer.",
            "Peu d'énergie pour un rapport de force : observe plutôt que d'insister.",
            "Une décision financière importante peut attendre un jour plus favorable.",
            "Un imprévu risque de dérégler ton planning — garde une marge.",
            "Ce n'est pas le moment de promettre plus que tu ne peux tenir.",
        ],
    },
    "Santé": {
        "favorise": [
            "Belle énergie physique : une activité qui te plaît vraiment en profitera pleinement.",
            "Ton corps suit sans effort aujourd'hui, mets-le à contribution.",
            "Bon jour pour reprendre une habitude que tu avais laissée filer.",
            "Tu récupères plus vite que d'habitude, même après un effort soutenu.",
            "Ton énergie déborde un peu : canalise-la dans une seule activité plutôt que de la disperser.",
            "Le corps et la tête sont alignés aujourd'hui, rare et à savourer.",
        ],
        "neutre": [
            "Un rythme tranquille te convient très bien aujourd'hui.",
            "Rien à signaler côté santé, ce qui est déjà une bonne nouvelle.",
            "Ton énergie reste stable, sans pic ni creux particulier.",
            "Une petite marche suffira à entretenir ce que tu as construit ces derniers jours.",
            "Le corps demande de la régularité aujourd'hui plutôt que de l'intensité.",
            "Ni fatigue ni excès d'énergie — un jour d'équilibre.",
        ],
        "freine": [
            "Fatigue à prendre au sérieux aujourd'hui — ralentir n'est pas un échec.",
            "Le mental tourne à plein régime, pense à lever les yeux de l'écran de temps en temps.",
            "Le repos te fera plus de bien qu'une nouvelle activité aujourd'hui.",
            "Une petite tension s'accumule : un vrai temps de pause la désamorcera avant qu'elle ne s'installe.",
            "Écoute le signal que ton corps t'envoie plutôt que de le repousser à demain.",
            "Pas la journée pour repousser tes limites, même pour une bonne raison.",
        ],
    },
    "Humeur": {
        "favorise": [
            "Optimiste et en mouvement, tu donnes envie aux autres de suivre le rythme.",
            "Ta bonne humeur est communicative aujourd'hui — elle ouvre des portes sans que tu le cherches.",
            "Tu vois plus large que d'habitude, et ça te met de bonne humeur.",
            "Confiant·e, tu prends un peu plus de place que d'habitude, et ça te va bien.",
            "Curieux·se et bavard·e, les échanges te font du bien aujourd'hui.",
            "Une légèreté inhabituelle t'accompagne toute la journée.",
        ],
        "neutre": [
            "Calme et posé·e, sans excès dans un sens ou dans l'autre.",
            "Une humeur stable, ni portée par un événement ni plombée par un autre.",
            "Tu observes plus que tu ne réagis aujourd'hui, et ça te va.",
            "Rien ne vient perturber ton rythme habituel.",
            "Une journée en pilotage automatique, dans le bon sens du terme.",
            "Ni élan particulier ni contrariété — un jour neutre, tout simplement.",
        ],
        "freine": [
            "Un peu trop sévère envers toi-même aujourd'hui : desserre l'étau.",
            "Sensible, tourné·e vers l'intérieur — inutile de te forcer à être sociable.",
            "L'irritabilité guette : mieux vaut le savoir avant qu'un mot de trop parte.",
            "Fatigue mentale plus que physique — accorde-toi une vraie pause, pas juste une pause écran.",
            "Un peu à fleur de peau aujourd'hui : préviens ceux qui t'entourent si besoin.",
            "L'agacement monte vite pour peu de chose — repère-le avant qu'il ne prenne toute la place.",
        ],
    },
}

# Score de base par situation ; generate_signs.py ajoute une petite
# variation déterministe (par signe+jour) pour éviter que tous les signes
# "favorisés" du même jour affichent exactement le même chiffre.
BASE_SCORE = {"favorise": 82, "neutre": 62, "freine": 46}
