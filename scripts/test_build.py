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

    def test_client_pack_includes_manifest_overrides_and_rabbit_jars(self):
        def download(url, target):
            target.write_bytes(self.jar_bytes)

        client = self.root / "client.zip"
        with patch.object(build, "ROOT", self.root), \
                patch.object(build, "urlopen", side_effect=self.release) as api, \
                patch.object(build, "download", side_effect=download):
            mods = build.rabbit_mods(self.manifest, self.root)
            build.build_client(client, mods)
        self.assertEqual(api.call_count, 3)
        self.assertEqual(set(mods), {"RabbitCore", "RabbitTools", "RabbitMine"})

        with ZipFile(client) as client_zip:
            jar_paths = {f"overrides/mods/{jar.name}" for jar in mods.values()}
            self.assertEqual(set(client_zip.namelist()), {
                "manifest.json", "modlist.html", "overrides/config/example.txt",
            } | jar_paths)
            for name in jar_paths:
                self.assertEqual(client_zip.read(name), self.jar_bytes)

    def test_no_release_is_reported_with_project_name(self):
        missing = HTTPError("https://api.github.com", 404, "Not Found", None, None)
        with patch.object(build, "urlopen", side_effect=missing):
            with self.assertRaisesRegex(ValueError, "RabbitCore has no published stable"):
                build.rabbit_mods(self.manifest, self.root)


if __name__ == "__main__":
    unittest.main()
