# TypeScript adapter: UNPROVEN

Derived from H1-H6/E1-E5 construction cards only. No task has proved this template
on the platform. Keep this status until a real task passes and records its identity.

Template markers: `platform`, `toolchain_version`, `package_manager_install`,
`fetch_command`, `development_install`, `profile_b64`. Select a currently allowed
platform base and verify its exact Node/Python runtime. The proposed node base
name is NOT VERIFIED. The runner requires Python at /usr/local/bin/python.

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
