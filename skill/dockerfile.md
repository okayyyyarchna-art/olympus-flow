# Construct the environment for this repository

1. **E1 - Discover before choosing a template.** Read the pin's manifests, lockfiles,
   CI, build scripts and test extras. Record exact runtime/toolchain, package manager,
   architecture, native libraries, JUnit converter and normal development tools. Check
   the actual base image versions. An accepted template is an example, not proof it
   fits a different pin/language. Unknown languages require adapter qualification.
2. **E2 - Pin build inputs.** The first line is one of the platform's allowed FROM lines,
   verbatim and bare: `FROM public.ecr.aws/x8v8d7g8/mars-base:latest`,
   `FROM public.ecr.aws/d3j8x8q7/olympus-base:latest` or
   `FROM public.ecr.aws/d3j8x8q7/olympus-base-go:latest` (no `--platform=`: the platform
   check rejects it; the local proof passes the platform to docker build itself).
   Record the base's resolved digest. Use lockfiles, literal versioned fetch
   URLs and verified checksums where supplied. Prevent implicit toolchain switching.
   Materialize dependencies, test-only dependencies and reporters at build time;
   also provision the repo's declared validation tools for solver use. Respect the
   current platform's build-network/source/vendoring rules, which can differ from
   local Docker. Do not infer a requirement to rebase from a generic rebuild error.
3. **E3 - Prepare portable access.** Install tools/dependencies in uid-readable
   system locations, not private HOME paths. Separate immutable dependency inputs
   from writable scratch caches. Support the actual platform user/architecture and
   the harness's unknown-uid, empty-env execution: the platform's verify step runs
   `groupadd`/`useradd` (uid 1000 `model`) and `chown -R model:model /app`, so any
   `ENV PATH` keeps `/usr/local/sbin:/usr/sbin:/sbin`, and the build ends with
   `chmod -R a+rwX /app` plus the caches it created (the Harbor oracle applies
   solution.patch in /app as uid 1000; without it verifySolution fails as
   `harbor_oracle_failed` with no detail). Include a verified pristine test
   source when Git history is unavailable. Exclude hidden answers, local scratch and
   stale build outputs from the image context; record `.dockerignore` effects.
4. **E4 - Keep image construction separate from tests.** Do not invoke a test runner
   in Dockerfile RUN, even compile-only test flags. Use package-manager dependency
   enumeration/fetch or supported build commands; run tests after building. Follow
   current platform Dockerfile rules. No comments, except one block right above each RUN
   that deviates from the base image, stating why (the AI precheck failed vet's Go
   reinstall without its "base has Go 1.26, go.mod needs 1.27.3" reason; the accepted
   vet 6 Dockerfile carries three such blocks: Go reinstall, the CI linter, a git
   wrapper fix). `tools/precheck.py <pkg>` enforces the FROM line, the comment rule, the
   PATH and the /app permissions on pkg/Dockerfile alone at stage 1. Never ship a
   solution-built cached binary as the executable graded against later candidates. Start
   from the newest platform-accepted Dockerfile of the language in templates/examples/
   (vet 6 for Go) and change only what the pin needs; the accepted Python examples still
   say `olympus-base-python`, which the FROM check no longer allows: copy them with
   `olympus-base:latest` and the /app chmod.
5. **E5 - Qualify once, reuse by identity.** Never reorder or edit the Dockerfile for local cache speed: the platform builds it from scratch. Build the full submitted Dockerfile through
   the configured lock. Key reuse by Dockerfile + source/context + resolved base image
   + platform + toolchain/dependency identities, not just a tag or HEAD. Run H6 offline
   after build, then obtain the **human's platform build result**. Record local and
   platform proof separately. A changed image/input invalidates environment-dependent
   evidence. Repair a pasted environment in a new version, never in its frozen folder.

## Pre-submit self-check, in priority order

| Gate | Evidence required |
|---|---|
| Auto Review T1/T6/T8, environment prechecks | Full build succeeds; no test runner in RUN; test.sh finds tools offline under unknown uid/cleared environment; exact source and dependencies identified. |
| False pass | No stale reference binaries, hidden answers or untracked cache shadows; effective candidate build checked; image change triggers replay and current proof. |
| Solution Quality | Native build/format/lint/type tools are usable; failures are diagnosed as code or environment, not silently ignored. |
| Task Quality | Normal solver validation is provisioned; fakes do not substitute for missing supported modes; image build/rebuild evidence is current. |

A local build cannot certify Harbor rebuild, platform network policy or mutable-image
availability. Until the human supplies those results they are **NOT VERIFIED**. No
Docker cleanup or shared-environment edits are authorized by this card.
