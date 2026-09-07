# Backlog — Grand Futur

Idées, tâches ouvertes et priorités, séparées de `docs/ARCHITECTURE.md`
— même principe que sur Scénario. P1 = bloquant pour une vraie v1 vivante,
P2 = important mais pas bloquant, P3 = idée future à explorer.

## P1 — Essentiel

- **Automatisation quotidienne réelle** : une routine planifiée (type
  Claude Code Remote) qui, chaque matin, appelle le moteur de contenu
  (`scripts/content/`, voir `ARCHITECTURE.md` § Moteur de contenu),
  récupère une photo Pexels adaptée au thème du jour, écrase `index.html`
  et fige l'archive — sur le modèle de la routine Scénario
  (`docs/routine-prompt.md`). Le moteur qui calcule le contenu existe déjà
  (7 septembre) ; ce qui manque encore, c'est le déclenchement automatique
  quotidien (la routine elle-même) et la génération programmatique du
  paragraphe d'intro + des 12 phrases "vibe" (encore écrites à la main à
  chaque édition, voir la limite notée dans `ARCHITECTURE.md`). Tant que
  ce point n'est pas fait, le site reste une démo figée sur l'édition du
  7 septembre.
- **FormSubmit** : envoyer un premier message de test depuis
  `contact.html` et cliquer sur le lien de confirmation reçu à
  `grandfuturcontact@gmail.com` pour activer le formulaire.

## P2 — Important, pas bloquant

- **Compte Google AdSense** à créer et faire valider, puis remplacer le
  placeholder `.ad-slot` par le vrai code — et implémenter un bandeau de
  consentement cookies avant activation réelle (voir
  `politique-de-confidentialite.html`, section Publicité).
- **Scénario Make.com** à construire côté Make (lecture de `feed.xml`,
  publication Instagram + Facebook).
- **Nom de domaine** : le site tourne pour l'instant sur
  `https://loliba92.github.io/grandfutur/` — à remplacer par un domaine
  dédié (`CNAME` + toutes les URLs absolues du site) une fois acheté.

## P3 — Idées futures

- **Graphique d'évolution du score par profil** (demande utilisateur du
  7 septembre) : pour chaque profil enregistré (Olivier, sa femme,
  Juliette, Lisa...), afficher une courbe de l'énergie de son signe
  solaire jour après jour, plutôt qu'une seule valeur instantanée —
  visualiser une tendance dans le temps.

  **Donnée : faite (7 septembre).** `data/historique-energie.json`
  existe, pré-rempli sur 91 jours (9 juin → 7 septembre) via
  `scripts/content/build_history.py` — le code du jour étant un vrai
  calcul astronomique, on peut le rejouer pour une date passée aussi
  bien que pour aujourd'hui, pas besoin d'attendre que la routine
  accumule les jours un par un. La routine quotidienne (étape 1,
  `docs/routine-prompt.md`) y ajoute l'entrée du jour à chaque édition.
  Format : `{"AAAA-MM-JJ": {"energies": {"belier": 78, ...}, "day_code": {...}}, ...}`
  — `day_code` (positions réelles + éléments favorisé/neutre/freiné)
  ajouté le 7 septembre pour que chaque énergie reste vérifiable après
  coup, voir `docs/ARCHITECTURE.md` § Historique des énergies.

  **Reste à construire : la courbe elle-même**, côté JS d'`index.html` —
  `fetch("data/historique-energie.json")`, puis pour chaque profil
  enregistré, extraire `energies[signe]` de chaque date et la tracer.
  Réutiliser le composant `.dc-chart-box`/SVG déjà construit sur Scénario
  pour le graphique de croissance d'audience (voir `docs/ARCHITECTURE.md`
  de Scénario, section « Mesure d'audience »), même principe
  d'escalier/ligne, pas besoin de bibliothèque de graphique externe.
  Plus bloqué par rien — à faire dès que demandé.

- ~~**Décan** comme troisième axe de personnalisation~~ — **fait le 7
  septembre**, voir `docs/ARCHITECTURE.md` § « Décan ». Pas de nuance de
  score ajoutée (décision assumée, voir la doc) : reste une phrase
  informative, pas un modificateur numérique en plus de celui de
  l'ascendant.
- **Style du jour et Conseil mécanisés** : ces deux blocs sont encore
  écrits/ajustés à la main à chaque édition (voir `ARCHITECTURE.md` §
  Moteur de contenu, limite assumée) — les faire aussi piocher dans une
  bibliothèque par situation du jour, comme les 4 domaines notés.
- **Ascendant avec lieu de naissance précis** : la v1 suppose une
  naissance en France métropolitaine (Paris) pour tout le monde — ajouter
  un champ ville/pays au profil si le besoin de précision se confirme
  pour des lecteurs nés loin de la France (voir `docs/ARCHITECTURE.md`,
  section calcul de l'ascendant).
- **Calcul de compatibilité** entre deux profils enregistrés (soi-même et
  un proche) — un des contenus les plus partagés en astrologie, faisable
  en zéro-backend (calcul JS côté client, pas d'appel serveur).
- **Personnalisation approfondie** (thème astral complet, rapport annuel)
  en version premium — à envisager seulement une fois une vraie audience
  fidèle installée.
