import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS = [
    ROOT / "README.md",
    ROOT / "README.zh-CN.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "CONTRIBUTING.zh-CN.md",
    ROOT / "CHANGELOG.md",
    ROOT / "CHANGELOG.zh-CN.md",
    ROOT / "AGENTS.md",
]
MARKDOWN_LINK = re.compile(r"\]\(([^)]+)\)")
HTML_IMAGE = re.compile(r'<img\s+[^>]*src="([^"]+)"')


def local_target(target):
    target = target.strip().strip("<>")
    if target.startswith(("https://", "http://", "mailto:", "#")):
        return None
    return target.split("#", 1)[0]


class DocumentationTests(unittest.TestCase):
    def test_required_documents_and_language_links_exist(self):
        for document in DOCUMENTS:
            self.assertTrue(document.is_file(), document)

        pairs = [
            (ROOT / "README.md", ROOT / "README.zh-CN.md"),
            (ROOT / "CONTRIBUTING.md", ROOT / "CONTRIBUTING.zh-CN.md"),
        ]
        for english, chinese in pairs:
            self.assertIn(chinese.name, english.read_text(encoding="utf-8"))
            self.assertIn(english.name, chinese.read_text(encoding="utf-8"))

        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("CONTRIBUTING.zh-CN.md", agents)
        self.assertIn("just check", agents)
        self.assertIn("cargo test --locked --workspace", agents)

    def test_local_links_and_images_resolve(self):
        for document in DOCUMENTS:
            text = document.read_text(encoding="utf-8")
            targets = MARKDOWN_LINK.findall(text) + HTML_IMAGE.findall(text)
            for target in targets:
                relative = local_target(target)
                if relative is None:
                    continue
                with self.subTest(document=document.name, target=target):
                    self.assertTrue((ROOT / relative).exists(), target)

    def test_readmes_list_every_plugin_with_its_real_icon_and_copy(self):
        manifests = sorted((ROOT / "plugins").glob("*/plugin.json"))
        self.assertGreater(len(manifests), 0)

        for readme, locale in [
            (ROOT / "README.md", "en"),
            (ROOT / "README.zh-CN.md", "zh-CN"),
        ]:
            text = readme.read_text(encoding="utf-8")
            rows = [
                line
                for line in text.splitlines()
                if "<img src=" in line and "resources/icon.png" in line
            ]
            self.assertEqual(len(rows), len(manifests), readme)

            for manifest_path in manifests:
                metadata = json.loads(manifest_path.read_text(encoding="utf-8"))[
                    "metadata"
                ]
                directory = manifest_path.parent.name
                icon = metadata["icon"]["value"]
                if locale == "zh-CN":
                    name = metadata["localizations"]["zh-CN"]["name"]
                    description = metadata["localizations"]["zh-CN"]["description"]
                else:
                    name = metadata["name"]
                    description = metadata["description"]

                matching = [
                    row for row in rows if f'src="plugins/{directory}/{icon}"' in row
                ]
                self.assertEqual(len(matching), 1, (readme, directory))
                row = matching[0]
                self.assertIn(f"[{name}](plugins/{directory})", row)
                self.assertIn(description, row)


if __name__ == "__main__":
    unittest.main()
