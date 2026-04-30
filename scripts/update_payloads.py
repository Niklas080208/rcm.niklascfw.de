#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parent.parent
PAYLOADS_DIR = REPO_ROOT / "payloads"
INDEX_HTML_PATH = REPO_ROOT / "index.html"


SOURCES = {
    "hekate": {
        "api_url": "https://api.github.com/repos/CTCaer/hekate/releases/latest",
        "asset_name_pattern": r"^hekate_ctcaer_(\d+\.\d+\.\d+)\.bin$",
        "output_filename": "hekate_ctcaer.bin",
        "html_link_id": "hekate-release-link",
        "fallback_version_from_tag": True,
    },
    "atmosphere": {
        "api_url": "https://api.github.com/repos/Atmosphere-NX/Atmosphere/releases/latest",
        "asset_name_pattern": r"^fusee\.bin$",
        "output_filename": "fusee.bin",
        "html_link_id": "atmosphere-release-link",
        "fallback_version_from_tag": True,
    },
}


def fetch_json(url: str) -> dict:
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "payload-updater",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def download_binary(url: str) -> bytes:
    request = Request(
        url,
        headers={
            "Accept": "application/octet-stream",
            "User-Agent": "payload-updater",
        },
    )
    with urlopen(request, timeout=60) as response:
        return response.read()


def find_matching_asset(release: dict, pattern: str) -> tuple[dict, str | None]:
    regex = re.compile(pattern)
    for asset in release.get("assets", []):
        name = asset.get("name", "")
        match = regex.match(name)
        if match:
            version = match.group(1) if match.lastindex else None
            return asset, version
    raise RuntimeError(f"No asset matched pattern: {pattern}")


def normalize_version(tag_name: str | None) -> str:
    if not tag_name:
        return "unknown"
    return tag_name.removeprefix("v")


def update_index_html(link_id: str, release_url: str, version: str) -> None:
    html = INDEX_HTML_PATH.read_text(encoding="utf-8")
    replacement = f'<a id="{link_id}" href="{release_url}">v{version}</a>'
    pattern = re.compile(rf'<a id="{re.escape(link_id)}" href="[^"]+">v[^<]+</a>')
    updated_html, replacements = pattern.subn(replacement, html, count=1)
    if replacements != 1:
        raise RuntimeError(f"Could not update link with id: {link_id}")
    INDEX_HTML_PATH.write_text(updated_html, encoding="utf-8")


def main() -> int:
    PAYLOADS_DIR.mkdir(parents=True, exist_ok=True)

    for source_name, source in SOURCES.items():
        release = fetch_json(source["api_url"])
        asset, version_from_name = find_matching_asset(release, source["asset_name_pattern"])
        version = version_from_name or (
            normalize_version(release.get("tag_name")) if source["fallback_version_from_tag"] else None
        )
        if not version:
            raise RuntimeError(f"Could not determine version for {source_name}")

        data = download_binary(asset["browser_download_url"])
        payload_path = PAYLOADS_DIR / source["output_filename"]
        payload_path.write_bytes(data)

        update_index_html(
            link_id=source["html_link_id"],
            release_url=release["html_url"],
            version=version,
        )

        print(f"Updated {source_name}: v{version} -> {source['output_filename']}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (HTTPError, URLError, TimeoutError, RuntimeError, KeyError) as exc:
        print(f"Payload update failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
