#!/usr/bin/env bash
# Fast-forward local main to origin/main (train workstation or lab checkout).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

REMOTE="${GIT_SYNC_REMOTE:-origin}"
BRANCH="${GIT_SYNC_BRANCH:-main}"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "git-sync-origin-main: not a git repo: $ROOT" >&2
  exit 2
fi

# Prefer SSH remote when HTTPS push fails (train box).
if [[ "${GIT_SYNC_ENSURE_SSH:-0}" == "1" ]]; then
  url="$(git remote get-url "$REMOTE" 2>/dev/null || true)"
  if [[ "$url" == https://github.com/* ]]; then
    slug="${url#https://github.com/}"
    slug="${slug%.git}"
    git remote set-url "$REMOTE" "git@github.com:${slug}.git"
    echo "git-sync-origin-main: remote $REMOTE → git@github.com:${slug}.git"
  fi
fi

echo "$(date -Iseconds) git-sync-origin-main: fetch $REMOTE"
git fetch "$REMOTE"

upstream="${REMOTE}/${BRANCH}"
if ! git rev-parse --verify "$upstream" >/dev/null 2>&1; then
  echo "git-sync-origin-main: missing $upstream" >&2
  exit 2
fi

dirty="$(git status --porcelain)"
if [[ -n "$dirty" ]]; then
  echo "git-sync-origin-main: working tree not clean — commit or stash before pull:" >&2
  git status -sb >&2
  exit 3
fi

git checkout "$BRANCH" 2>/dev/null || git checkout -B "$BRANCH" "$upstream"
before="$(git rev-parse HEAD)"
git pull --ff-only "$REMOTE" "$BRANCH"
after="$(git rev-parse HEAD)"
echo "$(date -Iseconds) git-sync-origin-main: HEAD $after ($(git log -1 --oneline))"
if [[ "$before" != "$after" ]]; then
  echo "git-sync-origin-main: updated $before → $after"
else
  echo "git-sync-origin-main: already up to date"
fi
