# TypeScript adapter: UNPROVEN

Derived from H1-H6/E1-E5 construction cards only. No task has proved this template
on the platform. Keep this status until a real task passes and records its identity.

Template markers: `toolchain_version`, `package_manager_install`,
`fetch_command`, `development_install` (Dockerfile) and `profile_json` (test.sh:
a readable, indented JSON object; the older `profile_b64` marker is no longer
read). The Dockerfile starts with the bare
`FROM public.ecr.aws/d3j8x8q7/olympus-base:latest` (the platform's allowed list;
no node image exists on it, so the Node runtime of that base is NOT VERIFIED)
and ends with `chmod -R a+rwX /app`. test.sh accepts
`[--output_path <junit.xml>] [--mode] <base|new>` in any order (mode default
base, output path optional, exit 2 on a malformed argument) and prints Vitest's
normal text. The runner requires Python at /usr/local/bin/python.

The image executes `npm ci` or `pnpm install --frozen-lockfile` at build time and
copies immutable installed dependencies outside /app so mounting candidate source
does not hide them. Pin pnpm/corepack explicitly with `package_manager_install`.
Lock a Vitest version with its built-in JUnit reporter. Run lint/types tooling
from the repository's scripts; ensure its dependencies are in the lockfile.

The initial native recipe is Vitest only. Discovery finds Jest as well and records
its reporter/adapter qualification as OPEN; it does not silently switch frameworks.
The Vitest recipe qualifies canonical IDs from a successful baseline JUnit run,
then filters exact file/name patterns for a single ID. It preserves the native
JUnit classname/name. Suite-name separators, custom reporters, multi-project names,
dynamic cases, compiled output and package exports require real qualification.

Native enumeration is documented by [Vitest CLI](https://vitest.dev/guide/cli)
(`vitest list --json`); reporter flags follow
[Vitest reporters](https://vitest.dev/guide/reporters). This draft uses a successful
baseline JUnit run to qualify the reporter's actual IDs, which also executes tests.
Older versions and custom JUnit naming need their own adapter before acceptance.

Supply nonempty provisional `expected.base` IDs in settings before repo_check.
Review test-helper/config restoration and compiled twins. Author new-mode IDs,
selectors and overlays separately. Missing inputs, unsupported frameworks and
reporter failures produce nonzero results; none is treated as platform proof.

For feature mode, run `test.sh new --discover` on a successful reference tree and
supply its returned map as `new_native_ids` in settings, alongside `expected.new`.
Execution uses that predeclared map and preserves native assertion outcomes on base;
it never learns IDs by running failing feature cases. Without the map it fails closed.
