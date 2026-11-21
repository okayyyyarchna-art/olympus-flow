import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("precheck", Path(__file__).parents[1] / "tools/precheck.py")
precheck = importlib.util.module_from_spec(spec)
spec.loader.exec_module(precheck)

TEMPLATES = Path(__file__).parents[1] / "templates"

GOOD_DOCKERFILE = """FROM public.ecr.aws/d3j8x8q7/olympus-base-go:latest

# go.mod needs Go 1.27.3 and the base image has Go 1.26 (GOTOOLCHAIN=local). Install the release archive in its place.
RUN curl -fsSL -o /tmp/go.tgz https://dl.google.com/go/go1.27.3.linux-amd64.tar.gz \\
    && echo "65efbc80fdc1fa2cd2631cad5b481777a68e8725f34e89f50fc6ac714e379b40  /tmp/go.tgz" | sha256sum -c - \\
    && rm -rf /usr/local/go && tar -C /usr/local -xzf /tmp/go.tgz && rm /tmp/go.tgz
ENV PATH=/usr/local/go/bin:/opt/go/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
WORKDIR /app
COPY . .
RUN go mod download && go build ./...
RUN mkdir -p /tmp/gocache && chmod -R a+rwX /app /tmp/gocache
CMD ["/bin/bash"]
"""
BAD_DOCKERFILE = """FROM --platform=linux/amd64 public.ecr.aws/d3j8x8q7/olympus-base-go:latest
RUN curl -fsSL -o /tmp/go.tgz https://dl.google.com/go/go1.27.3.linux-amd64.tar.gz \\
    && echo "65efbc80fdc1fa2cd2631cad5b481777a68e8725f34e89f50fc6ac714e379b40  /tmp/go.tgz" | sha256sum -c - \\
    && rm -rf /usr/local/go && tar -C /usr/local -xzf /tmp/go.tgz
ENV PATH=/usr/local/go/bin:/opt/go/bin:/usr/local/bin:/usr/bin:/bin
WORKDIR /app
COPY . .
# a stray comment
ENV GOFLAGS=-buildvcs=false
RUN go mod download && go build ./... && go test -run '^$' ./...
RUN find /app -type d -exec chmod a+rx {} +
CMD ["/bin/bash"]
"""


def test_patch(files):
    """A test.patch adding the given {path: body} files."""
    parts = []
    for name, body in files.items():
        added = "".join("+" + ln + "\n" for ln in body.splitlines())
        parts.append(f"diff --git a/{name} b/{name}\nnew file mode 100755\n--- /dev/null\n+++ b/{name}\n@@ -0,0 +1,{len(body.splitlines())} @@\n{added}")
    return "".join(parts)


def run_precheck(pkg, *extra):
    output = io.StringIO()
    precheck.results.clear()
    with patch.object(sys, "argv", ["precheck", str(pkg), *extra]), contextlib.redirect_stdout(output):
        with contextlib.suppress(SystemExit):
            precheck.main()
    return output.getvalue().splitlines()


def line(lines, text):
    return next(x for x in lines if text in x)


class DescriptionLimit(unittest.TestCase):
    def test_boundaries_and_platform_ceiling(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            pkg = Path(tmp)
            for name in ("test.patch", "solution.patch"):
                (pkg / name).write_text("")
            for words, status in ((249, "PASS"), (250, "WARN"), (251, "WARN"), (1001, "WARN")):
                with self.subTest(words=words):
                    # Exercise the actual CLI check, including both hyphen and slash splitting.
                    (pkg / "description.md").write_text("a-b/c " + "word " * (words - 3))
                    lines = run_precheck(tmp)
                    self.assertTrue(line(lines, "guidance: under 250").startswith(status))
                    self.assertTrue(line(lines, "platform ceiling").startswith("FAIL" if words > 1000 else "PASS"))


class DockerfileStage(unittest.TestCase):
    def test_dockerfile_only_package_runs_the_dockerfile_rules_and_skips_the_rest(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            pkg = Path(tmp) / "pkg"
            pkg.mkdir()
            (pkg / "Dockerfile").write_text(GOOD_DOCKERFILE)
            lines = run_precheck(pkg)
            self.assertEqual(sum(1 for x in lines if x.startswith("SKIP")), 3, lines)
            for text in ("allowed FROM line", "ENV PATH keeps", "/app writable", "Go reinstall RUN has its reason block",
                         "does not run tests during build", "Dockerfile comments"):
                self.assertTrue(line(lines, text).startswith("PASS"), line(lines, text))
            self.assertIn("0 FAIL", lines[-1])

    def test_platform_blocking_dockerfile_defects_fail(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            pkg = Path(tmp) / "pkg"
            pkg.mkdir()
            (pkg / "Dockerfile").write_text(BAD_DOCKERFILE)
            lines = run_precheck(pkg)
            for text in ("allowed FROM line", "ENV PATH keeps", "/app writable", "Go reinstall RUN has its reason block",
                         "does not run tests during build"):
                self.assertTrue(line(lines, text).startswith("FAIL"), line(lines, text))
            self.assertTrue(line(lines, "Dockerfile comments").startswith("WARN"))

    def test_templates_pass_the_dockerfile_rules_except_the_unrendered_version_url(self):
        for lang in ("go", "python", "typescript"):
            with self.subTest(lang=lang), tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
                pkg = Path(tmp) / "pkg"
                pkg.mkdir()
                (pkg / "Dockerfile").write_text((TEMPLATES / lang / "Dockerfile").read_text())
                fails = [x for x in run_precheck(pkg) if x.startswith("FAIL")]
                self.assertEqual([x for x in fails if "literal versioned URL" not in x], [], fails)


class TestShWords(unittest.TestCase):
    def test_process_words_in_test_sh_are_reported_with_their_line(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            pkg = Path(tmp) / "pkg"
            pkg.mkdir()
            (pkg / "description.md").write_text("Fix it.\n")
            (pkg / "solution.patch").write_text("")
            (pkg / "Dockerfile").write_text(GOOD_DOCKERFILE)
            sh = "#!/bin/bash\n# base and new modes\nGRADE_ROOTS=1\nrestore()\n{ echo base_hidden_paths; }\nmode=new\n"
            (pkg / "test.patch").write_text(test_patch({"test.sh": sh, "pkg/x_a1b2_test.go": "package x\n"}))
            lines = run_precheck(pkg)
            hit = line(lines, "no process words in test.sh")
            self.assertTrue(hit.startswith("FAIL"), hit)
            self.assertIn("3: GRADE_ROOTS", hit)
            self.assertIn("5: hidden_paths", hit)

    def test_templates_and_accepted_examples_carry_no_hard_process_word(self):
        paths = list(TEMPLATES.glob("*/test.sh")) + list(TEMPLATES.glob("examples/*/test.sh.*"))
        self.assertGreater(len(paths), 5)
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            pkg = Path(tmp) / "pkg"
            pkg.mkdir()
            for path in paths:
                with self.subTest(path=path.name):
                    lines = run_precheck(pkg, "--test-sh", str(path))
                    self.assertTrue(line(lines, "no process words in").startswith("PASS"), line(lines, "no process words in"))


class FlaggedNames(unittest.TestCase):
    def test_codex_filter_words_in_folder_and_test_file_names_fail(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            task = Path(tmp) / "cc-pmg-bypass-counts"
            pkg = task / "pkg"
            pkg.mkdir(parents=True)
            (pkg / "description.md").write_text("Fix it.\n")
            (pkg / "solution.patch").write_text("")
            (pkg / "Dockerfile").write_text(GOOD_DOCKERFILE)
            (pkg / "test.patch").write_text(test_patch({"test.sh": "base new\n", "internal/security/exploit_9f3a_test.go": "package security\n"}))
            lines = run_precheck(pkg)
            self.assertTrue(line(lines, "folder names avoid").startswith("FAIL"))
            self.assertIn("cc-pmg-bypass-counts", line(lines, "folder names avoid"))
            self.assertTrue(line(lines, "test file names avoid").startswith("FAIL"))
            self.assertTrue(line(lines, "test folders avoid").startswith("WARN"))

    def test_clean_names_pass(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            pkg = Path(tmp) / "cc-vet-pr-accuracy" / "pkg"
            pkg.mkdir(parents=True)
            (pkg / "Dockerfile").write_text(GOOD_DOCKERFILE)
            (pkg / "test.patch").write_text(test_patch({"test.sh": "base new\n", "internal/engine/prscan_prs9_test.go": "package engine\n"}))
            lines = run_precheck(pkg)
            for text in ("folder names avoid", "test file names avoid", "test folders avoid"):
                self.assertTrue(line(lines, text).startswith("PASS"), line(lines, text))


if __name__ == "__main__":
    unittest.main()
