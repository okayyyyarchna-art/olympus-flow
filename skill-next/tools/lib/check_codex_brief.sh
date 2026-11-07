#!/usr/bin/env bash
# Lists words in a Codex brief (and any files it names) that OpenAI's filter tends to flag, so they can be
# reworded before launch. Usage: bash check_codex_brief.sh brief-cx.md [other files...]
# Exit 0 = clean, 1 = words found.
words='attack|adversar|exploit|vulnerab|payload|malicious|malware|inject|intrusion|credential|bypass|hunt|probe|fuzz|crash|\bkill|trap|leak|cheat|mutant|surviv|backdoor|privilege|escalat|FP panel|red.?team|security'
if grep -inE "$words" "$@"; then
  echo "== reword the lines above before launching Codex" >&2
  exit 1
fi
echo "clean: no flagged words in $*"
