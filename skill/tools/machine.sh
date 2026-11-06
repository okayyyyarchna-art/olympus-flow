#!/usr/bin/env bash
# Source once per tool; machine.py validates and quotes every exported value.
OLYMPUS_TOOLS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OLYMPUS_LIB="$OLYMPUS_TOOLS/lib"
_olympus_python="${OLYMPUS_BOOTSTRAP_PYTHON:-$(command -v python3 || command -v python)}"
_olympus_exports="$("$_olympus_python" "$OLYMPUS_TOOLS/machine.py" shell)" || return 2
eval "$_olympus_exports"
export OLYMPUS_TOOLS OLYMPUS_LIB
export CODEX_HOME="$OLYMPUS_CODEX_HOME"
OLYMPUS_DOCKER_ENV=()
[ "$OLYMPUS_OS" != windows ] || OLYMPUS_DOCKER_ENV=(env MSYS_NO_PATHCONV=1)
machine_host() {
  if [ "$OLYMPUS_OS" = windows ]; then cygpath -m "$1"; else printf '%s\n' "$1"; fi
}
machine_config() {
  if [ "$OLYMPUS_OS" = windows ]; then cygpath -w "$1"; else printf '%s\n' "$1"; fi
}
unset _olympus_python _olympus_exports
