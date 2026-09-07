"""
Chargeur mince pour la bibliothèque de phrases — la source de vérité est
`data/fragments.json` à la racine du dépôt, pas ce fichier. Un seul JSON,
lu nativement par Python ici (`json.load`) et par le JS d'`index.html`
(`fetch`) : plus de duplication entre un dict Python et un objet JS, plus
de script de synchronisation à faire tourner. Éditer les phrases : ouvrir
`data/fragments.json` directement, jamais ce module.

Conserve les noms `FRAGMENTS`/`BASE_SCORE` pour ne rien changer côté
generate_signs.py.
"""
import json
import pathlib

_DATA_PATH = pathlib.Path(__file__).resolve().parent.parent.parent / "data" / "fragments.json"
_data = json.loads(_DATA_PATH.read_text(encoding="utf-8"))

FRAGMENTS = _data["domains"]
BASE_SCORE = _data["base_score"]
