"""Release source scrapers."""

from .github_releases import Release, scan_sites

__all__ = ["Release", "scan_sites"]
