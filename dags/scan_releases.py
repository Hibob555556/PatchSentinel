"""Airflow DAG for scanning configured projects for their latest release."""

from __future__ import annotations
from airflow.sdk import dag, task
import pendulum

DEFAULT_SITES = [
    "https://api.github.com/repos/apache/airflow/releases",
    "https://api.github.com/repos/microsoft/playwright/releases",
    "https://api.github.com/repos/SeleniumHQ/selenium/releases",
    "https://api.github.com/repos/nodejs/node/releases",
    "https://api.github.com/repos/dotnet/core/releases",
    "https://api.github.com/repos/tauri-apps/tauri/releases",
    "https://api.github.com/repos/godotengine/godot/releases",
    "https://api.github.com/repos/vercel/next.js/releases",
    "https://api.github.com/repos/react/react/releases",
    "https://api.github.com/repos/actions/runner/releases"
]

import os
from dataclasses import asdict, dataclass
from typing import Any, Iterable

import requests


DEFAULT_TIMEOUT_SECONDS = 20


@dataclass(frozen=True)
class Release:
    repository: str
    tag: str
    name: str
    published_at: str
    url: str
    prerelease: bool
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _repository_from_url(url: str) -> str:
    marker = "/repos/"
    if marker not in url:
        raise ValueError(f"Not a GitHub repository API URL: {url}")

    repository = url.split(marker, 1)[1].split("/releases", 1)[0].strip("/")
    if repository.count("/") != 1:
        raise ValueError(f"Could not determine repository from URL: {url}")
    return repository


def _release_from_payload(repository: str, payload: dict[str, Any]) -> Release:
    return Release(
        repository=repository,
        tag=payload.get("tag_name") or "",
        name=payload.get("name") or payload.get("tag_name") or "",
        published_at=payload.get("published_at") or payload.get("created_at") or "",
        url=payload.get("html_url") or "",
        prerelease=bool(payload.get("prerelease", False)),
        notes=payload.get("body") or "",
    )


def get_latest_release(
    releases_url: str,
    *,
    session: requests.Session | None = None,
    include_prereleases: bool = False,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> Release:
    """Return the newest published release from a GitHub releases endpoint."""

    client = session or requests.Session()
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "PatchSentinel/0.1",
    }
    if token := os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"

    response = client.get(
        releases_url,
        params={"per_page": 100},
        headers=headers,
        timeout=timeout,
    )
    response.raise_for_status()

    payload = response.json()
    if not isinstance(payload, list):
        raise ValueError(f"Expected a release list from {releases_url}")

    candidates = [
        item
        for item in payload
        if not item.get("draft")
        and item.get("published_at")
        and (include_prereleases or not item.get("prerelease"))
    ]
    if not candidates:
        raise LookupError(f"No published releases found for {releases_url}")

    newest = max(candidates, key=lambda item: item["published_at"])
    return _release_from_payload(_repository_from_url(releases_url), newest)

def scan_sites(
    sites: Iterable[str],
    *,
    session: requests.Session | None = None,
    include_prereleases: bool = False,
) -> list[Release]:
    """Scan each configured GitHub releases endpoint."""

    client = session or requests.Session()
    return [
        get_latest_release(
            site,
            session=client,
            include_prereleases=include_prereleases,
        )
        for site in sites
    ]

@dag(
    dag_id="scan_releases",
    schedule="0 */6 * * *",
    start_date=pendulum.datetime(2026, 6, 21, tz="UTC"),
    catchup=False,
    tags=["patch_sentinel", "releases"],
)
def scan_releases_dag():
    @task
    def fetch_latest_releases() -> list[dict]:
        return [release.to_dict() for release in scan_sites(DEFAULT_SITES)]

    fetch_latest_releases()


scan_releases_dag()
