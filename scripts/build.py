#!/usr/bin/env python3
"""Build Rabbit World archives for the CurseForge client."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zipfile import ZIP_DEFLATED, ZipFile, is_zipfile

ROOT = Path(__file__).resolve().parents[1]
RABBIT_PROJECTS = {
    "RabbitCore": "rabbitcore",
    "RabbitTools": "rabbittools",
    "RabbitMine": "rabbitmine",
}


def archive(output, files):
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as temp:
        staged = Path(temp) / output.name
        with ZipFile(staged, "w", ZIP_DEFLATED) as bundle:
            for file, name in sorted(files, key=lambda item: item[1]):
                bundle.write(file, name)
        staged.replace(output)


def tree_files(root, prefix=""):
    for path in root.rglob("*"):
        if path.is_file():
            yield path, prefix + path.relative_to(root).as_posix()


def download(url, target):
    with urlopen(url, timeout=120) as response, target.open("wb") as file:
        shutil.copyfileobj(response, file)


def rabbit_mods(manifest, directory):
    minecraft = manifest["minecraft"]["version"]
    mods = {}
    for project, mod_id in RABBIT_PROJECTS.items():
        api = f"https://api.github.com/repos/RabbitWorldTeam/{project}/releases/latest"
        request = Request(api, headers={"Accept": "application/vnd.github+json"})
        try:
            with urlopen(request, timeout=60) as response:
                release = json.load(response)
        except HTTPError as error:
            if error.code == 404:
                raise ValueError(f"{project} has no published stable GitHub Release.") from error
            raise
        version = release["tag_name"].removeprefix("v")
        name = f"{mod_id}-{minecraft}-neoforge-{version}.jar"
        assets = [asset for asset in release["assets"] if asset["name"] == name]
        if len(assets) != 1:
            raise ValueError(f"{project} {release['tag_name']} is missing the expected asset {name}.")
        asset = assets[0]
        target = directory / name
        if target.name != name:
            raise ValueError(f"Invalid release asset name: {name}")
        download(asset["browser_download_url"], target)
        if not is_zipfile(target):
            raise ValueError(f"Invalid release JAR: {project} {name}")
        digest = asset.get("digest")
        if digest and digest != "sha256:" + hashlib.sha256(target.read_bytes()).hexdigest():
            raise ValueError(f"SHA-256 mismatch: {project} {name}")
        mods[project] = target
        print(f"Using {project} {release['tag_name']}: {name}", flush=True)
    return mods


def build_client(output, mods):
    files = [(ROOT / name, name) for name in ("manifest.json", "modlist.html")]
    files.extend(tree_files(ROOT / "overrides", "overrides/"))
    files.extend((jar, f"overrides/mods/{jar.name}") for jar in mods.values())
    archive(output, files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", choices=("client",), default="client")
    parser.parse_args()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as temp:
        mods = rabbit_mods(manifest, Path(temp))
        output = ROOT / "dist" / f"Rabbit-World-Client-{manifest['version']}.zip"
        build_client(output, mods)
        print(output)


if __name__ == "__main__":
    try:
        main()
    except HTTPError as error:
        sys.exit(f"Download failed: HTTP {error.code}")
    except (URLError, ValueError, OSError) as error:
        sys.exit(str(error))
