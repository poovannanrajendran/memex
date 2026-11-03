#!/bin/bash
# Vercel Ignored Build Step
# Exit 0 -> Skip build
# Exit 1 -> Proceed with build

echo "== Vercel Ignored Build Step Check =="
echo "Commit: $VERCEL_GIT_COMMIT_SHA"
echo "Message: $VERCEL_GIT_COMMIT_MESSAGE"

# Check commit message prefixes that don't affect public site
if echo "$VERCEL_GIT_COMMIT_MESSAGE" | grep -iE '^(docs|test|tests|chore|ci|fix\(api\)|fix\(pipeline\)|fix\(db\)):' ; then
  echo "🛑 Commit matches non-UI prefix. Skipping Vercel build."
  exit 0
fi

# Check diff against previous commit
# If only backend scripts, tests, output, or migrations changed, skip build
git diff HEAD^ HEAD --quiet -- . ':(exclude)scripts/**' ':(exclude)tests/**' ':(exclude)output/**' ':(exclude)deploy/**' ':(exclude).agents/**' ':(exclude)README.md' ':(exclude)TASKS.md' ':(exclude)CHANGELOG.md' ':(exclude)requirements.txt'

DIFF_STATUS=$?
if [ $DIFF_STATUS -eq 0 ]; then
  echo "🛑 No web-facing content or Quartz code changed. Skipping Vercel build."
  exit 0
fi

echo "✅ Web-facing content or Quartz config changed. Proceeding with build."
exit 1
