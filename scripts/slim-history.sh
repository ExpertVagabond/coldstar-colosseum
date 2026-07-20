#!/usr/bin/env bash
# Slim coldstar's git history for the audit: strip large NON-CODE blobs that
# were committed and later removed, without altering the current HEAD tree by
# a single byte. Rust build artifacts, an old Remotion project, a manim media
# dir, and a handoff zip bloat .git to 276M for a 40M checkout.
#
# SAFE BY CONSTRUCTION:
#   - operates on a throwaway CLONE in a temp dir, never this working tree
#   - never touches the 1.2G untracked video/ working dir (gitignored, not cloned)
#   - ASSERTS the filtered HEAD tree is byte-identical to the original, and
#     aborts if it is not (a too-greedy glob can only fail loud, never silently
#     drop a live file)
#   - does NOT push. It prints the exact force-push command for you to run
#     after you review the numbers.
#
#   ./slim-history.sh            measure + verify on a clone, print push cmd
#
# Requires: git-filter-repo (installed).
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="${TMPDIR:-/tmp}/coldstar-slim.$$"
CLONE="$TMP/coldstar"

# Paths removed from ALL history. Every entry MUST have zero files in current
# HEAD (verified: coldstar_zk/target, coldstar-video, coldstar-manim, archives),
# or be a glob that matches only history-only files (video/*.mp4,
# coldstar-interactive/*.mp4 — those dirs keep code/assets in HEAD, no mp4).
# videos/*.mp4 is intentionally EXCLUDED: 4 such files are live in HEAD.
# --invert-paths flips filter-repo from "keep only these" to "remove these".
PATHS=(
  --invert-paths
  --path coldstar_zk/target/
  --path coldstar-video/
  --path coldstar-manim/
  --path archives/
  --path-glob 'video/*.mp4'
  --path-glob 'coldstar-interactive/*.mp4'
)

cleanup(){ rm -rf "$TMP"; }
trap cleanup EXIT
mkdir -p "$TMP"

echo "→ cloning working repo (local, fast)…"
git clone --quiet --no-local "file://$SRC/.git" "$CLONE" 2>/dev/null || git clone --quiet "$SRC/.git" "$CLONE"

before_git=$(du -sh "$CLONE/.git" | cut -f1)
before_tree=$(cd "$CLONE" && git ls-tree -r HEAD | shasum | cut -d' ' -f1)  # tree content, invariant to commit-SHA rewrite
before_files=$(cd "$CLONE" && git ls-files | wc -l | tr -d ' ')

echo "→ rewriting history (git-filter-repo)…"
( cd "$CLONE" && git filter-repo --force "${PATHS[@]}" >/dev/null )

after_git=$(du -sh "$CLONE/.git" | cut -f1)
after_tree=$(cd "$CLONE" && git ls-tree -r HEAD | shasum | cut -d' ' -f1)  # tree content, invariant to commit-SHA rewrite
after_files=$(cd "$CLONE" && git ls-files | wc -l | tr -d ' ')

echo
echo "  .git size : $before_git  →  $after_git"
echo "  HEAD files: $before_files →  $after_files"
if [ "$before_tree" = "$after_tree" ]; then
  echo "  HEAD tree : IDENTICAL ✓ (no live file changed)"
else
  echo "  HEAD tree : CHANGED ✗ — a glob was too greedy; ABORTING, do not push." >&2
  exit 1
fi

echo
echo "Review looks good? The rewrite is NOT applied to your repo or the remote."
echo "To apply (DESTRUCTIVE — rewrites SHAs, requires everyone to re-clone):"
echo "  1. cd \"$SRC\""
echo "  2. git filter-repo --force --invert-paths \\"
  echo "       --path coldstar_zk/target/ --path coldstar-video/ --path coldstar-manim/ --path archives/ \\"
  echo "       --path-glob 'video/*.mp4' --path-glob 'coldstar-interactive/*.mp4'"
echo "  3. git remote add origin git@github.com:ExpertVagabond/coldstar-colosseum.git  # filter-repo drops the remote"
echo "  4. git push --force --all && git push --force --tags"
