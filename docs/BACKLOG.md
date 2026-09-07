# Backlog — Grand Futur

Idées, tâches ouvertes et priorités, séparées de `docs/ARCHITECTURE.md`
— même principe que sur Scénario. P1 = bloquant pour une vraie v1 vivante,
P2 = important mais pas bloquant, P3 = idée future à explorer.

## P1 — Essentiel

- **Automatisation quotidienne réelle** : une routine planifiée (type
  Claude Code Remote) qui génère le vrai thème du jour, les 12 textes et
  les 4 scores par domaine (Amour, Argent & travail, Santé, Humeur) de
  chaque signe, récupère une photo Pexels adaptée au thème, écrase
  `index.html` et fige l'archive — sur le modèle exact de la routine
  Scénario (`docs/routine-prompt.md`). Tant que ce point n'est pas fait,
  le site reste une démo figée sur l'édition du 7 septembre.
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

  **Faisabilité : oui, sans backend**, à condition que la routine
  quotidienne publie une petite trace de données à chaque édition plutôt
  que seulement le HTML. Deux approches :
  1. *(Retenue)* Un fichier JSON cumulatif (ex. `data/energie-quotidienne.json`),
     complété par la routine chaque matin, au format
     `{"date": "AAAA-MM-JJ", "energies": {"belier": 78, "taureau": 64, ...}}`
     par jour publié. Le JS du site le télécharge une fois (`fetch`), puis
     pour chaque profil enregistré, extrait la série de son signe solaire
     et trace une courbe — réutiliser le composant `.dc-chart-box`/SVG déjà
     construit sur Scénario pour le graphique de croissance d'audience
     (voir `docs/ARCHITECTURE.md` de Scénario, section « Mesure
     d'audience »), même principe d'escalier/ligne, pas besoin de
     bibliothèque de graphique externe.
  2. Alternative sans nouveau fichier : lire chaque `archives/{date}.html`
     et en extraire les `data-energy` par signe via `fetch` + parsing HTML
     côté client — plus lourd dès que l'historique s'allonge (autant de
     requêtes que de jours d'archive), à éviter au-delà de quelques
     semaines d'historique.

  **Dépendance bloquante** : n'a de sens qu'une fois l'automatisation
  quotidienne réelle en place (P1) — tant que le contenu est un exemple
  figé sur une seule date, il n'y a rien à tracer dans le temps. À
  construire après, pas avant.

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
