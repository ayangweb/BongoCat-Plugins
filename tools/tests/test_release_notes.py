import tempfile
import unittest
from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "release_notes", ROOT / "tools" / "release_notes.py"
)
notes = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(notes)


class ReleaseNotesTests(unittest.TestCase):
    def test_current_manifests_have_bilingual_entries(self):
        names = notes.validate(ROOT)
        self.assertEqual(
            set(names),
            {
                "com.bongocat.input-source",
                "com.bongocat.key-sounds",
                "com.bongocat.pomodoro",
            },
        )

    def test_render_is_plugin_only_and_deterministic(self):
        rendered = notes.render(ROOT, "v1.0.0")
        self.assertIn("BongoCat Plugins v1.0.0", rendered)
        self.assertIn("com.bongocat.key-sounds", rendered)
        self.assertNotIn("latest.json", rendered)

    def test_changelogs_live_at_the_repository_root(self):
        self.assertTrue((ROOT / "CHANGELOG.md").is_file())
        self.assertTrue((ROOT / "CHANGELOG.zh-CN.md").is_file())
        self.assertFalse((ROOT / "plugins" / "CHANGELOG.md").exists())
        self.assertFalse((ROOT / "plugins" / "CHANGELOG.zh-CN.md").exists())

    def test_unknown_plugin_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "plugins").mkdir()
            with self.assertRaisesRegex(ValueError, "no plugin manifests"):
                notes.validate(root)


if __name__ == "__main__":
    unittest.main()
