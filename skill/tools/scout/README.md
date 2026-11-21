# scout: harness fingerprint and length attribution

Scripts (standard library; tiktoken optional, else a 4-characters-per-token estimate named in the first output line):
- `stage_a.py <trajectory.json or run folder>...`: hosted harness fingerprint per run: hidden prompt part (first-request input minus the visible messages), requests, windows and peaks, sequence length, output and reasoning tokens per request, minutes; then tool sets, argument-name sets, the tool-output header, the system head and the skills listed.
- `local_sessions.py [--marker TEXT] <sessions dir or rollout-*.jsonl>...`: the same fingerprint from local Codex session logs, where model and effort are known; `--marker` keeps only the sessions whose working folder names one task's solve clones.
- `attribution.py [--areas areas.json] <run folder or trajectory.json>...`: share of each run's context per requirement area; `areas.json` is `{"area name": "regex"}` (`_build` and `_orient` override the built-in test/build and orientation groups); without it one area, `all`.
- `timeline.py <trajectory.json or run folder> [--limit N]`: every tool call with its result size, the agent's messages, and the per-window peaks in the header.
Sequence length, run folders and verdicts are read by `../seqlen.py`; a batch table with the gate lines by `../rollout_report.py`.

When the workflow runs them:
1. Before any local stand-in solve: `stage_a.py` on the latest hosted runs and `local_sessions.py` on the stand-in's sessions; the stand-in is comparable only when its tool set, hidden part and reasoning per request are close to the hosted ones (hosted Codex compacts at about 244K; a local build may not).
2. After every rollout: `stage_a.py` on the new runs; record the hidden-part size and the reasoning per request in the ledger, so a platform change (harness build, model, effort) shows at once instead of being read as a task effect.
3. Before adding a requirement for length: `attribution.py` with the task's areas on the runs that fell short of 300K. Measured on vet task 6 (6 Orion runs): about 20K of context per requirement that needs a code change, 3-7K for one the reference already meets, tests and builds about 18%, the model's reasoning and messages about 15%, the fixed prompt about 5%.
4. One run that behaved oddly (a pass without the work, a compaction at the wrong time): `timeline.py` on it.
