# Templates

Copy only from `accepted/` (the platform accepted these packages). `in-review/` holds packages that passed every
check but are still in finalizing review: use them only for a language with no accepted example, and say so in
flow-status. Draft packages are never templates.

| Folder | Language | test.sh / Dockerfile | Source (platform status, results) |
|---|---|---|---|
| accepted | Python (faust) | *.python-faust-table-visibility | table visibility, ACCEPTED (AR 3/3/3, Vega 1/4, Orion 0, Nova 0) |
| accepted | Python (faust) | *.python-faust-eos | EOS offsets, ACCEPTED (Orion 1/4) |
| accepted | Go | *.go-oss-rebuild | oss-rebuild docker proxy, ACCEPTED (AR 3/3/3, Orion 1/8) |
| accepted | Go | *.go-burrow-snapshot | Burrow snapshot, ACCEPTED (older gates) |
| in-review | Python (faust) | *.python-faust-topic-start | topic start, finalizing review |
| in-review | Python | *.python-swift | swift conditional writes, finalizing review |
| in-review | Rust | *.rust-elio | elio folder history, finalizing review (no accepted Rust package yet) |

No accepted TypeScript package exists on this account yet.
Adapt: the new test file list, the base selection (every test file guarding touched code), the base commit, the exact
deselect list with one comment per id. Keep: two modes, scratch copy with base tests restored, fail-safe JUnit, hard
timeout below the platform kill.
