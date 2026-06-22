import pytest
import requests
import requests_mock

from patchsentinel.scrapers.github_releases import get_latest_release, scan_sites


RELEASES_URL = "https://api.github.com/repos/example/project/releases"


def test_get_latest_stable_release_ignores_drafts_and_prereleases():
    payload = [
        {
            "tag_name": "v3.0.0-rc1",
            "name": "3.0 RC 1",
            "published_at": "2026-06-20T00:00:00Z",
            "html_url": "https://github.com/example/project/releases/tag/v3.0.0-rc1",
            "prerelease": True,
            "draft": False,
            "body": "Candidate",
        },
        {
            "tag_name": "v2.1.0",
            "name": "2.1",
            "published_at": "2026-06-19T00:00:00Z",
            "html_url": "https://github.com/example/project/releases/tag/v2.1.0",
            "prerelease": False,
            "draft": False,
            "body": "Bug fixes",
        },
        {
            "tag_name": "v9.0.0",
            "published_at": "2026-06-21T00:00:00Z",
            "prerelease": False,
            "draft": True,
        },
    ]

    with requests_mock.Mocker() as mock:
        mock.get(RELEASES_URL, json=payload)
        release = get_latest_release(RELEASES_URL)

    assert release.repository == "example/project"
    assert release.tag == "v2.1.0"
    assert release.notes == "Bug fixes"


def test_get_latest_release_can_include_prereleases():
    payload = [
        {
            "tag_name": "v3.0.0-rc1",
            "published_at": "2026-06-20T00:00:00Z",
            "prerelease": True,
            "draft": False,
        },
        {
            "tag_name": "v2.1.0",
            "published_at": "2026-06-19T00:00:00Z",
            "prerelease": False,
            "draft": False,
        },
    ]

    with requests_mock.Mocker() as mock:
        mock.get(RELEASES_URL, json=payload)
        release = get_latest_release(RELEASES_URL, include_prereleases=True)

    assert release.tag == "v3.0.0-rc1"


def test_scan_sites_propagates_http_errors():
    with requests_mock.Mocker() as mock:
        mock.get(RELEASES_URL, status_code=403)
        with pytest.raises(requests.HTTPError):
            scan_sites([RELEASES_URL])
