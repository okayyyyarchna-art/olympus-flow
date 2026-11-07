# Shared preflight: call before creating outputs or starting any model job.
require_files() {
  local file failed=0
  for file in "$@"; do
    [ -s "$file" ] || { echo "missing or empty input: $file" >&2; failed=1; }
  done
  [ "$failed" = 0 ]
}
