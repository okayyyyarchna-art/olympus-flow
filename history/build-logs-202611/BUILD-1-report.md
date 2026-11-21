Verdict: PASS with native macOS hardware unverified; created/changed: `machine/schema.md`, `machine/windows-asus.json`, `machine/mac.example.json`, `skill/tools/machine.py`, `skill/tools/machine.sh`, `skill/tools/proof.py`, `skill/tools/solvers.sh`, `skill/tools/stop_solves.sh`, `skill/tools/solve_watch.py`, `skill/tools/replica.sh`, `skill/tools/round.sh`, `skill/tools/sweep.sh`, `skill/tools/watch.sh`, `skill/tools/pull.sh`, `skill/tools/hunt.sh`, `skill/tools/lib/codex_job.sh`, `skill/tools/lib/claude2_run.sh`, `skill/tools/lib/replay_patches.sh`, `skill/tools/lib/dockrun.py`, `skill/references/seam-bank.md`, `install.sh`, `README.md`, `BUILD-1-report.md`; scratch evidence: `.build1/`.

# Build 1 report

Work stayed in this product checkout. No live installation was performed. The live `.claude` and `OSS/shipd` copies and challenge/package folders were not modified. `FLOW.md` is unchanged; the sole reference edit is a moved helper path. Existing `BUILD-1-codex.log` and `eval/` were left to the coordinator.

Commits: `8b84794` (profiles/loaders), `0298b2d` (portable workflow tools), followed by the installer/documentation/report commit. No push was performed.

## Changes by file

| File | Change |
| --- | --- |
| `machine/schema.md` | Document selection, fields, defaults, overrides and the shared lock location. |
| `machine/windows-asus.json` | Record existing Windows paths, Python/CLI binaries, two Docker slots, amd64 and four solves. |
| `machine/mac.example.json` | Provide a home-relative Apple Silicon example: arm64 daily, amd64 final, eight Docker slots. |
| `skill/tools/machine.py` | Validate and load a selected profile; expose load(), dotted-key CLI and safely quoted shell exports. |
| `skill/tools/machine.sh` | Export profile settings and local helper paths; gate cygpath and Docker MSYS handling on Windows. |
| `skill/tools/proof.py` | Use the bundled dockrun helper and profile scratch roots/platforms; separate arm64 image tags; add --final and isolated --work-root; keep Windows stability serial. |
| `skill/tools/solvers.sh` | Use configured binaries/config/clone roots and solve count; retain Windows tree PID recording; give POSIX solves independent groups with foreground timeout. |
| `skill/tools/stop_solves.sh` | Select Windows taskkill tree termination or POSIX process-group termination from the profile. |
| `skill/tools/solve_watch.py` | Read configured transcript/solver roots; support clone paths with spaces and POSIX case-sensitive matching. |
| `skill/tools/replica.sh` | Load the profile and use bundled brief-check/Codex helpers; normalize this existing CRLF script to LF. |
| `skill/tools/round.sh` | Load Python/work root/review round limit from the profile; retain per-run ROUND_SLOTS override. |
| `skill/tools/sweep.sh` | Load the profile and resolve brief-check/Claude helpers under tools/lib. |
| `skill/tools/watch.sh` | Load the configured Python interpreter; retain platform polling commands. |
| `skill/tools/pull.sh` | Load the configured Python interpreter; retain artifact/pull commands. |
| `skill/tools/hunt.sh` | Use configured seam/shared-list roots and bundled helpers; remove the separate Mac-specific helper lookup. |
| `skill/tools/lib/codex_job.sh` | Use configured Codex binary/home and memory path; point generated probe instructions to bundled dockrun. |
| `skill/tools/lib/claude2_run.sh` | Use configured Claude/config/memory/cwd paths; generate OS-appropriate mount instructions and use bundled dockrun. |
| `skill/tools/lib/replay_patches.sh` | Use configured Python and bundled dockrun; apply MSYS/cygpath only for Windows. |
| `skill/tools/lib/dockrun.py` | Default slot count to docker.slots; retain DOCKRUN_SLOTS override and native OS locking; apply MSYS env only for Windows. |
| `skill/references/seam-bank.md` | Change only the moved codex_job.sh helper path; retain all rule text. |
| `install.sh` | Preflight a complete file diff before any write; support named profiles, local profile creation, --dry-run, --force and isolated --home. |
| `README.md` | Describe the product, Windows/Mac installation, profiles, architecture choices and shared-rule/per-machine-layer rule. |
| `BUILD-1-report.md` | Record changes, command evidence, checks and remaining portability limits. |

Tools without machine-specific values (`digest.py`, `precheck.py`, `summarize.py`, `tests_lint.py`, `watch_snap.py`, `lib/check_codex_brief.sh`) remain unchanged.

## Windows compatibility

Default roots were checked against the old Python constants and shell expressions. The profile preserves the existing paths:

| Setting | Before and after |
| --- | --- |
| Task root | `C:/Users/ASUS/OSS/claude-code/challenges` |
| Proof scratch/context | `C:/Users/ASUS/OSS/shipd/proof-work`, `C:/Users/ASUS/OSS/shipd/proof-ctx` |
| Solver clones | `C:/Users/ASUS/vp-<task>-<n>-<run>/work` |
| Seam workspace | `C:/Users/ASUS/OSS/shipd/seams/work/<repo>` |
| Round slots | `C:/Users/ASUS/OSS/shipd/.round-slots` |
| Claude main/second transcripts | `C:/Users/ASUS/.claude/projects`, `C:/Users/ASUS/.claude-cli/projects` |
| Codex sessions | `C:/Users/ASUS/.codex/sessions` |
| Daily/final platform | `linux/amd64` |
| Docker limit / default solves / replica-round limit | `2` / `4` / `2` |

Executable spelling is now selected by the profile. `python` resolves to the same Python executable that the old proof used as `sys.executable`; the Claude executable is the existing `.local/bin/claude.exe`, and Codex remains `codex`. Helper locations intentionally change from `OSS/shipd/tools` to this product's `skill/tools/lib`. The product helper has its own lock file; all cooperating product sessions must use that same installed helper.

The before/after command appendix contains exact echo-mode argv captured by running the preserved pre-edit scripts and the refactored scripts. External CLIs and heavy helper launches were stubbed; actual Bash control flow, profile loading, fixture git clones, prompt generation and report handling ran. To avoid touching live workspaces, the shell checks used copies of the Windows profile with all home/work/bin paths redirected into `.build1/smoke-before` and `.build1/smoke-windows`. These fixture prefixes and timestamp/PID differences are visible, rather than presented as live execution. The default Windows profile itself was used for the real proof and Python command/root comparison. The macOS echo pass used a scratch macOS profile and a cygpath stub that fails if called.

Windows timeout flags, model/effort flags, taskkill flags, replay Docker flags and container shell bodies remain the same. The pre-existing extra `n` argument in the Opus solve command is visible in both traces and was retained for Windows command parity.

## Required verification

All commands ran from the product root. Syntax and compile checks covered all 14 product shell scripts (including install.sh) and all 9 product Python files:

```text
bash -n: 14 files PASS
python -m py_compile: 9 files PASS
git diff --check: PASS
```

The two cheap vet checks were compared as raw stdout/stderr bytes and return codes against the live `.claude/skills/olympus-flow/tools` copies. Both source files are also byte-identical to their live versions. Commands and output:

```text
bash -n: 14 files PASS
python -m py_compile: 9 files PASS
COMMAND: python skill/tools/precheck.py C:\Users\ASUS\OSS\claude-code\challenges\cc-vet-unused-suppression\pkg --category feature_request
precheck.py: output byte-identical to live; exit=0
PASS description ASCII only
PASS description has no URLs or scheme://
PASS description site words (split on space - /): 147
PASS description not hard-wrapped (AI-look precheck)
PASS no em-dashes
PASS no rule-sheet lists: 0 list lines
PASS AI-look hygiene (no backticks, no semicolons, <= 0.9 commas / 20 words): backticks 0, semicolons 0, commas/20w 0.27
PASS no 'Should ...' directive list: 0 lines start with Should
PASS no process instructions to the solver (DQ inferable)
WARN category matches description shape: chosen feature_request, shape suggests bugfix
PASS test.patch adds test.sh
PASS test.sh has distinct base and new modes
PASS test.sh is executable (100755)
PASS no malformed hunk headers: 0 '+@@' lines
PASS no process words in test.patch (AR Tests Blocker)
PASS test file names not predictable (add a short hash suffix)
PASS no stray files in test.patch
PASS solution.patch and test.patch touch different files
PASS solution.patch adds no tests
PASS no stray files in solution.patch
PASS test.patch added lines ASCII: 0 lines with non-ASCII
PASS solution.patch added lines ASCII: 0 lines with non-ASCII
PASS test.patch deletes no file
PASS solution.patch deletes no file
PASS no grader-directed comments in solution (AR S4)
PASS Dockerfile does not run tests during build
PASS Go toolchain installed explicitly (pinned + SHA-256), not only GOTOOLCHAIN
PASS build-time downloads use a literal versioned URL (Harbor rebuild-safe)
WARN no comments in the Dockerfile (user rule): 11 comment lines
PASS FROM the platform base image (public.ecr.aws/d3j8x8q7/olympus-base-<lang>:latest)
PASS Dockerfile builds from the checked-out repo (no clone)
0 FAIL, 2 WARN
COMMAND: python skill/tools/tests_lint.py C:\Users\ASUS\OSS\claude-code\challenges\cc-vet-unused-suppression\pkg C:\Users\ASUS\OSS\claude-code\challenges\cc-vet-unused-suppression\repo
tests_lint.py: output byte-identical to live; exit=0
PASS   tests lint: no recurring platform pattern found
0 FAIL, 0 REVIEW
profile windows-asus: linux/amd64
profile windows-asus.json: linux/amd64
profile C:\Users\ASUS\OSS\olympus-product\machine\windows-asus.json: linux/amd64
profile mac.example: linux/arm64
missing profile: exit 2 with actionable message PASS
```

The required real proof ran with the unmodified Windows profile and a one-container override:

```bash
export OLYMPUS_MACHINE=machine/windows-asus.json
export DOCKRUN_SLOTS=1
python skill/tools/proof.py C:/Users/ASUS/OSS/claude-code/challenges/cc-vet-unused-suppression/base C:/Users/ASUS/OSS/claude-code/challenges/cc-vet-unused-suppression/pkg --build-only --work-root C:/Users/ASUS/OSS/olympus-product/.build1/proof
```

`--work-root` was necessary to honor the brief's ban on writes to the live `OSS/shipd` copy. It changes host scratch placement only; the default profile still resolves to the original proof-work/proof-ctx paths.

```text
PASS  1 image builds (reused olympus-proof-cc-vet-unused-suppression:4aea4557e1d5: same Dockerfile and base commit)
PASS  2a without solution: base passes ({'pass': 295, 'fail': 0, 'skip': 0})

image: olympus-proof-cc-vet-unused-suppression:4aea4557e1d5
artifacts: C:\Users\ASUS\OSS\olympus-product\.build1\proof\proof-work\proof-627hm7db
PROOF PASS
```

The reused image was inspected through the bundled lock: architecture `amd64`, ID `sha256:108b88226fbd93a1e1960ef14176442ae7226de888e49f2245a15de20ff2b98e`. No image rebuild, Docker removal or pruning was performed. Real verification containers ran sequentially through `lib/dockrun.py` with `DOCKRUN_SLOTS=1`.

## Additional verification

```text
before: 11 shell tools PASS (external services echoed; writes confined to scratch)
windows: 11 shell tools PASS (external services echoed; writes confined to scratch)
macos: 11 shell tools PASS (external services echoed; writes confined to scratch)
Windows msvcrt lock PASS: max active=2 (profile=2, DOCKRUN_SLOTS=None)
Windows msvcrt lock PASS: max active=1 (profile=2, DOCKRUN_SLOTS=1)
bad-os: rejected PASS
bad-slots: rejected PASS
bad-final: rejected PASS
bad-bool: rejected PASS
bad-required: rejected PASS
machine.py: missing profile fails clearly PASS
proof.py: missing profile fails clearly PASS
solve_watch.py: missing profile fails clearly PASS
lib/dockrun.py: missing profile fails clearly PASS
optional claude2 omitted: clears inherited value; shell does not globally disable MSYS conversion PASS
Installer PASS: dry run writes nothing; full copy; local creation; installed loader; idempotency; conflict preflight; force preview/apply.
```

Installer checks ran only under `.build1/install-home*` from copied source trees. The installed loader was invoked from a different cwd with no OLYMPUS_MACHINE and correctly found its installed machine/local.json. A conflict plus a missing agent caused a full preflight refusal before either destination was changed. Forced dry run still changed nothing; forced application restored the conflicting tool and missing agent.

Selected installer output:

```text
ADD    C:\Users\ASUS\OSS\olympus-product\.build1\install-home-current\.claude\skills\olympus-flow\machine\schema.md (3751 bytes)
ADD    C:\Users\ASUS\OSS\olympus-product\.build1\install-home-current\.claude\skills\olympus-flow\machine\windows-asus.json (852 bytes)
ADD    C:\Users\ASUS\OSS\olympus-product\.build1\install-source-current\machine\local.json (852 bytes)
ADD    C:\Users\ASUS\OSS\olympus-product\.build1\install-home-current\.claude\skills\olympus-flow\machine\local.json (852 bytes)
Diff summary: 77 files, 0 existing files differ.
Installed Olympus Flow at C:\Users\ASUS\OSS\olympus-product\.build1\install-home-current\.claude\skills\olympus-flow

$ bash install.sh --home <scratch>
Diff summary: 0 files, 0 existing files differ.
Installed Olympus Flow at C:\Users\ASUS\OSS\olympus-product\.build1\install-home-current\.claude\skills\olympus-flow

$ bash install.sh --home <scratch>
CHANGE C:\Users\ASUS\OSS\olympus-product\.build1\install-home-current\.claude\skills\olympus-flow\tools\precheck.py (+153/-1 lines)
ADD    C:\Users\ASUS\OSS\olympus-product\.build1\install-home-current\.claude\agents\olympus-tq-judge.md (56089 bytes)
Diff summary: 2 files, 1 existing files differ.
Existing files require --force; no files will be written.

$ bash install.sh --home <scratch> --force --dry-run
CHANGE C:\Users\ASUS\OSS\olympus-product\.build1\install-home-current\.claude\skills\olympus-flow\tools\precheck.py (+153/-1 lines)
ADD    C:\Users\ASUS\OSS\olympus-product\.build1\install-home-current\.claude\agents\olympus-tq-judge.md (56089 bytes)
Diff summary: 2 files, 1 existing files differ.
Dry run: no files written.

$ bash install.sh --home <scratch> --force
CHANGE C:\Users\ASUS\OSS\olympus-product\.build1\install-home-current\.claude\skills\olympus-flow\tools\precheck.py (+153/-1 lines)
ADD    C:\Users\ASUS\OSS\olympus-product\.build1\install-home-current\.claude\agents\olympus-tq-judge.md (56089 bytes)
Diff summary: 2 files, 1 existing files differ.
Installed Olympus Flow at C:\Users\ASUS\OSS\olympus-product\.build1\install-home-current\.claude\skills\olympus-flow
```

A read-only source mount in the existing vet image exercised actual Linux/POSIX process groups and fcntl locking. Docker itself was stubbed inside the lock concurrency checks, so those checks did not start nested containers. The first process-group probe exposed timeout creating a separate group; POSIX-only --foreground fixed it. Final runtime/orchestration output:

```text
ÿþs t o p p e d   / t m p / m a c h i n e - c h e c k - j o y p h j n 9 / t a s k / s o l v e s / s 1   ( t r e e   2 8 ) 
 
 P O S I X   s o l v e   s t o p   P A S S :   s e p a r a t e   s a v e d   P G I D ,   C l a u d e   s t u b   a n d   i t s   s l e e p   c h i l d   b o t h   t e r m i n a t e d 
 
 P O S I X   d o c k r u n   l o c k   P A S S :   m a x   a c t i v e = 2   ( p r o f i l e = 2 ,   D O C K R U N _ S L O T S = N o n e ) 
 
 P O S I X   d o c k r u n   l o c k   P A S S :   m a x   a c t i v e = 1   ( p r o f i l e = 2 ,   D O C K R U N _ S L O T S = 1 ) 
 
 P A S S     1   i m a g e   b u i l d s   ( r e u s e d   o l y m p u s - p r o o f - t a s k : 0 9 e 5 c 8 8 e b 0 8 7 - a r m 6 4 :   s a m e   D o c k e r f i l e   a n d   b a s e   c o m m i t ) 
 
 P A S S     2 a   w i t h o u t   s o l u t i o n :   b a s e   p a s s e s   ( { ' p a s s ' :   1 ,   ' f a i l ' :   0 ,   ' s k i p ' :   0 } ) 
 
 
 
 i m a g e :   o l y m p u s - p r o o f - t a s k : 0 9 e 5 c 8 8 e b 0 8 7 - a r m 6 4 
 
 a r t i f a c t s :   / t m p / m a c h i n e - c h e c k - j o y p h j n 9 / h o m e / O S S / o l y m p u s - w o r k / p r o o f - w o r k / p r o o f - 1 p z 1 t 3 p i 
 
 P R O O F   P A S S 
 
 P r o o f   o r c h e s t r a t i o n   P A S S :   [ ' - - b u i l d - o n l y ' ] ,   l i n u x / a r m 6 4 ,   i m a g e   s u f f i x = ' - a r m 6 4 ' 
 
 P A S S     1   i m a g e   b u i l d s   ( r e u s e d   o l y m p u s - p r o o f - t a s k : 0 9 e 5 c 8 8 e b 0 8 7 :   s a m e   D o c k e r f i l e   a n d   b a s e   c o m m i t ) 
 
 P A S S     2 a   w i t h o u t   s o l u t i o n :   b a s e   p a s s e s   ( { ' p a s s ' :   1 ,   ' f a i l ' :   0 ,   ' s k i p ' :   0 } ) 
 
 
 
 i m a g e :   o l y m p u s - p r o o f - t a s k : 0 9 e 5 c 8 8 e b 0 8 7 
 
 a r t i f a c t s :   / t m p / m a c h i n e - c h e c k - j o y p h j n 9 / h o m e / O S S / o l y m p u s - w o r k / p r o o f - w o r k / p r o o f - m y e e n b o 7 
 
 P R O O F   P A S S 
 
 P r o o f   o r c h e s t r a t i o n   P A S S :   [ ' - - f i n a l ' ,   ' - - b u i l d - o n l y ' ] ,   l i n u x / a m d 6 4 ,   i m a g e   s u f f i x = ' ' 
 
 P A S S     1   i m a g e   b u i l d s   ( r e u s e d   o l y m p u s - p r o o f - t a s k : 0 9 e 5 c 8 8 e b 0 8 7 :   s a m e   D o c k e r f i l e   a n d   b a s e   c o m m i t ) 
 
 P A S S     2 a   w i t h o u t   s o l u t i o n :   b a s e   p a s s e s   ( { ' p a s s ' :   1 ,   ' f a i l ' :   0 ,   ' s k i p ' :   0 } ) 
 
 P A S S     2 b   w i t h o u t   s o l u t i o n :   e v e r y   n e w   t e s t   f a i l s   ( { ' p a s s ' :   0 ,   ' f a i l ' :   1 ,   ' s k i p ' :   0 } ) 
 
 P A S S     2 c   c l e a n   n e w   r u n   0   s   ( <   3 0 0   s ) 
 
 P A S S     3   w i t h   s o l u t i o n   r u n   1 :   b a s e   { ' p a s s ' :   1 ,   ' f a i l ' :   0 ,   ' s k i p ' :   0 } ,   n e w   { ' p a s s ' :   1 ,   ' f a i l ' :   0 ,   ' s k i p ' :   0 } 
 
 P A S S     3   w i t h   s o l u t i o n   r u n   2 :   b a s e   { ' p a s s ' :   1 ,   ' f a i l ' :   0 ,   ' s k i p ' :   0 } ,   n e w   { ' p a s s ' :   1 ,   ' f a i l ' :   0 ,   ' s k i p ' :   0 } 
 
 P A S S     3   i d e n t i c a l   r e s u l t s   b e t w e e n   t h e   t w o   s o l u t i o n   r u n s 
 
 P A S S     4   a s   u i d   1 2 3 4 5   w i t h   e n v   - i :   n e w   { ' p a s s ' :   1 ,   ' f a i l ' :   0 ,   ' s k i p ' :   0 } 
 
 P A S S     5   u n s o l v e d :   6   r u n s   i d e n t i c a l 
 
 P A S S     5   s o l v e d :   6   r u n s   i d e n t i c a l 
 
 
 
 i m a g e :   o l y m p u s - p r o o f - t a s k : 0 9 e 5 c 8 8 e b 0 8 7 
 
 a r t i f a c t s :   / t m p / m a c h i n e - c h e c k - j o y p h j n 9 / h o m e / O S S / o l y m p u s - w o r k / p r o o f - w o r k / p r o o f - s j 9 a o _ m 6 
 
 P R O O F   P A S S 
 
 P r o o f   o r c h e s t r a t i o n   P A S S :   [ ' - - s t a b i l i t y ' ] ,   l i n u x / a m d 6 4 ,   i m a g e   s u f f i x = ' ' 
 
 A L L   P O S I X   C H E C K S   P A S S 
 
 
```

The proof orchestration checks echoed Docker calls: daily arm64 received its own image tag; --final and all 19 --stability cells used amd64. They are selection/control-flow checks, not native arm64 image builds.

## Python before/after command evidence

```text
before proof.run:
C:\Users\ASUS\AppData\Local\Programs\Python\Python312\python.exe C:\Users\ASUS\OSS\shipd\tools\dockrun.py run --rm --platform linux/amd64 --network none -v C:\fixtures\patches:/patches:ro fixture-image bash -c "{ mkdir -p /out && cd /app && git apply --whitespace=nowarn /patches/test.patch; } >/tmp/apply.log 2>&1 && ./test.sh --output_path /out/base.xml base; echo '=====PROOF-JUNIT====='; cat /out/base.xml 2>/dev/null"
after proof.run:
python C:\Users\ASUS\OSS\olympus-product\skill\tools\lib\dockrun.py run --rm --platform linux/amd64 --network none -v C:\fixtures\patches:/patches:ro fixture-image bash -c "{ mkdir -p /out && cd /app && git apply --whitespace=nowarn /patches/test.patch; } >/tmp/apply.log 2>&1 && ./test.sh --output_path /out/base.xml base; echo '=====PROOF-JUNIT====='; cat /out/base.xml 2>/dev/null"
proof.run PASS: identical Docker argv + Windows env; only interpreter spelling and helper relocation differ
before dockrun:
docker run --rm --network none fixture-image true
after dockrun:
docker run --rm --network none fixture-image true
solve_watch.py before == after transcript roots:
C:\Users\ASUS\.claude\projects
C:\Users\ASUS\.claude-cli\projects
C:\Users\ASUS\.codex\sessions
s1: SUSPICIOUS (1 transcripts, 1 tool calls, 1 hits)
    Read: {"path": "C:\\Users\\ASUS\\OSS\\olympus-product\\.build1\\watch-fixture\\solver_root\\vp-two\\work\\README"}
s2: CLEAN (1 transcripts, 1 tool calls, 0 hits)

Python compatibility and transcript fixture checks PASS
```

This covers proof.py, lib/dockrun.py and solve_watch.py. The transcript fixture additionally confirmed custom transcript locations, a clone path containing spaces, an outside-clone read marked SUSPICIOUS and an own-clone read marked CLEAN.

## Shell before/after command evidence

Each block below is the captured command line in shell-escaped form (`printf %q`); `$'...'` preserves embedded newlines. Shell redirections go to the scratch outputs described above and are not argv. `timeout` commands retain the complete Claude/Codex arguments. The helper echo stubs record child helper invocations without launching paid jobs.

### solvers.sh

Before:

```bash
timeout --kill-after=60 90m bash /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/OSS/shipd/tools/codex_job.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/vp-task-3-1107031723/work solve /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/vp-task-3-1107031723/work/../brief.md high build
timeout --kill-after=60 90m bash /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/OSS/shipd/tools/codex_job.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/vp-task-4-1107031723/work solve /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/vp-task-4-1107031723/work/../brief.md high build
timeout --kill-after=60 90m /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/bin/claude -p $'# Fixture\n\nFixture request' --model opus --effort high --permission-mode acceptEdits --append-system-prompt Work\ only\ inside\ the\ repository\ in\ your\ current\ folder\ and\ with\ the\ task\ description\ you\ were\ given.\ Do\ not\ read\,\ search\ or\ use\ any\ file\ or\ folder\ outside\ this\ repository\;\ your\ work\ is\ checked\ for\ that\,\ and\ a\ solve\ that\ leaves\ the\ repository\ is\ discarded. n --allowedTools Bash\,Read\,Grep\,Glob\,Write\,Edit --output-format json
timeout --kill-after=60 90m /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/bin/claude -p $'# Fixture\n\nFixture request' --model opus --effort high --permission-mode acceptEdits --append-system-prompt Work\ only\ inside\ the\ repository\ in\ your\ current\ folder\ and\ with\ the\ task\ description\ you\ were\ given.\ Do\ not\ read\,\ search\ or\ use\ any\ file\ or\ folder\ outside\ this\ repository\;\ your\ work\ is\ checked\ for\ that\,\ and\ a\ solve\ that\ leaves\ the\ repository\ is\ discarded. n --allowedTools Bash\,Read\,Grep\,Glob\,Write\,Edit --output-format json
python /c/Users/ASUS/OSS/olympus-product/.build1/before-tools/solve_watch.py /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task
```

After (Windows profile topology):

```bash
timeout --kill-after=60 90m bash /c/Users/ASUS/OSS/olympus-product/skill/tools/lib/codex_job.sh C:/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/home/vp-task-3-1107031732/work solve C:/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/home/vp-task-3-1107031732/work/../brief.md high build
timeout --kill-after=60 90m bash /c/Users/ASUS/OSS/olympus-product/skill/tools/lib/codex_job.sh C:/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/home/vp-task-4-1107031732/work solve C:/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/home/vp-task-4-1107031732/work/../brief.md high build
timeout --kill-after=60 90m C:/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/home/.local/bin/claude.exe -p $'# Fixture\n\nFixture request' --model opus --effort high --permission-mode acceptEdits --append-system-prompt Work\ only\ inside\ the\ repository\ in\ your\ current\ folder\ and\ with\ the\ task\ description\ you\ were\ given.\ Do\ not\ read\,\ search\ or\ use\ any\ file\ or\ folder\ outside\ this\ repository\;\ your\ work\ is\ checked\ for\ that\,\ and\ a\ solve\ that\ leaves\ the\ repository\ is\ discarded. n --allowedTools Bash\,Read\,Grep\,Glob\,Write\,Edit --output-format json
timeout --kill-after=60 90m C:/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/home/.local/bin/claude.exe -p $'# Fixture\n\nFixture request' --model opus --effort high --permission-mode acceptEdits --append-system-prompt Work\ only\ inside\ the\ repository\ in\ your\ current\ folder\ and\ with\ the\ task\ description\ you\ were\ given.\ Do\ not\ read\,\ search\ or\ use\ any\ file\ or\ folder\ outside\ this\ repository\;\ your\ work\ is\ checked\ for\ that\,\ and\ a\ solve\ that\ leaves\ the\ repository\ is\ discarded. n --allowedTools Bash\,Read\,Grep\,Glob\,Write\,Edit --output-format json
python /c/Users/ASUS/OSS/olympus-product/skill/tools/solve_watch.py /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task
```

### stop_solves.sh

Before:

```bash
taskkill //PID 11508 //T //F
taskkill //PID 29960 //T //F
taskkill //PID 25104 //T //F
taskkill //PID 21268 //T //F
taskkill //PID 999999 //T //F
```

After (Windows profile topology):

```bash
taskkill //PID 31004 //T //F
taskkill //PID 13424 //T //F
taskkill //PID 9076 //T //F
taskkill //PID 25884 //T //F
taskkill //PID 999999 //T //F
```

### replica.sh

Before:

```bash
bash /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/OSS/shipd/tools/check_codex_brief.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task/eval/replica/brief-sq-smoke.md /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task/eval/replica/prompts/common.md /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task/eval/replica/prompts/sq.md /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task/eval/replica/prompts/kb-solution.md /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task/eval/replica/prompts/kb-tests.md
bash /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/OSS/shipd/tools/codex_job.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task replica-sq-smoke /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task/eval/replica/brief-sq-smoke.md medium judge
```

After (Windows profile topology):

```bash
bash /c/Users/ASUS/OSS/olympus-product/skill/tools/lib/check_codex_brief.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task/eval/replica/brief-sq-smoke.md /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task/eval/replica/prompts/common.md /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task/eval/replica/prompts/sq.md /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task/eval/replica/prompts/kb-solution.md /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task/eval/replica/prompts/kb-tests.md
bash /c/Users/ASUS/OSS/olympus-product/skill/tools/lib/codex_job.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task replica-sq-smoke /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task/eval/replica/brief-sq-smoke.md medium judge
```

### round.sh

Before:

```bash
bash /c/Users/ASUS/OSS/olympus-product/.build1/before-tools/replica.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task fairness smoke
bash /c/Users/ASUS/OSS/olympus-product/.build1/before-tools/replica.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task sq smokea
bash /c/Users/ASUS/OSS/olympus-product/.build1/before-tools/replica.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task sq smokeb
bash /c/Users/ASUS/OSS/olympus-product/.build1/before-tools/replica.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task dq smoke
bash /c/Users/ASUS/OSS/olympus-product/.build1/before-tools/replica.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task ar smoke
bash /c/Users/ASUS/OSS/olympus-product/.build1/before-tools/replica.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task verify smoke
```

After (Windows profile topology):

```bash
bash /c/Users/ASUS/OSS/olympus-product/skill/tools/replica.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task fairness smoke
bash /c/Users/ASUS/OSS/olympus-product/skill/tools/replica.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task sq smokea
bash /c/Users/ASUS/OSS/olympus-product/skill/tools/replica.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task sq smokeb
bash /c/Users/ASUS/OSS/olympus-product/skill/tools/replica.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task dq smoke
bash /c/Users/ASUS/OSS/olympus-product/skill/tools/replica.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task ar smoke
bash /c/Users/ASUS/OSS/olympus-product/skill/tools/replica.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task verify smoke
```

### sweep.sh

Before:

```bash
bash /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/OSS/shipd/tools/check_codex_brief.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task/eval/sweep-brief-smoke.md
bash /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/OSS/shipd/tools/claude2_run.sh ar /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task pkg /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task/eval/sweep-brief-smoke.md high
bash /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/OSS/shipd/tools/claude2_run.sh sq /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task pkg /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task/eval/sweep-brief-smoke.md high
bash /c/Users/ASUS/OSS/olympus-product/.build1/tools/replica.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task ref-audit swsmokea
bash /c/Users/ASUS/OSS/olympus-product/.build1/tools/replica.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task ref-audit swsmokeb
```

After (Windows profile topology):

```bash
bash /c/Users/ASUS/OSS/olympus-product/skill/tools/lib/check_codex_brief.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task/eval/sweep-brief-smoke.md
bash /c/Users/ASUS/OSS/olympus-product/skill/tools/lib/claude2_run.sh ar /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task pkg /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task/eval/sweep-brief-smoke.md high
bash /c/Users/ASUS/OSS/olympus-product/skill/tools/lib/claude2_run.sh sq /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task pkg /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task/eval/sweep-brief-smoke.md high
bash /c/Users/ASUS/OSS/olympus-product/skill/tools/replica.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task ref-audit swsmokea
bash /c/Users/ASUS/OSS/olympus-product/skill/tools/replica.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task ref-audit swsmokeb
```

### watch.sh

Before:

```bash

```

After (Windows profile topology):

```bash

```

### pull.sh

Before:

```bash
olympus problems view fixture --json
olympus problems version list fixture --json
python /c/Users/ASUS/OSS/olympus-product/.build1/before-tools/digest.py /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/pull /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/pull/digest
```

After (Windows profile topology):

```bash
olympus problems view fixture --json
olympus problems version list fixture --json
python /c/Users/ASUS/OSS/olympus-product/skill/tools/digest.py /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/pull /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/pull/digest
```

### hunt.sh

Before:

```bash
gh repo view fixture/project --json stargazerCount\,licenseInfo\,pushedAt\,defaultBranchRef\,primaryLanguage\,isArchived -q \"stars\ \\\(.stargazerCount\)\ \|\ licence\ \\\(.licenseInfo.spdxId\ //\ \"see\ LICENSE\"\)\ \|\ pushed\ \\\(.pushedAt\)\ \|\ branch\ \\\(.defaultBranchRef.name\)\ \|\ \\\(.primaryLanguage.name\)\ \|\ archived\ \\\(.isArchived\)\"
gh api search/issues\?q=repo:fixture/project+is:pr+is:merged+merged:\>2025-11-07\&per_page=1 -q .total_count
gh repo view fixture/project --json primaryLanguage -q .primaryLanguage.name
bash /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/OSS/shipd/tools/check_codex_brief.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/OSS/shipd/seams/work/project/brief.md
bash /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/OSS/shipd/tools/codex_job.sh /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/OSS/shipd/seams/work/project hunt /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/OSS/shipd/seams/work/project/brief.md high search
bash /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/OSS/shipd/tools/claude2_run.sh free /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/OSS/shipd/seams/work/project hunt /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/OSS/shipd/seams/work/project/brief.md high
```

After (Windows profile topology):

```bash
gh repo view fixture/project --json stargazerCount\,licenseInfo\,pushedAt\,defaultBranchRef\,primaryLanguage\,isArchived -q \"stars\ \\\(.stargazerCount\)\ \|\ licence\ \\\(.licenseInfo.spdxId\ //\ \"see\ LICENSE\"\)\ \|\ pushed\ \\\(.pushedAt\)\ \|\ branch\ \\\(.defaultBranchRef.name\)\ \|\ \\\(.primaryLanguage.name\)\ \|\ archived\ \\\(.isArchived\)\"
gh api search/issues\?q=repo:fixture/project+is:pr+is:merged+merged:\>2025-11-07\&per_page=1 -q .total_count
gh repo view fixture/project --json primaryLanguage -q .primaryLanguage.name
bash /c/Users/ASUS/OSS/olympus-product/skill/tools/lib/check_codex_brief.sh C:/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/home/OSS/shipd/seams/work/project/brief.md
bash /c/Users/ASUS/OSS/olympus-product/skill/tools/lib/codex_job.sh C:/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/home/OSS/shipd/seams/work/project hunt C:/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/home/OSS/shipd/seams/work/project/brief.md high search
bash /c/Users/ASUS/OSS/olympus-product/skill/tools/lib/claude2_run.sh free C:/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/home/OSS/shipd/seams/work/project hunt C:/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/home/OSS/shipd/seams/work/project/brief.md high
```

### lib/codex_job.sh

Before:

```bash
codex exec --sandbox danger-full-access --skip-git-repo-check -C /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task -c model_reasoning_effort=\"high\" -o /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task/eval/codex/mock.md.final $'You are an independent reviewer (Codex) working for the coordinator (main Claude); nobody else\'s verdicts bind you.\nTask folder: /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task. Your instructions are in this brief; read it first and do exactly what it asks: /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task/brief.md\nEverything you need is in that brief and the files it names. Do not open, read or load any skill files\n(nothing under C:/Users/ASUS/.codex/skills) and no memory files. Verify every claim by file:line or a check run, and\nmark the rest NOT VERIFIED. You may read anything in the task folder; run check builds in Docker one container at a\ntime through python C:/Users/ASUS/OSS/shipd/tools/dockrun.py run ...; write ONLY\nyour report plus check files under the task\'s eval/ folder with a _cx suffix; never edit package folders (wip*/),\nrepo/, base-clean/ or solveN/; never docker rm/rmi/prune or stop containers you did not start.\nReturn only your report (Markdown), starting with a one-line Verdict.'
```

After (Windows profile topology):

```bash
codex exec --sandbox danger-full-access --skip-git-repo-check -C /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task -c model_reasoning_effort=\"high\" -o /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task/eval/codex/mock.md.final $'You are an independent reviewer (Codex) working for the coordinator (main Claude); nobody else\'s verdicts bind you.\nTask folder: /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task. Your instructions are in this brief; read it first and do exactly what it asks: /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task/brief.md\nEverything you need is in that brief and the files it names. Do not open, read or load any skill files\n(nothing under C:/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/home/.codex/skills) and no memory files. Verify every claim by file:line or a check run, and\nmark the rest NOT VERIFIED. You may read anything in the task folder; run check builds in Docker one container at a\ntime through "python" "C:/Users/ASUS/OSS/olympus-product/skill/tools/lib/dockrun.py" run ...; write ONLY\nyour report plus check files under the task\'s eval/ folder with a _cx suffix; never edit package folders (wip*/),\nrepo/, base-clean/ or solveN/; never docker rm/rmi/prune or stop containers you did not start.\nReturn only your report (Markdown), starting with a one-line Verdict.'
```

### lib/claude2_run.sh

Before:

```bash
claude -p $'Before anything else read /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/.claude/projects/c--Users-asus-OSS/memory/MEMORY.md and every lesson file it lists that concerns\nyour role (test quality, solution quality, auto review, FP/passers, hints/calibration, reviewers); they are the\nteam\'s accumulated rules and outweigh your defaults.\nTask folder: /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task (work there; use absolute paths). Package under review: pkg. Read the brief first: /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task/brief.md\nIndependence: form and write your own verdict first, from the package itself. Only then read earlier reviews/triage\ntables the brief points to, and add a section \'Against earlier decisions\' listing each earlier decision you disagree with.\n\nRules: you are an independent reviewer running on a second Claude account; nobody else\'s verdicts bind you.\nNever edit package folders (wip*/ submit*/ sample/), repo/, base-clean/ or solveN/ folders. Write probes only under\neval/ with a _c2 suffix. Docker: one container at a time via: MSYS_NO_PATHCONV=1 python "C:/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/OSS/claude-code/challenges/cc-faust-eos-offsets/eval/dockrun.py" run --rm\n--network none -v "$(pwd -W):/s:ro" <image> bash /s/eval/<script>.sh ; never docker rm/rmi/prune, never stop\ncontainers you did not start. Verify every claim you make (probe or file:line); mark the rest NOT VERIFIED.\nNO mutation batteries, mutant sweeps, PYTHONHASHSEED sweeps or repeat runs (user rule 2026-10-18: mutation is\nthe coordinator\'s job after all checks): at most one targeted probe per suspected gap, host venv first, Docker\nonly to confirm (each container <= ~15 min).\nWhen done, write your full report to /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task/eval/claude2/pkg-sq.md and end with a short summary.' --effort high --permission-mode acceptEdits --allowedTools Bash\,Read\,Grep\,Glob\,Write\,Edit\,Agent --add-dir /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task --add-dir /c/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/.claude/skills --agent olympus-sq-judge --model claude-opus-5-5
```

After (Windows profile topology):

```bash
claude -p $'Before anything else read C:/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/home/.claude/projects/c--Users-asus-OSS/memory/MEMORY.md and every lesson file it lists that concerns\nyour role (test quality, solution quality, auto review, FP/passers, hints/calibration, reviewers); they are the\nteam\'s accumulated rules and outweigh your defaults.\nTask folder: /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task (work there; use absolute paths). Package under review: pkg. Read the brief first: /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task/brief.md\nIndependence: form and write your own verdict first, from the package itself. Only then read earlier reviews/triage\ntables the brief points to, and add a section \'Against earlier decisions\' listing each earlier decision you disagree with.\n\nRules: you are an independent reviewer running on a second Claude account; nobody else\'s verdicts bind you.\nNever edit package folders (wip*/ submit*/ sample/), repo/, base-clean/ or solveN/ folders. Write probes only under\neval/ with a _c2 suffix. Docker: one container at a time via: MSYS_NO_PATHCONV=1 "python" "C:/Users/ASUS/OSS/olympus-product/skill/tools/lib/dockrun.py" run --rm\n--network none -v "$(pwd -W):/s:ro" <image> bash /s/eval/<script>.sh ; never docker rm/rmi/prune, never stop\ncontainers you did not start. Verify every claim you make (probe or file:line); mark the rest NOT VERIFIED.\nNO mutation batteries, mutant sweeps, PYTHONHASHSEED sweeps or repeat runs (user rule 2026-10-18: mutation is\nthe coordinator\'s job after all checks): at most one targeted probe per suspected gap, host venv first, Docker\nonly to confirm (each container <= ~15 min).\nWhen done, write your full report to /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task/eval/claude2/pkg-sq.md and end with a short summary.' --effort high --permission-mode acceptEdits --allowedTools Bash\,Read\,Grep\,Glob\,Write\,Edit\,Agent --add-dir /c/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task --add-dir C:/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/home/.claude/skills --agent olympus-sq-judge --model claude-opus-5-5
```

### lib/replay_patches.sh

Before:

```bash
python C:/Users/ASUS/OSS/olympus-product/.build1/smoke-before/home/OSS/shipd/tools/dockrun.py run --rm --network none -v C:/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task/pkg:/pkg:ro -v C:/Users/ASUS/OSS/olympus-product/.build1/smoke-before/task/base:/repo:ro -v C:/Users/ASUS/OSS/olympus-product/.build1/smoke-before/patches:/patches:ro --entrypoint bash fixture-image -c $'\nset -u\ncp -r /repo /tmp/r && cd /tmp/r\nrun() { n=$1; f=$2\n  git checkout -q . && git clean -qfd\n  git apply /pkg/test.patch && git apply "$f" 2>/dev/null || { echo "$n: APPLY FAIL"; return; }\n  timeout -k 30 1800 bash test.sh --output_path /tmp/out.xml new > /tmp/log 2>&1\n  python3 - "$n" <<PY\nimport sys, xml.etree.ElementTree as ET\nn = sys.argv[1]\ntry:\n    root = ET.parse("/tmp/out.xml").getroot()\nexcept Exception as exc:\n    print(f"{n}: NO JUNIT ({exc})"); raise SystemExit\ncases = list(root.iter("testcase"))\nbad = [c.get("name") for c in cases if c.find("failure") is not None or c.find("error") is not None]\nprint(f"{n}: {len(cases) - len(bad)}/{len(cases)} new")\nfor b in bad: print(f"      FAILED {b}")\nPY\n}\nrun reference /pkg/solution.patch\nfor f in /patches/*.patch; do run "$(basename "$f" .patch)" "$f"; done\n'
```

After (Windows profile topology):

```bash
env MSYS_NO_PATHCONV=1 python C:/Users/ASUS/OSS/olympus-product/skill/tools/lib/dockrun.py run --rm --network none -v C:/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task/pkg:/pkg:ro -v C:/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/task/base:/repo:ro -v C:/Users/ASUS/OSS/olympus-product/.build1/smoke-windows/patches:/patches:ro --entrypoint bash fixture-image -c $'\nset -u\ncp -r /repo /tmp/r && cd /tmp/r\nrun() { n=$1; f=$2\n  git checkout -q . && git clean -qfd\n  git apply /pkg/test.patch && git apply "$f" 2>/dev/null || { echo "$n: APPLY FAIL"; return; }\n  timeout -k 30 1800 bash test.sh --output_path /tmp/out.xml new > /tmp/log 2>&1\n  python3 - "$n" <<PY\nimport sys, xml.etree.ElementTree as ET\nn = sys.argv[1]\ntry:\n    root = ET.parse("/tmp/out.xml").getroot()\nexcept Exception as exc:\n    print(f"{n}: NO JUNIT ({exc})"); raise SystemExit\ncases = list(root.iter("testcase"))\nbad = [c.get("name") for c in cases if c.find("failure") is not None or c.find("error") is not None]\nprint(f"{n}: {len(cases) - len(bad)}/{len(cases)} new")\nfor b in bad: print(f"      FAILED {b}")\nPY\n}\nrun reference /pkg/solution.patch\nfor f in /patches/*.patch; do run "$(basename "$f" .patch)" "$f"; done\n'
```

## Remaining portability limits

- Native macOS/Apple Silicon was unavailable. POSIX behavior was tested in Linux; macOS branches and absence of cygpath usage were checked in echo mode. Apple Silicon Docker builds and real authenticated Claude/Codex jobs need a machine smoke test.
- macOS needs GNU timeout on PATH (coreutils/gnubin), documented in README.md. Profile shell describes the shell; the shipped scripts still require Bash and may be invoked from zsh with bash.
- Existing challenge Dockerfiles may download architecture-specific binaries. A native arm64 daily proof requires an arm64-compatible Dockerfile; use an amd64 native_platform for such legacy tasks until their owners supply compatible Dockerfiles. No package or Dockerfile was edited.
- docker.memory_gb records the intended Docker Desktop allocation; it does not alter Desktop settings. parallel.battery_workers is exported for external batteries; there is no battery launcher in this product to refactor.
- Shared novelty lists, playbooks, existing coordinator memory, second-account credentials and repository data must already exist at the profile paths. The installer deliberately does not migrate those live stores.
- The relocated product lock does not coordinate with a legacy copy using OSS/shipd/tools/.docker.lock. Use one installed lib/dockrun.py across all cooperating sessions. During this task real containers were sequential and limited to one.

Scratch scripts, complete echo logs, installation fixtures and JUnit/log proof artifacts are under `.build1/` and were not committed. No skill, agent, package or live workspace installation was changed.
