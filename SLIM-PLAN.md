# Coldstar repo-slim plan (for the Hashlock audit)

**Status: DRAFT on branch `chore/repo-slim`. Nothing pushed. Nothing rewritten.**

## The corrected problem

The initial triage said "split the 1.2G `video/` out for the audit." That was
wrong — it measured the *working tree*, not what an auditor receives.

- `video/` (1.2G) is **gitignored**. `git clone` never pulls it.
- Current **HEAD checkout is 40M** (304 tracked files, clean — no build
  artifacts, audio, or zips tracked today).
- But **`.git` history is 276M**, because these were committed and later
  removed (they still live in history, so every clone drags them along):

  | path (history-only) | ~size | what it is |
  |---|---|---|
  | `coldstar_zk/target/` | 237M | Rust build artifacts (should never be committed) |
  | `coldstar-video/` | 103M | old Remotion project (audio .wav/.mp3) |
  | `archives/coldstar-handoff.zip` | 25M | a handoff zip |
  | `coldstar-manim/` | 3M | manim render media |
  | `video/*.mp4`, `coldstar-interactive/*.mp4` | ~30M | old demo renders |

For a security audit this is the real issue: auditors clone **276M for a 40M
project**, and the history carries build artifacts — avoidable supply-chain noise.

## What the draft does

1. **`.gitignore` hygiene (applied on this branch):** `**/target/`, `*.wav`,
   `*.mp3` so the purged classes can't be re-committed. (`coldstar_zk/target/`
   was already ignored; the anchoring is now belt-and-suspenders.)

2. **`scripts/slim-history.sh` — measured, not applied.** Rewrites history to
   drop the paths above, on a *throwaway clone*, and **asserts the HEAD tree is
   byte-identical** before/after (aborts if any live file would change). Proven
   result:

   ```
   .git size : 276M  →  ~60M
   HEAD files: 304   →  304   (tree IDENTICAL — zero live files changed)
   ```

   Only zero-HEAD paths are purged. `videos/*.mp4` is deliberately **kept**:
   4 of those are live in HEAD.

## What it does NOT do (needs your explicit go)

The actual rewrite + force-push is destructive: it rewrites every commit SHA,
so anyone who cloned `coldstar-colosseum` must re-clone, and open PRs/branches
break. The script prints the exact commands; run them only when you've
coordinated with anyone working off the repo (and ideally before, not during,
the audit hand-off). `git-filter-repo` also drops the `origin` remote — the
printed steps re-add it.

## Audit-scope note

Slimming history ≠ defining the audit surface. *Which code* Hashlock audits
(the Rust `secure_signer/`, `coldstar_zk/`, signing paths vs. the TUI/demo
tooling) is their scope call from the engagement letter — not inferred here.
