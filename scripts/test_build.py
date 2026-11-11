import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from zipfile import ZipFile

import build


class RabbitReleaseTests(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory()
        self.addCleanup(work.cleanup)
        self.root = Path(work.name)
        (self.root / "overrides" / "config").mkdir(parents=True)
        (self.root / "overrides" / "config" / "example.txt").touch()
        (self.root / "manifest.json").touch()
        (self.root / "modlist.html").touch()
        self.manifest = {"minecraft": {"version": "1.21.1", "modLoaders": [
            {"id": "neoforge-21.1.265", "primary": True},
        ]}}
        payload = io.BytesIO()
        with ZipFile(payload, "w") as jar:
            jar.writestr("META-INF/neoforge.mods.toml", "")
        self.jar_bytes = payload.getvalue()

    def release(self, request, timeout):
        project = request.full_url.split("/")[-3]
        mod_id = build.RABBIT_PROJECTS[project]
        name = f"{mod_id}-1.21.1-neoforge-1.2.3.jar"
        return io.BytesIO(json.dumps({"tag_name": "v1.2.3", "assets": [{
            "name": name,
            "browser_download_url": f"https://github.com/example/releases/download/v1.2.3/{name}",
            "digest": "sha256:" + hashlib.sha256(self.jar_bytes).hexdigest(),
        }]}).encode())

    def test_both_packs_reuse_common_jars_and_auth_is_server_only(self):
        def download(url, target):
            target.write_bytes(self.jar_bytes)

        def install_neoforge(command, cwd, env, check):
            for name in ("run.sh", "run.bat", "user_jvm_args.txt"):
                (cwd / name).touch()

        client = self.root / "client.zip"
        server = self.root / "server.zip"
        with patch.object(build, "ROOT", self.root), \
                patch.object(build, "urlopen", side_effect=self.release) as api, \
                patch.object(build, "download", side_effect=download), \
                patch.object(build, "install_mods"), \
                patch.object(build.subprocess, "run", side_effect=install_neoforge):
            mods = build.rabbit_mods(self.manifest, self.root, include_server_only=True)
            build.build_client(client, mods)
            build.build_server(self.manifest, server, mods, "test-key")
        self.assertEqual(api.call_count, 4)

        with ZipFile(client) as client_zip, ZipFile(server) as server_zip:
            client_mods = {Path(name).name for name in client_zip.namelist() if name.startswith("overrides/mods/")}
            server_mods = {Path(name).name for name in server_zip.namelist() if name.startswith("mods/")}
            self.assertEqual(client_mods, {jar.name for project, jar in mods.items() if project != "RabbitAuth"})
            self.assertEqual(server_mods, {jar.name for jar in mods.values()})
            for name in client_mods:
                self.assertEqual(client_zip.read(f"overrides/mods/{name}"), server_zip.read(f"mods/{name}"))

    def test_no_release_is_reported_with_project_name(self):
        missing = HTTPError("https://api.github.com", 404, "Not Found", None, None)
        with patch.object(build, "urlopen", side_effect=missing):
            with self.assertRaisesRegex(ValueError, "RabbitCore has no published stable"):
                build.rabbit_mods(self.manifest, self.root, include_server_only=True)


if __name__ == "__main__":
    unittest.main()
