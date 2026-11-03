#!/bin/bash
# Vercel Ignored Build Step
# Exit 0 -> Skip build
# Exit 1 -> Proceed with build
#
# Rule: Rely strictly on path-based diffing, not commit message prefixes,
# so that any update touching published content, Quartz engine/config,
# dependencies, or deployment settings always triggers a build.

echo "== Vercel Ignored Build Step =="
echo "Commit: ${VERCEL_GIT_COMMIT_SHA:-HEAD}"
echo "Message: ${VERCEL_GIT_COMMIT_MESSAGE:-None}"

# Fallback base commit: compare against HEAD^ unless Vercel supplies previous commit
BASE_COMMIT="HEAD^"
if [ -n "$VERCEL_GIT_PREVIOUS_SHA" ]; then
  BASE_COMMIT="$VERCEL_GIT_PREVIOUS_SHA"
fi

# If comparison fails (e.g. shallow clone or initial commit), proceed with build to be safe
if ! git rev-parse --verify "$BASE_COMMIT" >/dev/null 2>&1; then
  echo "⚠️ Cannot resolve base commit ($BASE_COMMIT). Proceeding with build."
  exit 1
fi

# Paths that MUST trigger a rebuild:
# - content / wiki (the published markdown knowledge base)
# - quartz (Quartz components, layouts, plugins)
# - quartz.config.ts, quartz.layout.ts
# - package.json, package-lock.json (dependencies)
# - vercel.json, tsconfig.json
# - public / assets
CRITICAL_PATHS=(
  "content"
  "wiki"
  "quartz"
  "quartz.config.ts"
  "quartz.layout.ts"
  "package.json"
  "package-lock.json"
  "tsconfig.json"
  "vercel.json"
  "public"
)

CHANGED_CRITICAL=$(git diff "$BASE_COMMIT" HEAD --name-only -- "${CRITICAL_PATHS[@]}")

if [ -n "$CHANGED_CRITICAL" ]; then
  echo "✅ Web-facing content, Quartz configuration, or dependencies changed:"
  echo "$CHANGED_CRITICAL" | sed 's/^/   - /'
  echo "Proceeding with build."
  exit 1
fi

echo "🛑 Only non-web files changed (e.g. scripts, tests, runner docs, data). Skipping Vercel build."
exit 0
