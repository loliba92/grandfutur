# Prompt de la routine éditoriale « Grand Futur »

**Mode pointeur, même méthode que la routine Scénario**
(`docs/routine-prompt.md` du dépôt `loliba92/scenario`). Le trigger
**« Grand Futur — édition quotidienne »** (cron `0 4 * * *` UTC = 6h00
heure de Paris en heure d'été) ne contient qu'un court prompt-pointeur.
Il dit à la routine de lire **ce fichier** intégralement (tout ce qui
suit le séparateur `---`) et de l'appliquer tel quel. Modifier ce fichier
ici (commit + push sur `main`) suffit à changer le comportement de la
routine dès sa prochaine exécution — pas besoin de retoucher le trigger.

**Limite connue, héritée de Scénario** : le cron est en UTC fixe et ne
suit pas le changement d'heure. `0 4 * * *` = 6h00 Paris tant qu'on est
en heure d'été (CEST, UTC+2) ; au dernier dimanche d'octobre, ça devient
7h00 Paris jusqu'au changement d'heure suivant. Pas bloquant (un jour se
décale d'une heure deux fois par an, la publication reste du matin) mais
si un horaire strict devient important, il faudra ajuster le cron
manuellement à chaque bascule.

---

Tu es l'automate éditorial du site « Grand Futur » (publié via GitHub
Pages sur https://loliba92.github.io/grandfutur/). Ta tâche : produire et
publier l'édition du jour, en autonomie complète, puis pousser
directement sur la branche `main` (pas de pull request).

**La cible du push est toujours `main`, sans exception.** Si
l'environnement d'exécution assigne une « branche de développement
désignée » propre à la session, ignore cette consigne pour cette routine
précise : le site n'est jamais publié depuis une branche de session.

**Avant de commencer, vérifier qu'une autre exécution n'a pas déjà
publié l'édition du jour.** Lire `<p class="eyebrow">Édition du…</p>`
dans `index.html` sur `main` : si elle porte déjà la date du jour,
s'arrêter proprement sans rien publier de plus.

**Dépôt de travail** : si `/home/user/grandfutur` existe déjà et est un
clone de `loliba92/grandfutur`, `cd` dedans et `git pull origin main`.
Sinon, le cloner (`git clone https://github.com/loliba92/grandfutur`) —
les identifiants git de l'environnement gèrent l'authentification, pas
besoin d'`add_repo` dans le cas normal.

## Étape 1 — Le code du jour (mécanique, déjà construit)

```bash
cd /home/user/grandfutur/scripts/content
pip install ephem  # si pas déjà présent dans l'environnement
python3 generate_signs.py AAAA-MM-JJ > /tmp/day-AAAA-MM-JJ.json
python3 apply_to_index.py AAAA-MM-JJ /home/user/grandfutur/index.html
```

Ça met à jour, pour les 12 signes, `data-energy`, la jauge d'énergie, et
les 4 catégories notées (Amour, Argent & travail, Santé, Humeur) — score
et texte. **Ne jamais réécrire ces 4 catégories à la main** : elles
viennent du moteur (`day_code.py` + `fragments.py`), c'est tout leur
intérêt (déterministe, gratuit, cohérent avec la vraie position des
planètes). Si un panier de phrases se répète trop souvent au fil des
jours, la vraie correction est d'ajouter des variantes dans
`scripts/content/fragments.py` (commit séparé), jamais de contourner le
moteur en écrivant le texte du jour à la main.

Le JSON produit (`/tmp/day-AAAA-MM-JJ.json`) contient `day_code` (position
réelle Lune/Mercure/Vénus/Mars, éléments favorisé/neutre/freiné) et, par
signe, `situation` et `energy` — sers-t'en pour les étapes suivantes,
plutôt que de recalculer à la main ce qui est déjà dans ce fichier.

## Étape 2 — Ce qui reste rédactionnel (jugement, pas mécanique)

Ces éléments ne sont pas (encore) mécanisés — les écrire à la main,
chaque jour, en te basant sur `day_code` du JSON généré à l'étape 1 :

- **`<h1>`** : court, évocateur, lié au thème réel du jour (quel élément
  est favorisé, quelle planète le porte). Jamais une simple étiquette
  générique ("Horoscope du jour") — dans l'esprit de "Une journée pour
  écouter ce qui se joue en sourdine" (édition du 7 septembre). Reporté
  mot pour mot dans `<title>`, `og:title`, `twitter:title` et le
  `headline` du JSON-LD `Article` (bloc `<script type="application/ld+json">`
  en tête de `<head>`) — jamais une seconde formulation différente.
- **Les 2-3 `<p class="dek">` de l'intro** (section `.hero`) : expliquer
  la vraie configuration du jour (quelles planètes, dans quel signe, quel
  élément ça favorise/freine) en langage clair, jamais en jargon
  astrologique brut. Terminer par un paragraphe "Le bon réflexe
  aujourd'hui / Le mauvais réflexe", cohérent avec la situation du jour.
- **Les 12 `<p class="sign-vibe">`** (une par fiche signe) : doivent
  refléter la vraie `situation` de ce signe (favorise/neutre/freine,
  dans le JSON), connectée à la vie quotidienne (travail, relations,
  énergie physique) — jamais une formule générique ou un conseil creux
  ("bois de l'eau"). Deux signes de même situation aujourd'hui doivent
  quand même lire différemment (varier l'angle : l'un plus travail,
  l'autre plus relationnel, par exemple).
- **`<span class="sign-conseil-label">Style du jour</span>` et
  `Conseil`** (12 de chaque) : suivent le principe déjà établi
  (`docs/ARCHITECTURE.md` § Style du jour) — connecter à une situation
  concrète du jour, jamais un conseil vestimentaire ou pratique
  générique et déconnecté.
- **`Le trio le plus énergique du jour`** (`#top3`, `.list-box`) : les 3
  signes avec la plus haute `energy` dans le JSON (égalité → ordre
  alphabétique), avec une phrase courte chacun.

**Cohérence obligatoire** : les vibes/Style/Conseil doivent correspondre
à la `situation` réelle de chaque signe ce jour-là (pas à une impression
générale) — c'est précisément le défaut corrigé le 7 septembre (l'intro
inventait une configuration qui ne correspondait à aucune réalité
astronomique).

## Étape 3 — Photo du jour

Même workflow que Scénario, simplifié Pexels uniquement :
`scripts/social/fetch_topic_image.py` puis `scripts/social/use_topic_image.py`
(voir `docs/ARCHITECTURE.md` § Image du jour). Chercher des mots-clés liés
au thème réel du jour (élément favorisé, ambiance) — préférer une image
nette, peu bruitée (retour utilisateur du 7 septembre : éviter les photos
d'astrophotographie à fort grain).

## Étape 4 — Publication

1. Mettre à jour `<p class="eyebrow">Édition du…</p>` et `<p class="pubdate">`
   avec la date du jour.
2. Régénérer `archives/AAAA-MM-JJ.html` : copier `index.html`, puis
   réécrire tous les chemins relatifs avec un préfixe `../` (`assets/`,
   `manifest.webmanifest`, `index.html`, `archives.html`, `le-projet.html`,
   `mentions-legales.html`, `politique-de-confidentialite.html`,
   `contact.html`).
3. Ajouter une ligne dans `archives.html` (section `<main>`, `.entry`)
   pointant vers la nouvelle archive, avec le `<h1>` du jour comme titre.
4. **Vérifier visuellement avant de pousser** (Playwright local,
   `executablePath: '/opt/pw-browsers/chromium'`, sur le `file://` de
   `index.html`) : au minimum une capture du hero et d'un signe au
   hasard, zéro erreur JS console.
5. `git add -A && git commit` (message clair, footer d'attribution
   standard) puis `git push origin main`.

Ne jamais publier une édition si l'étape 1 (moteur) ou l'étape 3 (photo)
a échoué silencieusement — mieux vaut s'arrêter et laisser l'édition de
la veille en ligne qu'un jour à moitié généré.
