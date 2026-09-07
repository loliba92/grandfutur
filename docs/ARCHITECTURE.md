# Architecture — Grand Futur

Vue d'ensemble technique du site. Même principe que Scénario
(`docs/ARCHITECTURE.md` de ce projet jumeau) : site statique, zéro
backend, hébergé gratuitement sur GitHub Pages.

## Aperçu

**Grand Futur** est un horoscope quotidien statique, publié via
**GitHub Pages**. Aucun backend, aucune base de données : tout est fait
de fichiers HTML/CSS/JS statiques. Chaque page est autonome (CSS et JS
inline), pour que les archives figées ne cassent jamais si le design
évolue plus tard — même règle que Scénario, à ne jamais factoriser.

**État au 7 septembre 2026 : v1 de démonstration.** Cette première
version prouve le concept avec une édition complète, mais le contenu du
jour (édito, énergie par signe, texte des 12 cartes) est **écrit à la
main pour la démo**, pas encore généré automatiquement chaque matin par
une routine planifiée — voir « Ce qui reste à faire » en bas de ce
fichier.

## Structure des fichiers

```
index.html                    L'édition du jour, écrasée chaque matin (une fois l'automatisation branchée).
archives.html                 Liste des éditions passées.
archives/AAAA-MM-JJ.html       Copie figée de chaque édition (chemins relatifs préfixés ../).
le-projet.html                Page « À propos ».
contact.html                  Formulaire de contact (FormSubmit).
mentions-legales.html         Éditeur, hébergeur, transparence IA.
politique-de-confidentialite.html  Données collectées, cookies AdSense, droits RGPD.
feed.xml / feed.json          Flux consommés par le workflow Make.com (Instagram/Facebook).
assets/logo.svg               Logo.
assets/topic-images/          Photo du jour (Pexels), carrée + recadrage large.
scripts/social/               Scripts Python de récupération d'image (voir plus bas).
```

## Le gabarit d'édition (`index.html`)

Ordre de lecture, retravaillé le 7 septembre (retour utilisateur : les
profils doivent être vus en premier, avant même le résumé du jour) :

1. **Masthead** — logo, wordmark, nav (Accueil / Archives / Le projet / Contact).
2. **Emplacement pub** — bandeau réservé pour Google AdSense (voir plus bas).
3. **Vos proches** — gestionnaire de profils, **en tout premier dans le
   corps de page** (voir plus bas) : c'est ce qu'un lecteur doit voir avant
   toute autre chose.
4. **Hero / résumé du jour** — photo plein écran type « couverture »
   (traitement repris de Scénario : dégradé sombre, logo en filigrane,
   titre incrusté en bas de l'image — voir `.article-image-*`), puis le
   texte d'intro. **Toujours ancré sur des éléments réels et nommés**
   (une planète, une position, une phase lunaire) reliés à une conséquence
   concrète — jamais une formule vague type « le ciel invite à... » qui ne
   dit rien de vérifiable ni d'actionnable. Retour utilisateur explicite le
   7 septembre : *"c'est creux, ça ne veut rien dire"* sur une première
   version trop lisse — règle à appliquer aussi le jour où la génération
   sera automatisée avec de vraies éphémérides.
5. **Les 12 signes, en damier** — une grille de 12 tuiles compactes
   (glyphe + nom, couleur d'élément), sans détail affiché. Cliquer sur une
   tuile affiche l'analyse complète du signe dans un panneau unique juste
   en dessous (`#sign-detail`) — un seul signe visible à la fois, basculé
   via l'attribut HTML natif `hidden` sur chaque `.sign-card` plutôt qu'une
   animation CSS complexe. **Remplace un essai précédent en accordéon**
   (chaque carte se dépliait sur place) — retour utilisateur du 7 septembre :
   préférence pour un damier de sélection + un panneau de détail unique,
   plus proche d'une interaction "choisir puis voir" que d'une longue liste
   à parcourir.
   Chaque carte de détail porte `data-sign`, `data-element` et
   `data-energy` (moyenne arrondie des 4 scores ci-dessous) — lue par le JS
   du gestionnaire de profils, **source unique de vérité** (pas de
   duplication du contenu du jour dans un objet JS séparé). Un clic sur
   « Voir le détail de son signe » depuis une carte famille sélectionne la
   bonne tuile puis scrolle vers le panneau.
   **Score par domaine** (retour utilisateur du 7 septembre, en plus de
   l'énergie globale) : chaque signe porte 4 sous-scores — Amour, Argent,
   Santé, Humeur — chacun avec un texte dédié. **L'énergie globale
   affichée est la moyenne arrondie de ces 4 scores**, jamais une 5e valeur
   inventée séparément : ça garantit la cohérence et simplifie la future
   génération automatique (la routine n'écrit que 4 chiffres, le total se
   déduit).
6. **Trio du jour** — top 3 énergie, `.list-box` (composant repris tel quel
   du gabarit Scénario).
7. **Lexique** — Signe, Ascendant, Élément.

## Gestionnaire de profils (« Vos proches »)

Fonctionnalité centrale demandée : pouvoir enregistrer plusieurs profils
(soi-même, conjoint·e, enfants...) et voir leur résultat du jour sans
ressaisir leurs informations à chaque visite.

- Stockage : `localStorage`, clé `grandfutur_profiles`, tableau de
  `{id, name, date, time}`. **Rien n'est jamais envoyé à un serveur.**
- Vue « famille » : tous les profils enregistrés affichés en grille dès
  l'arrivée sur la page (pas seulement un sélecteur un par un).
- Chaque carte famille calcule le signe solaire (à partir de la date) et
  l'ascendant (date + heure), puis va lire l'énergie/le texte du jour
  directement sur la carte `.sign-card` correspondante du DOM.
- Un lien « Voir le détail de son signe » fait défiler jusqu'à la carte
  complète et la met en surbrillance quelques secondes.

### Calcul de l'ascendant — méthode et limites

Formule géométrique standard (temps sidéral local de Greenwich + obliquité
moyenne de l'écliptique), implémentée en JS pur, sans dépendance externe :

1. Conversion de la date/heure saisie (supposée heure locale de Paris) en
   UTC, avec la règle de changement d'heure européenne (dernier dimanche
   de mars/octobre) codée en dur.
2. Jour julien (algorithme de Meeus).
3. Temps sidéral de Greenwich (GMST), puis temps sidéral local en ajoutant
   la longitude de Paris (2,3522°E).
4. Ascendant = `atan2(cos(RAMC), -(sin(RAMC)·cos(ε) + tan(lat)·sin(ε)))`,
   avec `ε` l'obliquité moyenne (23,4367°) et `lat` la latitude de Paris
   (48,8566°N).

**Limite assumée dès la v1 (décision prise en amont)** : latitude/longitude
**fixées sur Paris** pour tout le monde, pas de champ « lieu de
naissance ». Précis à quelques degrés près pour l'immense majorité des
lecteurs ; un lecteur né loin de la France métropolitaine aura un
ascendant légèrement moins précis. À revoir en v2 si le besoin se
confirme (ajout d'un champ ville/pays).

Vérifié : la vitesse de déplacement de l'ascendant dans le zodiaque n'est
**pas constante** au cours de la journée (plus rapide ou plus lente selon
la portion du ciel, un vrai phénomène d'ascension oblique aux latitudes
non équatoriales) — comportement attendu de la formule, pas un bug.

### L'ascendant doit se voir, pas juste se calculer

Défaut identifié par l'utilisateur (7/09) : le calcul d'ascendant était
correct, mais **invisible dans le résultat**. Deux personnes du même signe
solaire lisaient exactement le même horoscope — mêmes scores des 4
domaines, même texte — l'ascendant ne servait qu'à afficher un libellé et
une phrase générique partagée par les 3 signes du même élément.

Correctif :
- `ASCENDANT_FLAVOR` : une phrase par signe ascendant (12 variantes) au
  lieu d'une par élément (4 variantes).
- `ASCENDANT_NUDGE` + `applyAscendantNudge()` : l'élément de l'ascendant
  déplace de quelques points les 4 scores du signe solaire (ex. Feu :
  +4 Argent / -3 Santé ; Eau : +4 Amour / -2 Argent),
  bornés à [0, 100]. L'énergie globale de la carte famille est recalculée
  comme la moyenne de ces scores ajustés — elle n'est donc plus identique
  à celle affichée sur la carte générique du signe.
- Les mêmes valeurs ajustées alimentent le bouton « Copier »/« Partager »,
  pour que le texte exporté corresponde à ce qui est affiché.

Limite assumée : seuls les *chiffres* et une phrase varient avec
l'ascendant ; les paragraphes détaillés par domaine restent ceux du signe
solaire (rédiger 144 combinaisons signe × ascendant chaque jour à la main
n'est pas réaliste tant que l'automatisation quotidienne — voir Backlog
P1 — n'existe pas).

### Moteur de contenu (`scripts/content/`) — jour réel + bibliothèque de phrases

Problème plus profond, remonté par l'utilisateur le 7 septembre en
réaction au point précédent : réécrire les 12 textes à la main chaque
jour (ou, pire, générer 144 combinaisons uniques par IA chaque matin —
chiffré, cf. discussion, quelques dizaines de centimes à ~1 $/jour selon
le modèle, donc pas bloquant côté coût mais un mauvais choix
d'architecture) ne scale pas et ne garantit rien de cohérent. Le
paragraphe d'intro du 7 septembre inventait même une configuration
("Mars en Lion") qui ne correspondait à aucune réalité astronomique.

Solution retenue : séparer un **code du jour** (calculé, réel) d'une
**bibliothèque de phrases** (écrite une fois, réutilisée) reliés par une
**sélection déterministe** — le modèle des horoscopes syndiqués, pas une
génération IA à la volée.

Dépendance : `pip install ephem` (bibliothèque pure Python, aucune donnée
externe à télécharger — à installer dans l'environnement qui exécutera la
future routine quotidienne, P1).

1. **`day_code.py`** — calcule la position réelle de la Lune, Mercure,
   Vénus et Mars (signe + rétrograde) via la bibliothèque `ephem`
   (auto-suffisante, aucune donnée externe à télécharger), dans le même
   esprit que le calcul de l'ascendant côté client : une vraie formule,
   pas une configuration inventée. En déduit, par un score pondéré par
   planète (Lune ×2, Mars ×1.5, Mercure/Vénus ×1), quel élément est
   `favorise`/`neutre`/`freine` aujourd'hui.
2. **`fragments.py`** — pour chacun des 4 domaines notés (Amour,
   Argent, Santé, Humeur) × 3 situations (favorise/neutre/
   freine), 6 phrases écrites à la main, plus un score de base par
   situation (82/62/46). Écrire une variante de plus dans un panier
   existant n'impacte rien d'autre — c'est le seul travail d'écriture
   récurrent que ce système ne supprime pas, mais il devient ponctuel
   (étoffer la bibliothèque de temps en temps) au lieu de quotidien.
3. **`generate_signs.py`** — pour chaque signe, situation = état de son
   élément dans le code du jour ; choisit une phrase par domaine par un
   hash stable de `date + signe + domaine` (déterministe : la même date
   redonne toujours le même résultat, condition nécessaire pour que
   « Copier l'horoscope » et l'archive figée restent identiques dans le
   temps) ; score = score de base de la situation + petite variation
   elle aussi déterministe (±6).
4. **`apply_to_index.py`** — patch `index.html` : `data-energy`, jauge
   d'énergie et les 4 blocs `.sign-cat` (score + texte) des 12 signes.

Exemple concret (7 septembre, calculé) : Lune et Mars en Cancer → élément
Eau favorisé, Feu freiné, Terre/Air neutres — l'inverse de la
configuration inventée la veille. Le trio de tête est passé de
Sagittaire/Lion/Bélier à Scorpion/Poissons/Cancer.

**Ce qui n'est pas encore mécanisé** (limite assumée de ce premier
passage) : le paragraphe d'intro général et les 12 phrases "vibe" en tête
de chaque fiche signe sont encore réécrits à la main pour rester
cohérents avec le code du jour — de même pour "Style du jour" et
"Conseil", qui peuvent ponctuellement sonner un peu décalés par rapport à
la situation du jour (ex. un conseil pensé pour un jour calme affiché un
jour où le signe est en fait favorisé). Les mécaniser à leur tour (leur
propre bibliothèque par situation) est noté dans `BACKLOG.md`.

Cette architecture compose proprement avec le nudge d'ascendant
ci-dessus : le code du jour fixe la base par signe solaire, l'ascendant
la nuance ensuite — deux axes indépendants, aucun conflit.

### Chaque domaine a sa propre planète, pas les 4 à la fois

Défaut identifié par l'utilisateur (7/09) : « si Mercure influence mon
humeur négativement, est-ce que ce sera bien pris en compte dans la
phrase Humeur ? » Réponse honnête à l'époque : non. Le code du jour ne
calculait qu'un seul verdict par élément (toutes planètes confondues),
appliqué identiquement aux 4 domaines — Mercure mal placé freinait Amour
et Santé exactement autant que Argent & travail, aucun lien entre une
planète précise et son domaine.

Correctif : `DOMAIN_PLANETS` (`day_code.py`) attribue à chaque domaine
les planètes qui le gouvernent traditionnellement — Amour (Vénus, Lune),
Argent (Mercure, Mars), Santé (Mars, Lune), Humeur (Mercure,
Lune). `domain_elements` refait le même classement favorisé/neutre/freiné
que `elements`, mais un jeu de poids séparé par domaine, restreint à ses
seules planètes. `generate_signs.py` pioche désormais la situation de
chaque domaine dans `domain_elements[domaine]`, plus dans `elements`
(qui reste calculé, toutes planètes confondues — sert au thème général
du jour, paragraphe d'intro et phrase "vibe", pas au choix des phrases
par domaine).

Effet concret (7 septembre, avant/après) : le Taureau passait de
4 domaines "neutre" identiques (énergie 64) à Amour freiné / Argent &
travail neutre / Santé freiné / Humeur neutre (énergie 56) — quatre
lectures réellement différentes au lieu d'une seule recopiée 4 fois.
Historique (`data/historique-energie.json`) recalculé sur les 91 jours
avec le nouveau modèle.

### Décan — troisième axe, sans nouveau calcul en temps réel

Ajouté le 7 septembre, même logique de « code + bibliothèque de
fragments » que le reste : le décan (chaque signe divisé en 3 tranches
de ~10°, ~10 jours) ne dépend que de la date de naissance, jamais du
jour — contrairement à l'ascendant, pas besoin de recalculer quoi que ce
soit en temps réel, une table de dates statique suffit.

- **`DECAN_RANGES`** (36 entrées, JS) : bornes calculées à partir de la
  vraie position du Soleil (10° d'écart écliptique par décan, script
  ponctuel via `ephem`), pas d'une simple division en 3 du nombre de
  jours du signe — décalage possible de ±1 jour d'une année sur l'autre
  (précession négligeable à cette échelle), même tolérance que
  `SUN_SIGN_RANGES`.
- **`decanFromDate()`** : *pas* la même logique à 3 clauses OR que
  `sunSignFromDate()` — celle-ci suppose implicitement que `from.month
  != to.month`, ce qui n'est pas toujours vrai pour un décan (souvent
  contenu dans un seul mois, ex. Bélier 1er décan `[3,21]`-`[3,30]`).
  Bug rencontré et corrigé en test local (25 mars rendait "2e décan" au
  lieu de "1er") : comparaison numérique `mois*100+jour` à la place.
- **`decanRulerSign()`** : au lieu d'écrire 36 phrases à la main, la
  règle classique des décans est codée en formule — le 1er décan d'un
  signe est son expression "pure", le 2e et le 3e sont teintés par les
  deux autres signes du même élément (sa triplicité), dans l'ordre du
  zodiaque (`(index + (decan-1)*4) % 12`). Ex. Bélier : décan 1 =
  Bélier, décan 2 = Lion, décan 3 = Sagittaire.
- **`DECAN_COLOR_TRAIT`** : 12 traits réutilisables (un par signe), pas
  36 — combinés par `decanFlavor()` en "à la base de {signe} s'ajoute
  une touche de {signe teintant} — {trait}". 12 phrases produisent
  mécaniquement 36 combinaisons cohérentes, dans le même esprit que
  `ASCENDANT_NUDGE`/`ASCENDANT_FLAVOR` : un petit calcul plutôt qu'une
  bibliothèque proportionnelle au nombre de combinaisons.

**Décision assumée : pas de nudge de score pour le décan.** Contrairement
à l'ascendant, le décan reste purement informatif (libellé + phrase) —
cumuler un deuxième modificateur numérique sur les 4 scores rendrait le
système difficile à expliquer et à faire confiance ("pourquoi ce chiffre
précis ?"). Un axe de plus (l'ascendant) nuance déjà les chiffres ; le
décan nuance le texte. Affiché dans la carte famille : sous-titre
("Bélier (2e décan) · Ascendant Gémeaux") + une phrase dédiée, sous celle
de l'ascendant ; repris dans le texte "Copier"/"Partager".

### Décan et quotidien — le décan repioche le texte du jour, pas juste une phrase fixe

Retour utilisateur (7/09) : après avoir compris que le décan ne touche
aucun score et ne réagit pas au ciel du jour, sa contribution semblait
trop mince ("qu'apporte le décan alors ? comprends pas"). Trois options
posées, l'utilisateur choisit : garder le décan purement informatif
(inchangé) VS le retirer VS **le faire influencer le texte quotidien des
4 domaines, sans toucher aux scores** — retenue.

Mécanisme : chaque bloc `.sign-cat` de la fiche signe porte maintenant
un attribut `data-situation="favorise/neutre/freine"` (ajouté par
`apply_to_index.py`, lu depuis `categories[i].situation` de
`generate_signs.py`) — c'était déjà calculé côté Python, seulement pas
exposé au DOM jusqu'ici. Côté JS, `readCardData()` le récupère, et
`pickPersonalizedText(date, signe, décan, domaine, situation)` repioche,
**pour le profil**, une phrase dans le même panier `FRAGMENTS_DOMAINS`
que celui utilisé côté Python — mais avec le décan en plus dans la clé
de hash (`date|signe|décan|domaine|pick`), via un hash JS maison
(djb2, `stableHashJS`) plutôt qu'une réplique du MD5 Python : aucun
besoin de faire correspondre les deux algorithmes, la sélection
personnalisée n'a jamais à reproduire le texte générique de la fiche
signe, juste à être stable dans le temps.

Conséquence voulue : deux profils du même signe solaire, même situation
du jour, mais de décans différents, lisent maintenant un texte différent
pour un même domaine (vérifié : Bélier 1er décan vs 3e décan, même jour,
même ascendant → 3 des 4 domaines diffèrent, le 4e coïncide par hasard —
attendu avec un panier de 6). Les scores restent strictement identiques
(le décan ne les touche jamais, décision du paragraphe précédent
inchangée) — seul le texte varie. Le texte affiché sur la fiche signe
générique (le damier public des 12 signes) ne change pas : cette
repioche n'a lieu que pour une carte de profil, où un décan existe.

### Bibliothèque de phrases — un seul JSON, deux runtimes

Retour utilisateur (7/09) : les phrases (fragments par domaine/situation,
ASCENDANT_FLAVOR, DECAN_COLOR_TRAIT) étaient éparpillées entre
`scripts/content/fragments.py` (dict Python) et des objets JS codés en
dur dans `index.html` — deux syntaxes différentes pour le même genre de
contenu, aucun lien mécanique entre les deux.

**`data/fragments.json`** est maintenant l'unique source de vérité —
`{domains, base_score, ascendant_flavor, decan_color_trait}`. JSON est
nativement lisible par les deux runtimes du projet, sans script de
synchronisation ni étape de build :

- **Python** (`scripts/content/fragments.py`) : devenu un simple
  chargeur (`json.loads` du fichier), toujours exposé sous les mêmes
  noms `FRAGMENTS`/`BASE_SCORE` — `generate_signs.py` n'a rien eu à
  changer.
- **JS** (`index.html`) : `ASCENDANT_FLAVOR`/`DECAN_COLOR_TRAIT`
  démarrent comme des objets vides, peuplés par un `fetch("data/fragments.json")`
  avant le tout premier `render()` en fin de script. Les `render()`
  déclenchés ensuite par une interaction (ajout de profil, clic sur une
  puce) n'ont plus besoin d'attendre : les deux objets restent en mémoire
  pour le reste de la session.

**Piège de test local, à connaître** : `fetch()` d'un fichier local est
bloqué par le navigateur en `file://` (restriction CORS), alors que tout
le test en local de ce projet se fait via `file:///.../index.html`
(voir plus haut, limite du proxy réseau de l'environnement de session).
Depuis ce changement, tester la page nécessite un petit serveur HTTP
local : `python3 -m http.server` à la racine du dépôt, puis Playwright
sur `http://localhost:PORT/index.html` — jamais `file://` pour une page
qui fait un `fetch()`. En production (GitHub Pages), aucun problème :
c'est un vrai serveur HTTP.

### Historique des énergies — recalculé rétroactivement, pas inventé

`data/historique-energie.json` — une entrée par date :
```json
"AAAA-MM-JJ": {
  "energies": { "belier": 78, "taureau": 64, ... },
  "day_code": {
    "planetes": { "lune": {"signe": "cancer", "element": "eau", "degre": 116.75, "retrograde": false}, ... },
    "elements": { "feu": "freine", "terre": "neutre", "air": "neutre", "eau": "favorise" }
  }
}
```
`energies` nourrit le futur graphique d'évolution par profil
(`docs/BACKLOG.md` § P3, demandé le 7 septembre, débloqué le même jour
par ce fichier). `day_code` répond à un défaut relevé le même jour :
sans lui, aucun moyen de vérifier après coup *pourquoi* un signe
affichait tel chiffre à telle date — jusque-là le code du jour n'était
imprimé que dans un fichier temporaire pendant l'exécution de la
routine, puis jeté. Chaque énergie de l'historique est désormais
traçable jusqu'à la position réelle des planètes qui l'a produite.

**Point important à ne jamais perdre de vue** : ce n'est *pas* un journal
de ce qui a réellement été publié — le site n'a qu'une seule vraie
édition (7 septembre 2026). C'est le code du jour **recalculé
rétroactivement** avec `scripts/content/build_history.py`, pour chaque
date passée, exactement avec la même formule que pour aujourd'hui. Ce
n'est légitime que *parce que* le moteur est un vrai calcul astronomique
déterministe (position réelle des planètes à cette date) — recalculer
pour le 9 juin donne ce que la formule aurait produit ce jour-là, ni plus
ni moins vrai que pour aujourd'hui. Backfillé sur 91 jours (9 juin → 7
septembre) en une commande plutôt que d'attendre que la routine
quotidienne accumule les jours un par un pendant 3 mois.

Entièrement stable dans le temps : la sélection de phrase et le score
sont un hash déterministe de `date + signe + domaine` (voir § Moteur de
contenu) — recalculer le même jour demain, dans un an, donne rigoureusement
le même résultat. La seule chose qui romprait cette stabilité serait de
modifier `data/fragments.json` (les phrases/scores de base) après coup ;
l'historique déjà écrit resterait alors figé sur l'ancienne version, ce
qui est le comportement souhaité (un historique ne doit pas bouger sous
les pieds une fois publié).

## Image du jour (Pexels)

Port simplifié des scripts Scénario (`fetch_topic_image.py` /
`use_topic_image.py`), Pexels uniquement (pas de repli Pixabay, non
demandé ici) :

```bash
export PEXELS_API_KEY=...
python3 scripts/social/fetch_topic_image.py "night sky stars galaxy" --count 5 --out /tmp/topic-image-candidates
# Regarder les candidats, puis :
python3 scripts/social/use_topic_image.py /tmp/topic-image-candidates/candidate-N.jpg --date AAAA-MM-JJ --credits /tmp/topic-image-candidates/credits.json
```

Produit `assets/topic-images/{date}.jpg` (carré 1080×1080) et
`{date}-wide.jpg` (1600×900, image en tête d'article). Mots-clés toujours
en anglais, toujours des concepts génériques — voir docstring du script
pour le détail. **`PEXELS_API_KEY` ne doit jamais être committée dans ce
dépôt** (public) : à fournir uniquement en variable d'environnement, ou
dans la config privée du futur trigger d'automatisation (même principe
que le token GoatCounter de Scénario).

## Distribution (Make.com → Instagram/Facebook)

`feed.xml` et `feed.json` sont structurés pour être consommés directement
par un scénario Make.com : titre, lien, image (`enclosure`/`image`),
légende prête à poster (`description`/`content_text`). La construction du
scénario Make (connexion aux comptes Instagram/Facebook) se fait côté
Make, hors de ce dépôt.

## Publicité (Google AdSense)

Un emplacement `.ad-slot` est réservé dans le gabarit, juste sous le
masthead. Le code réel AdSense sera à coller à la place du placeholder
une fois le compte créé et validé par Google (délai variable, parfois
plusieurs jours, hors du contrôle du site).

**Point de conformité à traiter avant activation réelle** : AdSense dépose
des cookies (personnalisation publicitaire), ce qui nécessite un recueil
de consentement (bandeau cookies / CMP) sous RGPD — contrairement à
GoatCounter qui n'en a pas besoin. La politique de confidentialité
mentionne déjà ce consentement, mais **le bandeau lui-même n'est pas
encore implémenté** dans cette v1 — à ajouter avant la mise en production
réelle des annonces.

## Mesure d'audience

GoatCounter (gratuit, sans cookie), même script que Scénario :
```html
<script data-goatcounter="https://grandfutur.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
```
Le compte `grandfutur` doit être créé sur goatcounter.com avant que le
compteur ne fonctionne réellement.

## Formulaire de contact

FormSubmit, AJAX (comme Scénario), destination `grandfuturcontact@gmail.com`.
**Reste à faire : envoyer un premier message de test depuis `contact.html`
et cliquer sur le lien de confirmation reçu par email** — le formulaire
ne délivre rien tant que cette activation n'est pas faite. Une fois
activé, un alias anonyme pourra remplacer l'email en clair dans le code,
comme sur Scénario (optionnel, évite l'exposition aux robots spammeurs).

## Identité visuelle

**Fond sombre, identique au principe de Scénario** — décision finale du
7 septembre, après deux allers-retours sur la palette dans la même
journée : une v1 sombre à dominante indigo/violette jugée « trop
ésotérique », puis un essai en fond clair parchemin jugé « pas du tout »
convaincant (« le marron »), pour revenir au fond sombre classique. Palette
actuelle, propre à Grand Futur (pas une reprise exacte des couleurs
Scénario, mais le même principe visuel) : fond très sombre (`--bg
#10151c`), texte clair (`--ink #ece7da`), accent or (`--gold #cf9d4c`),
quatre couleurs d'élément (Feu `#bd6248`, Terre `#5e9c78`, Air `#6f8fae`,
Eau `#8a7fae`). Un token dédié `--ink-on-gold` (`#201a10`, fixe, ne suit
pas le thème) sert uniquement au texte posé sur un fond or plein (bouton
« Ajouter », sélection de texte) — toujours sombre pour le contraste,
indépendamment de la couleur du texte courant de la page. Même base
typographique que Scénario pour la lisibilité (Fraunces + Inter +
JetBrains Mono).

**Ordre des sections retravaillé deux fois le 7 septembre** : d'abord
« Vos proches » en premier (retour utilisateur), puis revenu à l'ordre
Scénario — la photo/résumé du jour en tout premier, « Vos proches »
juste en dessous — décision finale, à ne pas réinverser sans nouveau
retour explicite.

## Backlog

Le backlog (idées, tâches ouvertes, priorités P1-P3) est dans un fichier
dédié : voir [`docs/BACKLOG.md`](./BACKLOG.md).

## Historique

- **7 septembre 2026** : troisième passage sur la carte famille suite aux
  retours utilisateur.
  - **La vibe est revenue, enrichie, sous la jauge d'Énergie** : le
    paragraphe `.sign-vibe` (une phrase par signe, reflétant sa
    `situation` du jour) avait été retiré plus tôt dans la journée au
    profit d'un texte générique par palier d'énergie — jugé trop pauvre
    ("on va réajouter le vibe que tu vas enrichir"). Il revient sous
    forme de **deux phrases** (la seconde ajoute un exemple concret) et
    s'affiche désormais directement sous la jauge d'Énergie centrée, à
    la place du texte par palier. `readCardData()`, `buildProfileText()`
    et `apply_to_index.py` (dict `VIBES`) le lisent/écrivent à nouveau.
  - **Conseil retiré définitivement** (retour utilisateur : "boiteux, tu
    dis n'importe quoi, aucun lien") : contrairement à la vibe et aux 4
    domaines, ce texte était fixe par signe et ne reflétait jamais la
    situation réelle du jour — d'où le sentiment de décalage. Plutôt que
    de le raccrocher au code du jour (retravail conséquent pour un
    contenu jugé pas indispensable), il est retiré comme "Style du jour"
    avant lui : les 12 blocs `.sign-conseil`/`.sign-extras`, la règle CSS,
    `readCardData().conseil`, et la ligne correspondante dans
    `buildProfileText()` et `docs/routine-prompt.md`.
  - **Les 4 domaines repassent dans l'accordéon "Voir le détail"**
    (retour utilisateur : "tu peux mettre l'accordéon qui englobe amour
    etc") — seule Énergie (+ sa vibe) reste visible sans clic ; l'idée
    du 7 septembre matin ("tout afficher sans accordéon, super visuel")
    est donc partiellement revenue en arrière une fois testée en vrai.
  - **Lexique déplacé de la page d'accueil vers "Le projet"**
    (`le-projet.html`) : contenu de référence (définitions Signe/
    Ascendant/Élément), pas du contenu du jour — n'avait pas sa place au
    milieu de la carte famille et des 12 signes.

- **7 septembre 2026** : ajustement de la grille Énergie + 4 domaines
  (voir entrée juste en dessous) suite à un premier retour utilisateur
  ("c'est quand même moche") : 5 cartes en grille à 2 colonnes laissait
  Humeur seul sur sa 3e ligne. Énergie — une moyenne des 4 domaines, pas
  un domaine en soi — est désormais centrée seule au-dessus d'une ligne
  de séparation (`<hr class="family-divider">`), avec une jauge plus
  grande (`.energy-ring--lg`) ; les 4 domaines restent en dessous, en
  grille fixe 2x2 (jamais de carte orpheline avec exactement 4 éléments).
  Icône et libellé de chaque carte reprennent désormais la couleur de sa
  jauge (`--ring-color`, celle du seuil de score) au lieu d'un or fixe,
  pour que chaque unité icône+jauge+libellé se lise d'un seul bloc.

- **7 septembre 2026** : le paragraphe "vibe" (résumé du signe en une
  phrase, `.sign-vibe`) retiré de la carte famille — remplacé par une
  grille toujours visible, Énergie + les 4 domaines, chacun avec sa
  propre jauge ronde (icône, pourcentage, une phrase courte), réutilisant
  le composant `.energy-ring` déjà utilisé pour l'énergie globale. Retour
  utilisateur : "ça doit être super visuel", avec un mockup de référence
  (icône + jauge + texte court par carte). Les 4 domaines ne sont donc
  plus cachés derrière l'accordéon "Voir le détail" — celui-ci ne
  contient plus que Conseil (renommé "Voir le conseil"). `apply_to_index.py`
  ne lit/écrit plus `.sign-vibe` (fonction et dict `NEW_VIBES` retirés),
  et `docs/routine-prompt.md` ne demande plus de le rédiger chaque jour —
  la donnée n'était plus affichée nulle part. `index.html` et l'archive
  du jour régénérés et vérifiés (Playwright, zéro erreur JS).

- **7 septembre 2026** : `rank_elements()` (`day_code.py`) plafonné à
  **un seul** élément favorisé et **un seul** freiné par calcul, jamais
  plus — retour utilisateur : "tu es sûr de tes % c'est super bas".
  Vérification faite à la main : le calcul était juste, mais quand un
  domaine n'a que 1-2 planètes gouvernantes (`DOMAIN_PLANETS`) et
  qu'elles se concentrent dans un même élément (ex. Lune + Mars tous
  les deux en Cancer le 7 septembre), les 2-3 autres éléments tombent
  à égalité à 0 et étaient *tous* classés "freiné" simultanément — un
  signe pouvait se retrouver avec ses 4 domaines freinés le même jour
  (Bélier : 42% avant correctif). Désormais, en cas d'égalité, un seul
  élément parmi les ex-æquo est tiré au sort de façon stable (hash de
  `date + domaine`, jamais toujours le même pour ne pas avantager Feu
  qui passait en premier dans le dict) ; les autres redeviennent
  neutres. Effet le 7 septembre : Bélier passe de 42% à 49%, plus aucun
  signe n'a ses 4 domaines freinés à la fois. `index.html`, l'archive du
  jour et l'historique (91 jours) recalculés avec la règle corrigée.

- **7 septembre 2026** : plusieurs retouches rapides sur la carte
  famille suite aux retours utilisateur en continu.
  - **"Style du jour" retiré entièrement** ("c'est nul") : les 12 blocs
    statiques, `readCardData()`/`styleEl`, la ligne dans le texte
    Copier/Partager, et les instructions correspondantes dans
    `docs/routine-prompt.md` — tout supprimé, pas juste masqué (contrairement
    à `#signes`/`#top3`, rien ne dépendait de cette donnée ailleurs).
  - **Phrase d'ascendant retirée de la zone visible et du texte
    Copier/Partager**, même raison que le décan plus tôt dans la
    journée : "je comprends pas s'il y a un lien" entre la phrase
    d'ascendant (générique) et le résumé du jour (quotidien), juxtaposés
    sans transition. L'ascendant continue de nuancer les scores
    (`applyAscendantNudge`), simplement plus expliqué en prose.
  - **Nom et sous-titre sur la même ligne** (`family-card-name`/
    `family-card-signs` passés de `<div>` à `<span>`) — carte encore un
    cran plus compacte.
  - **Bouton "Voir le détail" restylé en label discret** (JetBrains
    Mono, minuscule, `--paper-dim`, dorée seulement au survol) plutôt
    qu'un texte doré de taille normale — moins criard, plus éditorial.
  - **"Partager cet horoscope" raccourci en "Partager"**.
  - **Grille "Vos proches" repassée en damier 2 colonnes** (1 colonne
    sous 640px) — le choix initial "un profil par ligne" datait d'une
    époque où les cartes étaient beaucoup plus verbeuses ; devenu
    inutilement large maintenant qu'elles sont compactes. Chaque carte
    garde sa propre hauteur (`align-items:start`) : une carte dépliée
    à côté d'une repliée ne s'étire pas pour s'aligner, compromis visuel
    assumé.

- **7 septembre 2026** : bouton "Copier"/"Partager" unifiés en un seul
  bouton "Partager cet horoscope" (mobile : feuille native inchangée ;
  desktop : petit menu de 4 icônes dessinées à la main — Copier,
  WhatsApp, Telegram, X — plutôt que 2-3 widgets séparés). Deux
  maquettes présentées avant codage, option retenue par l'utilisateur.
  **Même jour** : sections "Les 12 signes aujourd'hui" et "Le trio le
  plus énergique du jour" masquées (`hidden`, jamais supprimées —
  `#signes` reste la source de données de "Vos proches", `#top3` ne
  sert à rien d'autre et pourra être supprimé plus tard) — jugées non
  utiles maintenant que "Vos proches" est la porte d'entrée ; la routine
  n'a donc plus à écrire le trio chaque matin. Raffinement visuel
  (point 7 d'une liste de pistes de refonte plus large, points 5 et 6
  mis de côté pour l'instant) : bordures de cartes adoucies
  (`--hairline-soft`), plus de respiration (padding/gap augmentés),
  halo doux et animé très lentement derrière les jauges d'énergie,
  texture d'étoiles discrète en fond de page (radial-gradients, pas une
  image) — palette et typographie déjà alignées avec l'idée de départ,
  pas retouchées. Titre du jour agrandi (`clamp(2.1rem, 5vw, 3.3rem)`
  contre `1.6rem-2.4rem`). Photo du jour remplacée : un ciel étoilé
  jugé "trop banal" comme choix récurrent → paysage de montagnes
  brumeuses au lever du jour (Marek Piwnicki/Pexels), plus cohérent
  avec la consigne "un beau paysage" et la palette du site.

- **7 septembre 2026** : "Argent & travail" renommé en "Argent" (retour
  utilisateur : séparer les deux en 2 domaines demanderait une nouvelle
  bibliothèque de phrases, une attribution planétaire séparée et une
  mise en page à 5 cases — jugé disproportionné pour l'instant ; un mot
  plus court suffit). Renommé dans `fragments.json`, `day_code.py`
  (`DOMAIN_PLANETS`), `generate_signs.py` (`DOMAINS`) et `index.html`
  (`ASCENDANT_NUDGE`) — le libellé affiché se propage automatiquement
  depuis `c["label"]`, aucun autre endroit à toucher à la main.
  **Même jour** : carte famille restructurée — l'accordéon "Voir le
  détail" englobe maintenant les 4 domaines *et* Style du jour/Conseil
  (avant : mini-jauges + Style/Conseil toujours visibles, seuls les
  détails par domaine repliés), pour une carte bien plus compacte par
  défaut ; CSS mort nettoyé (`.family-gauges`, `.family-chart-*`, d'une
  itération de design antérieure jamais reliée au JS actuel). Barre
  verticale colorée sur les phrases d'ascendant/décan retirée (retour
  utilisateur : "moches et ne veulent rien dire" — la couleur venait de
  l'élément du signe sans lien de sens avec le texte) : texte simple,
  couleur atténuée, sans bordure.

- **7 septembre 2026** : audit technique externe (généraliste, sans lecture
  du code réel) comparé point par point au code effectif. La plupart des
  recommandations UX/archives/SEO de base étaient déjà en place ou ne
  s'appliquaient pas (heure de naissance volontairement obligatoire, par
  exemple). Trois points se sont révélés réels et corrigés :
  - `p.name` (saisi librement dans le formulaire) était injecté via
    `innerHTML` sans échappement (`chip.innerHTML`, carte famille) — un
    prénom contenant du HTML/JS s'exécutait dans le propre navigateur du
    visiteur. Corrigé avec un helper `escapeHtml()` et `textContent` pour
    la puce de profil.
  - Les tuiles de signes (déjà de vrais `<button>`) n'exposaient pas leur
    état sélectionné aux lecteurs d'écran. Ajout de `aria-pressed` (basculé
    dans `selectSign()`) et `aria-controls="sign-detail"`.
  - Ajout de données structurées `Article` (JSON-LD : `headline`,
    `datePublished`, `dateModified`, `image`, `publisher`) — absent
    jusqu'ici, pertinent pour un contenu quotidien daté. **À mettre à jour
    à chaque nouvelle édition**, en même temps que `<title>`/meta/og:title
    (mêmes informations, un endroit de plus à changer).
- **7 septembre 2026** : v1 de démonstration publiée. GitHub Pages activé
  (branche `main`, dossier racine). Compte GoatCounter `grandfutur` créé
  et confirmé fonctionnel (le script déjà posé dans le gabarit correspond
  au bon compte). Email de contact confirmé : `grandfuturcontact@gmail.com`.
- **7 septembre 2026, même jour** : retours utilisateur successifs sur le
  premier jet — palette repassée en clair « éditorial chaleureux » (fond
  sombre indigo jugé trop ésotérique), hero repassé en photo plein écran
  type couverture, contenu du jour réécrit pour être concret (planètes et
  positions nommées, conséquences actionnables, plus de formule vague),
  passage d'un accordéon à un damier de 12 tuiles + panneau de détail
  unique, et ajout des 4 scores par domaine (Amour, Argent & travail,
  Santé, Humeur) dont la moyenne devient l'énergie globale affichée.
