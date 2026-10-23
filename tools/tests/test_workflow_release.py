import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")


class WorkflowReleaseTests(unittest.TestCase):
    def test_workflow_is_tag_only(self):
        self.assertIn('on:\n  push:\n    tags:\n      - "v*"', WORKFLOW)
        self.assertNotIn("workflow_dispatch", WORKFLOW)
        self.assertNotIn("branches:", WORKFLOW)
        self.assertNotIn("workflow_run", WORKFLOW)

    def test_tag_membership_uses_ancestor_check(self):
        self.assertIn(
            'git merge-base --is-ancestor "$tag" refs/remotes/origin/master', WORKFLOW
        )
        self.assertNotIn('git rev-list --count "$tag"..origin/master', WORKFLOW)

    def test_release_is_drafted_verified_and_then_published(self):
        draft = WORKFLOW.index("--draft")
        verify = WORKFLOW.index("Verify the draft before exposing it")
        publish = WORKFLOW.index("Publish the verified release")
        self.assertLess(draft, verify)
        self.assertLess(verify, publish)
        self.assertIn('gh release edit "$RELEASE_TAG"', WORKFLOW)
        self.assertIn("--draft=false", WORKFLOW)

    def test_every_matrix_target_and_asset_is_checked(self):
        for platform in [
            "macos-aarch64",
            "macos-x86_64",
            "windows-x86_64",
        ]:
            self.assertGreaterEqual(WORKFLOW.count(platform), 3)
        self.assertIn("for required in plugins.json release-state.json", WORKFLOW)
        self.assertIn("for asset in plugin-assets/*.zip", WORKFLOW)
        self.assertGreaterEqual(WORKFLOW.count("cargo run --locked -p bongocat-plugin-packaging -- verify"), 2)

    def test_publish_permissions_are_scoped(self):
        self.assertIn("permissions:\n  contents: read", WORKFLOW)
        self.assertIn(
            "permissions:\n      contents: write\n      actions: read", WORKFLOW
        )
        self.assertEqual(len(re.findall(r"contents: write", WORKFLOW)), 1)

    def test_workflow_does_not_reference_the_application_release(self):
        for forbidden in [
            "BongoCat/releases",
            "latest.json",
            "secrets.SIGNING_PRIVATE_KEY",
            "secrets.RELEASE_SIGNING_KEY",
        ]:
            self.assertNotIn(forbidden, WORKFLOW)

    def test_validation_installs_every_tool_it_invokes(self):
        self.assertIn("components: clippy,rustfmt", WORKFLOW)
        self.assertIn("cargo install cargo-deny --version 0.20.2 --locked", WORKFLOW)
        self.assertLess(
            WORKFLOW.index("Install pinned cargo-deny"),
            WORKFLOW.index("cargo deny --locked check licenses sources bans"),
        )


if __name__ == "__main__":
    unittest.main()
