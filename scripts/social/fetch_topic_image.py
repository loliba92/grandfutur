#!/usr/bin/env python3
"""
Cherche des photos libres de droits sur Pexels pour illustrer le thème
astral du jour, et télécharge les meilleurs candidats pour revue visuelle
avant usage — même principe que sur Scénario (scripts/social/fetch_topic_image.py),
simplifié à une seule source (Pexels) puisque c'est la seule demandée ici.

Ne choisit JAMAIS automatiquement une image finale : ce script propose des
candidats téléchargés localement. La sélection reste un geste humain — voir
`use_topic_image.py` pour valider un candidat comme image officielle du jour.

Mots-clés : toujours en anglais, toujours des CONCEPTS génériques (ex.
"night sky stars galaxy", "sunrise mountains", "ocean waves calm") — jamais
un nom propre. Pas de filtre d'orientation sur la recherche elle-même (ça
écarte une partie du catalogue avant même le classement par pertinence) —
le recadrage carré est appliqué après coup, sur la photo déjà choisie.

Usage:
    export PEXELS_API_KEY=...
    python3 scripts/social/fetch_topic_image.py "night sky stars galaxy" \\
        --count 5 --out /tmp/topic-image-candidates
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse

PEXELS_SEARCH_URL = "https://api.pexels.com/v1/search"
USER_AGENT = "GrandFutur/1.0"


def search_pexels(query: str, count: int, api_key: str, color: str | None = None) -> list[dict]:
    params_dict = {"query": query, "per_page": count}
    if color:
        params_dict["color"] = color
    params = urllib.parse.urlencode(params_dict)
    req = urllib.request.Request(
        f"{PEXELS_SEARCH_URL}?{params}",
        headers={"Authorization": api_key, "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("photos", [])


def crop_url(original_url: str, w: int, h: int) -> str:
    """Recadrage à la volée via le CDN Pexels, sur n'importe quel ratio d'origine."""
    sep = "&" if "?" in original_url else "?"
    return f"{original_url}{sep}auto=compress&cs=tinysrgb&fit=crop&w={w}&h={h}"


def square_crop_url(original_url: str, size: int = 1080) -> str:
    return crop_url(original_url, size, size)


def download(url: str, dest_path: str) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp, open(dest_path, "wb") as f:
        f.write(resp.read())


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("query", help="Mots-clés thématiques en anglais, ex. 'night sky stars galaxy'")
    parser.add_argument("--count", type=int, default=5, help="Nombre de candidats à télécharger (défaut 5)")
    parser.add_argument("--out", default="/tmp/topic-image-candidates", help="Dossier de sortie")
    parser.add_argument("--color", default=None, help="Filtre couleur dominante optionnel (nom Pexels ou hex)")
    args = parser.parse_args()

    if any(c in args.query for c in "àâäéèêëïîôöùûüçÀÂÄÉÈÊËÏÎÔÖÙÛÜÇ"):
        print(f"ATTENTION : « {args.query} » contient des accents français — "
              "Pexels indexe par tags anglais, reformule en 2-3 mots-clés anglais.\n", file=sys.stderr)

    os.makedirs(args.out, exist_ok=True)

    api_key = os.environ.get("PEXELS_API_KEY")
    if not api_key:
        print("ERREUR : PEXELS_API_KEY absente de l'environnement.", file=sys.stderr)
        sys.exit(1)

    try:
        results = search_pexels(args.query, args.count, api_key, color=args.color)
    except Exception as e:
        print(f"ERREUR lors de la recherche Pexels : {e}", file=sys.stderr)
        sys.exit(1)

    if not results:
        print(f"Aucun résultat pour « {args.query} ».")
        sys.exit(0)

    credits = []
    for i, item in enumerate(results, start=1):
        dest = os.path.join(args.out, f"candidate-{i}.jpg")
        img_url = square_crop_url(item["src"]["original"])
        try:
            download(img_url, dest)
        except Exception as e:
            print(f"  (échec téléchargement candidat {i} : {e})", file=sys.stderr)
            continue
        credit = {
            "candidate": i,
            "source": "pexels",
            "file": dest,
            "photographer": item.get("photographer"),
            "pexels_url": item.get("url"),
            "original_url": item.get("src", {}).get("original"),
            "query": args.query,
        }
        print(f"  candidat {i} : {dest}  (photo par {credit['photographer']}, {credit['pexels_url']})")
        credits.append(credit)

    if not credits:
        print("\nAucun candidat obtenu.")
        sys.exit(0)

    with open(os.path.join(args.out, "credits.json"), "w", encoding="utf-8") as f:
        json.dump(credits, f, ensure_ascii=False, indent=2)

    print(f"\n{len(credits)} candidat(s) téléchargé(s) dans {args.out}/ — à regarder avant tout usage.")


if __name__ == "__main__":
    main()
