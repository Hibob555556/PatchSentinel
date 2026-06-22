"""Command-line entry point for an on-demand release scan."""

from __future__ import annotations

import argparse
import json

from data.sites import DEFAULT_SITES
from patchsentinel.scrapers.github_releases import scan_sites


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan configured GitHub releases")
    parser.add_argument(
        "--include-prereleases",
        action="store_true",
        help="Consider prereleases when selecting the newest release",
    )
    args = parser.parse_args()

    releases = scan_sites(
        DEFAULT_SITES,
        include_prereleases=args.include_prereleases,
    )
    print(json.dumps([release.to_dict() for release in releases], indent=2))


if __name__ == "__main__":
    main()
