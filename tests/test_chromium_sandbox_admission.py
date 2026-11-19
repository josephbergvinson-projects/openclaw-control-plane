from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ChromiumSandboxAdmissionTests(unittest.TestCase):
    def run_admission(self, directory, *, restriction=None, apparmor=None,
                      mode="", browser="/fixture/chromium/chrome"):
        root = Path(directory)
        module = root / "sys/module"
        module.mkdir(parents=True)
        if apparmor is not None:
            parameters = module / "apparmor/parameters"
            parameters.mkdir(parents=True)
            if apparmor != "unreadable":
                (parameters / "enabled").write_text(apparmor)
        restriction_file = root / "proc/sys/kernel/apparmor_restrict_unprivileged_userns"
        if restriction is not None:
            restriction_file.parent.mkdir(parents=True)
            restriction_file.write_text(restriction)
        profile = root / "etc/apparmor.d/openclaw-reference-chromium"
        profile.parent.mkdir(parents=True)
        if mode == "existing-profile":
            profile.write_text("existing profile")
        workflow = (ROOT / ".github/workflows/verify-reference.yml").read_text()
        admission = workflow.split("          # Admit only this pinned browser", 1)[1]
        admission = "          # Admit only this pinned browser" + admission.split(
            "      - name: Verify managed Chromium startup", 1)[0]
        admission = textwrap.dedent(admission)
        # Replace only kernel/filesystem boundaries; execute the actual workflow
        # shell with fake sysctl/sudo/stat, never alter the test host's policy.
        admission = admission.replace("/proc/sys/kernel/", str(root / "proc/sys/kernel") + "/")
        admission = admission.replace("/sys/module", str(module))
        admission = admission.replace("/etc/apparmor.d/", str(profile.parent) + "/")
        prelude = r'''
sysctl() {
  printf 'sysctl %s\n' "$*" >> "$FIXTURE_ROOT/calls"
  if [ "$MODE" = sysctl-failure ]; then return 1; fi
  if [ "$1" = -n ]; then
    cat "$FIXTURE_ROOT/proc/sys/kernel/apparmor_restrict_unprivileged_userns"
  else
    printf 'kernel.apparmor_restrict_unprivileged_userns = fixture\n'
  fi
}
sudo() {
  printf 'sudo %s\n' "$*" >> "$FIXTURE_ROOT/calls"
  if [ "$1" = tee ]; then
    command tee "$2"
  elif [ "$1" = apparmor_parser ]; then
    if [ "$MODE" = parser-failure ]; then return 1; fi
    if [ "$MODE" = changed-restriction ]; then
      printf '0' > "$FIXTURE_ROOT/proc/sys/kernel/apparmor_restrict_unprivileged_userns"
    fi
  else
    return 99
  fi
}
stat() {
  if [ "$MODE" = missing-sysfs ]; then printf 'tmpfs\n'; else printf 'sysfs\n'; fi
}
'''
        script = root / "admission.sh"
        script.write_text(prelude + admission)
        result = subprocess.run(["/bin/bash", "-e", str(script)], cwd=root,
                                env={"PATH": "/usr/bin:/bin", "FIXTURE_ROOT": str(root),
                                     "MODE": mode, "playwright_chromium": browser},
                                capture_output=True, text=True)
        calls = (root / "calls").read_text() if (root / "calls").exists() else ""
        return result, calls, profile

    def test_host_capabilities_preserve_restrictions_and_fail_closed(self):
        cases = [
            ("restricted", "1", "Y", "", True, True),
            ("existing-unrestricted-setting", "0", "Y", "", True, True),
            ("kernel-without-apparmor", None, None, "", True, False),
            ("kernel-disabled-apparmor", None, "N", "", True, False),
            ("enabled-with-missing-interface", None, "Y", "", False, False),
            ("unknown-apparmor-state", None, "unknown", "", False, False),
            ("unreadable-apparmor-state", None, "unreadable", "", False, False),
            ("missing-kernel-interfaces", None, None, "missing-sysfs", False, False),
            ("sysctl-read-failure", "1", "Y", "sysctl-failure", False, False),
            ("profile-load-failure", "1", "Y", "parser-failure", False, True),
            ("restriction-changed", "1", "Y", "changed-restriction", False, True),
            ("preexisting-policy", "1", "Y", "existing-profile", False, False),
        ]
        for name, restriction, apparmor, mode, success, loaded in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                result, calls, profile = self.run_admission(
                    directory, restriction=restriction, apparmor=apparmor, mode=mode)
                self.assertEqual(success, result.returncode == 0, result.stdout + result.stderr)
                self.assertEqual(loaded, "sudo apparmor_parser -r" in calls)
                self.assertNotIn("sysctl -w", calls)
                if restriction is None:
                    self.assertEqual("", calls)
                    self.assertFalse(profile.exists())
                elif success:
                    self.assertIn('profile openclaw-reference-chromium "/fixture/chromium/chrome"',
                                  profile.read_text())
                    self.assertIn("userns,", profile.read_text())
                    self.assertEqual(restriction, (Path(directory) /
                        "proc/sys/kernel/apparmor_restrict_unprivileged_userns").read_text())
                elif mode == "existing-profile":
                    self.assertEqual("existing profile", profile.read_text())

    def test_unsafe_browser_path_fails_before_policy_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            result, calls, profile = self.run_admission(
                directory, restriction="1", apparmor="Y", browser='/fixture/chrome" bad')
            self.assertNotEqual(0, result.returncode)
            self.assertEqual("", calls)
            self.assertFalse(profile.exists())

    def test_sandbox_startup_remains_an_unconditional_gate_before_build(self):
        workflow = (ROOT / ".github/workflows/verify-reference.yml").read_text()
        startup = workflow.split("      - name: Verify managed Chromium startup\n", 1)[1]
        startup = startup.split("      - name: Build the reconstructed runtime\n", 1)[0]
        self.assertIn("chromiumSandbox: true", startup)
        self.assertIn("const browser = await chromium.launch({", startup)
        self.assertNotIn("if:", startup)
        self.assertNotIn("continue-on-error", startup)
        self.assertNotIn("--no-sandbox", startup)


if __name__ == "__main__":
    unittest.main()
