# Construct the environment for this repository

1. **E1 - Discover before choosing a template.** Read the pin's manifests, lockfiles,
   CI, build scripts and test extras. Record exact runtime/toolchain, package manager,
   architecture, native libraries, JUnit converter and normal development tools. Check
   the actual base image versions. An accepted template is an example, not proof it
   fits a different pin/language. Unknown languages require adapter qualification.
2. **E2 - Pin build inputs.** Use an allowed platform base; record its resolved digest
   even if the submitted form requires a tag. Use lockfiles, literal versioned fetch
   URLs and verified checksums where supplied. Prevent implicit toolchain switching.
   Materialize dependencies, test-only dependencies and reporters at build time;
   also provision the repo's declared validation tools for solver use. Respect the
   current platform's build-network/source/vendoring rules, which can differ from
   local Docker. Do not infer a requirement to rebase from a generic rebuild error.
3. **E3 - Prepare portable access.** Install tools/dependencies in uid-readable
   system locations, not private HOME paths. Separate immutable dependency inputs
   from writable scratch caches. Support the actual platform user/architecture and
   the harness's unknown-uid, empty-env execution. Include a verified pristine test
   source when Git history is unavailable. Exclude hidden answers, local scratch and
   stale build outputs from the image context; record `.dockerignore` effects.
4. **E4 - Keep image construction separate from tests.** Do not invoke a test runner
   in Dockerfile RUN, even compile-only test flags. Use package-manager dependency
   enumeration/fetch or supported build commands; run tests after building. Follow
   current platform Dockerfile rules. No comments, except one block right above a RUN
   that deviates from the base image, stating why (the AI precheck failed vet's Go
   reinstall without its "base has Go 1.26, go.mod needs 1.27.3" reason). Never ship a solution-built cached binary
   as the executable graded against later candidates.
5. **E5 - Qualify once, reuse by identity.** Build the full submitted Dockerfile through
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
