#!/usr/bin/env python3
"""
Valide un candidat trouvé par fetch_topic_image.py comme image officielle
du jour : le copie vers assets/topic-images/{date}.jpg (carré, usage
réseaux sociaux) et produit un second recadrage 16:9 (1600×900) vers
assets/topic-images/{date}-wide.jpg (image en tête d'article) — même
principe que sur Scénario.

Geste toujours volontaire (jamais automatique) : n'exécuter qu'après avoir
regardé le candidat et confirmé qu'il correspond au thème du jour.

Usage:
    python3 scripts/social/use_topic_image.py \\
        /tmp/topic-image-candidates/candidate-2.jpg \\
        --date 2026-09-07 \\
        --credits /tmp/topic-image-candidates/credits.json
"""

import argparse
import json
import os
import shutil
import sys
import urllib.request


def crop_url(original_url: str, w: int, h: int) -> str:
    sep = "&" if "?" in original_url else "?"
    return f"{original_url}{sep}auto=compress&cs=tinysrgb&fit=crop&w={w}&h={h}"


def download(url: str, dest_path: str) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "GrandFutur/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp, open(dest_path, "wb") as f:
        f.write(resp.read())


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("candidate_path", help="Chemin du fichier candidate-N.jpg choisi")
    parser.add_argument("--date", required=True, help="Date de l'édition, AAAA-MM-JJ")
    parser.add_argument("--credits", required=True, help="Chemin du credits.json produit par fetch_topic_image.py")
    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    out_dir = os.path.join(repo_root, "assets", "topic-images")
    os.makedirs(out_dir, exist_ok=True)

    square_dest = os.path.join(out_dir, f"{args.date}.jpg")
    shutil.copy(args.candidate_path, square_dest)
    print(f"Image carrée : {square_dest}")

    with open(args.credits, encoding="utf-8") as f:
        credits = json.load(f)

    candidate_num = int(os.path.basename(args.candidate_path).split("-")[1].split(".")[0])
    entry = next((c for c in credits if c["candidate"] == candidate_num), None)

    if entry and entry.get("original_url"):
        wide_dest = os.path.join(out_dir, f"{args.date}-wide.jpg")
        try:
            download(crop_url(entry["original_url"], 1600, 900), wide_dest)
            print(f"Image large : {wide_dest}")
        except Exception as e:
            print(f"(échec recadrage large, pas bloquant : {e})", file=sys.stderr)
    else:
        print("(pas d'original_url dans credits.json, image large non produite)", file=sys.stderr)

    credit_dest = os.path.join(out_dir, f"{args.date}.credit.json")
    with open(credit_dest, "w", encoding="utf-8") as f:
        json.dump(entry or {}, f, ensure_ascii=False, indent=2)
    print(f"Fiche de provenance : {credit_dest}")

    print("\nÀ mettre à jour à la main : og:image / twitter:image dans le HTML du jour, "
          "et l'enclosure de feed.xml.")


if __name__ == "__main__":
    main()
