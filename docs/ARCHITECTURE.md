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
5. **Les 12 signes, en accordéon** — une carte par signe, repliée par
   défaut : l'en-tête (glyphe, dates, jauge d'énergie) reste visible en
   permanence, le détail (texte du jour, atout, à éviter) ne s'affiche
   qu'au clic. Accordéon en CSS pur (`grid-template-rows` 0fr → 1fr, comme
   l'accordéon des résumés de `archives.html` sur Scénario), le JS ne fait
   que basculer une classe `is-open` — plusieurs cartes peuvent rester
   ouvertes en même temps, pas de fermeture automatique des autres. Chaque
   carte porte `data-sign`, `data-element` et `data-energy` — lus par le
   JS du gestionnaire de profils, **source unique de vérité** (pas de
   duplication du contenu du jour dans un objet JS séparé). Un clic sur
   « Voir le détail de son signe » depuis une carte famille ouvre
   l'accordéon correspondant avant de scroller — sinon le contenu resterait
   caché malgré le défilement.
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

**Fond clair « éditorial chaleureux »** (décidé le 7 septembre après retour
utilisateur : une première version sombre à dominante indigo/violette a été
jugée « trop ésotérique »). Palette actuelle, propre à Grand Futur : fond
parchemin chaud (`--bg #f3ead9`), texte encre brune (`--ink #2b2318`),
accent or plus profond qu'un simple jaune pour garder du contraste sur fond
clair (`--gold #b8863f`), quatre couleurs d'élément recalées pour rester
lisibles sur fond clair (Feu `#b5573c`, Terre `#4f8563`, Air `#4f708f`, Eau
`#6f5f96`). Seule la photo du jour (bandeau `.article-image-*`) garde un
traitement sombre — dégradé + texte clair incrusté dessus — puisqu'elle
reste une image, indépendante du thème du reste de la page. Même base
typographique que Scénario pour la lisibilité (Fraunces + Inter +
JetBrains Mono).

## Ce qui reste à faire

- **Automatisation quotidienne réelle** : une routine planifiée (type
  Claude Code Remote) qui génère le vrai thème du jour, les 12 textes et
  l'énergie de chaque signe, récupère une photo Pexels adaptée au thème,
  écrase `index.html` et fige l'archive — sur le modèle exact de la
  routine Scénario (`docs/routine-prompt.md`).
- **FormSubmit** : envoyer un premier message de test depuis
  `contact.html` et cliquer sur le lien de confirmation reçu à
  `grandfuturcontact@gmail.com` pour activer le formulaire.
- **Compte Google AdSense** à créer et faire valider, puis remplacer le
  placeholder `.ad-slot` par le vrai code — et implémenter un bandeau de
  consentement cookies avant activation réelle.
- **Scénario Make.com** à construire côté Make (lecture de `feed.xml`,
  publication Instagram + Facebook).
- **Nom de domaine** : le site tourne pour l'instant sur
  `https://loliba92.github.io/grandfutur/` — à remplacer par un domaine
  dédié (`CNAME` + toutes les URLs absolues du site) une fois acheté.

## Historique

- **7 septembre 2026** : v1 de démonstration publiée. GitHub Pages activé
  (branche `main`, dossier racine). Compte GoatCounter `grandfutur` créé
  et confirmé fonctionnel (le script déjà posé dans le gabarit correspond
  au bon compte). Email de contact confirmé : `grandfuturcontact@gmail.com`.
