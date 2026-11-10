#!/usr/bin/env python3
"""Build Rabbit World archives from the CurseForge pack sources."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zipfile import ZIP_DEFLATED, ZipFile, is_zipfile

ROOT = Path(__file__).resolve().parents[1]
CURSEFORGE_API = "https://api.curseforge.com/v1"
NEOFORGE_MAVEN = "https://maven.neoforged.net/releases/net/neoforged/neoforge"


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


def curseforge(path, key, payload=None):
    headers = {"x-api-key": key, "Accept": "application/json"}
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode()
    with urlopen(Request(CURSEFORGE_API + path, data=body, headers=headers), timeout=60) as response:
        return json.load(response)["data"]


def download(url, target):
    with urlopen(url, timeout=120) as response, target.open("wb") as file:
        shutil.copyfileobj(response, file)


def install_mods(manifest, mods, key):
    excluded = {
        line.split("#", 1)[0].strip()
        for line in (ROOT / "server-excludes.txt").read_text().splitlines()
    } - {""}
    projects = curseforge("/mods", key, {"modIds": sorted({
        entry["projectID"] for entry in manifest["files"]
    })})
    slugs = {project["id"]: project["slug"] for project in projects}

    for entry in manifest["files"]:
        project_id, file_id = entry["projectID"], entry["fileID"]
        slug = slugs.get(project_id)
        label = f"{slug or 'unknown'} (projectID={project_id}, fileID={file_id})"
        if slug is None:
            raise ValueError(f"CurseForge project metadata unavailable: {label}")
        if slug in excluded:
            continue

        try:
            details = curseforge(f"/mods/{project_id}/files/{file_id}", key)
        except HTTPError as error:
            raise ValueError(f"CurseForge metadata request failed (HTTP {error.code}): {label}") from error
        url, name = details.get("downloadUrl"), details["fileName"]
        if not url:
            raise ValueError(f"CurseForge download unavailable: {label}")
        if Path(name).name != name or not name.lower().endswith(".jar"):
            raise ValueError(f"Expected a server mod JAR: {label}")
        target = mods / name
        if target.exists():
            raise ValueError(f"Duplicate mod filename: {name} ({label})")
        print(f"Downloading {label}", flush=True)
        try:
            download(url, target)
        except HTTPError as error:
            raise ValueError(f"CurseForge file request failed (HTTP {error.code}): {label}") from error
        if not is_zipfile(target):
            raise ValueError(f"Invalid JAR: {label}")
        sha1 = next((item["value"] for item in details.get("hashes", []) if item["algo"] == 1), None)
        if sha1 and hashlib.sha1(target.read_bytes()).hexdigest() != sha1.lower():
            raise ValueError(f"SHA-1 mismatch: {label}")


def build_server(manifest, output):
    key = os.environ.get("CURSEFORGE_API_KEY")
    if not key:
        raise ValueError("Set CURSEFORGE_API_KEY before building the server pack.")
    loader = next(
        loader["id"] for loader in manifest["minecraft"]["modLoaders"] if loader["primary"]
    )
    if not loader.startswith("neoforge-"):
        raise ValueError(f"Expected NeoForge, found {loader}")
    version = loader.removeprefix("neoforge-")
    with tempfile.TemporaryDirectory() as temp:
        work = Path(temp)
        server = work / "server"
        shutil.copytree(ROOT / "overrides", server)
        # BlueMap generates server-world profiles on first run.
        shutil.rmtree(server / "config/bluemap/maps", ignore_errors=True)
        install_mods(manifest, server / "mods", key)

        installer = work / f"{loader}-installer.jar"
        download(f"{NEOFORGE_MAVEN}/{version}/{installer.name}", installer)
        java_env = os.environ.copy()
        java_env.pop("CURSEFORGE_API_KEY", None)
        subprocess.run(
            ["java", "-jar", str(installer), "--installServer"],
            cwd=server,
            env=java_env,
            check=True,
        )
        files = [(server / name, name) for name in ("run.sh", "run.bat", "user_jvm_args.txt")]
        for name in ("libraries", "mods", "config", "kubejs"):
            files.extend(tree_files(server / name, f"{name}/"))
        archive(output, files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", choices=("client", "server"))
    args = parser.parse_args()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    output = ROOT / "dist" / f"Rabbit-World-{args.target.title()}-{manifest['version']}.zip"
    if args.target == "client":
        files = [(ROOT / name, name) for name in ("manifest.json", "modlist.html")]
        files.extend(tree_files(ROOT / "overrides", "overrides/"))
        archive(output, files)
    else:
        build_server(manifest, output)
    print(output)


if __name__ == "__main__":
    try:
        main()
    except HTTPError as error:
        sys.exit(f"Download failed: HTTP {error.code}")
    except (URLError, ValueError, OSError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
