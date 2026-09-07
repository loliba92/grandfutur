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
   l'énergie globale) : chaque signe porte 4 sous-scores — Amour, Argent &
   travail, Santé, Humeur — chacun avec un texte dédié. **L'énergie globale
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
  +4 Argent & travail / -3 Santé ; Eau : +4 Amour / -2 Argent & travail),
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
