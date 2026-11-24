"""Download the pinned OWID CO2 CSV files without overwriting existing files."""

from __future__ import annotations

import hashlib
import os
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


COMMIT = "382ee6c662b0ece26e111f263b44c029afad7787"
BASE_URL = f"https://raw.githubusercontent.com/owid/co2-data/{COMMIT}"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPOSITORY_ROOT / "data" / "raw"
SOURCES_FILE = RAW_DIR / "SOURCES.txt"

DOWNLOADS = (
    ("owid-co2-data.csv", f"{BASE_URL}/owid-co2-data.csv"),
    ("owid-co2-codebook.csv", f"{BASE_URL}/owid-co2-codebook.csv"),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def append_source(file_name: str, url: str) -> None:
    with SOURCES_FILE.open("a", encoding="utf-8", newline="\n") as file:
        file.write(f"{date.today().isoformat()}  {url}  {file_name}\n")


def download_file(url: str, destination: Path) -> bool:
    if destination.exists():
        return False

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".part",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            with urlopen(url) as response:
                for chunk in iter(lambda: response.read(1024 * 1024), b""):
                    temporary.write(chunk)

        try:
            os.link(temporary_path, destination)
            return True
        except FileExistsError:
            return False
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def report_file(path: Path) -> None:
    print(f"{path.name}: {path.stat().st_size} bytes")
    print(f"{path.name}: SHA-256 {sha256(path)}")


def run(downloads: Iterable[tuple[str, str]] = DOWNLOADS) -> None:
    for file_name, url in downloads:
        destination = RAW_DIR / file_name
        downloaded = download_file(url, destination)

        if downloaded:
            append_source(file_name, url)

        report_file(destination)


def main() -> int:
    try:
        run()
    except (HTTPError, URLError, OSError) as error:
        print(f"Error: download failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
