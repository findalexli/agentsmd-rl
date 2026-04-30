#!/usr/bin/env bash
set -euo pipefail

cd /workspace/qtpass

# Idempotency guard
if grep -qF "See [qtpass-localization](../qtpass-localization/SKILL.md) skill for comprehensi" ".claude/skills/qtpass-docs/SKILL.md" && grep -qF "This enables clangd/LSP to provide accurate completions and catch real issues. W" ".claude/skills/qtpass-fixing/SKILL.md" && grep -qF "gh api graphql -f query='{ repository(owner: \"OWNER\", name: \"REPO\") { pullReques" ".claude/skills/qtpass-github/SKILL.md" && grep -qF "For proper code completion and analysis in editors like Visual Studio Code with " ".claude/skills/qtpass-linting/SKILL.md" && grep -qF "Currently includes: af_ZA, ar_MA, bg_BG, ca_ES, cs_CZ, cy_GB, da_DK, de_DE, de_L" ".claude/skills/qtpass-localization/SKILL.md" && grep -qF "For scripts that modify remote state (uploading releases, signing files), add a " ".claude/skills/qtpass-releasing/SKILL.md" && grep -qF "Tests that modify QtPass settings can pollute the user's live config. This is es" ".claude/skills/qtpass-testing/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/qtpass-docs/SKILL.md b/.claude/skills/qtpass-docs/SKILL.md
@@ -0,0 +1,195 @@
+---
+name: qtpass-docs
+description: Documentation guide for QtPass - README, FAQ, localization
+license: GPL-3.0-or-later
+metadata:
+  audience: developers
+  workflow: documentation
+---
+
+# Project Documentation
+
+## QtPass Documentation Files
+
+| File               | Purpose                                     |
+| ------------------ | ------------------------------------------- |
+| README.md          | Main documentation, installation, usage     |
+| FAQ.md             | Frequently asked questions, troubleshooting |
+| CHANGELOG.md       | Release history, changes                    |
+| CONTRIBUTING.md    | Developer contribution guidelines           |
+| CODE_OF_CONDUCT.md | Community code of conduct                   |
+| Doxyfile           | API documentation configuration             |
+| Windows.md         | Windows-specific installation and build     |
+
+## README.md Sections
+
+- Badges (build, license, version)
+- Description
+- Features
+- Installation (Linux, macOS, Windows)
+- Usage / Getting Started
+- Configuration
+- Acknowledgments
+
+## FAQ.md Sections
+
+- Installation issues
+- Configuration issues
+- GPG/Key issues
+- Git integration
+- Platform-specific (macOS, Windows, Linux)
+
+### FAQ Template
+
+```markdown
+## Question Title
+
+**Problem:** Description of the issue
+
+**Solution:** Step-by-step solution
+
+**Related:** Links to relevant issues
+```
+
+## Localization
+
+See [qtpass-localization](../qtpass-localization/SKILL.md) skill for comprehensive guide.
+
+## Docs Build
+
+### API Documentation
+
+```bash
+# Generate API docs
+doxygen Doxyfile
+# Or use project-specific docs command
+
+# View
+open html/index.html
+```
+
+## Linting
+
+**THIS IS THE PATTERN - always run before pushing:**
+
+```bash
+# Check formatting (this is the pattern)
+npx prettier --check "**/*.md"
+
+# Format all markdown files
+npx prettier --write "**/*.md"
+
+# Format specific file
+npx prettier --write README.md
+```
+
+### Markdown (prettier)
+
+```bash
+npx prettier --write <markdown-file>
+npx prettier --write .opencode/skills/*/SKILL.md
+```
+
+### YAML (prettier)
+
+```bash
+npx prettier --write <yaml-file>
+npx prettier --write .github/workflows/*.yml
+```
+
+## Updating Documentation
+
+### Adding New FAQ Entry
+
+1. Edit `FAQ.md`
+2. Use the FAQ template section above
+3. Run prettier: `npx prettier --write FAQ.md`
+4. Test the changes render correctly
+
+### Updating Version in readme
+
+When releasing a new version, update download links:
+
+```bash
+# Find version strings in README
+grep -n "1\.5\|download" README.md
+```
+
+Update:
+
+- Download links for each platform
+- Badge version numbers
+- Any version-specific instructions
+
+### Building API Docs
+
+```bash
+# Generate with doxygen
+doxygen Doxyfile
+
+# Output goes to docs/html/
+ls docs/html/index.html
+```
+
+## Common Pitfalls
+
+### Forgetting to Run Prettier
+
+Always format Markdown with prettier before committing:
+
+```bash
+# Wrong - may fail CI
+git commit -m "Update FAQ"
+
+# Correct
+npx prettier --write FAQ.md
+git commit -m "Update FAQ"
+```
+
+### Broken Links
+
+When adding links to issues or PRs:
+
+```bash
+# Use full GitHub URLs (they redirect correctly)
+[Issue #123](https://github.com/IJHack/QtPass/issues/123)
+
+# Not relative paths
+[Issue #123](issues/123)  # Broken
+```
+
+### Outdated Platform Instructions
+
+QtPass changes frequently. When updating installation instructions:
+
+- Verify the commands still work
+- Check for new dependencies
+- Update screenshots if UI changed
+
+### CHANGELOG Format
+
+Keep CHANGELOG entries consistent:
+
+```markdown
+## [1.5.1] - 2026-03-30
+
+### Fixed
+
+- Issue #123: Description of fix
+
+### Added
+
+- New feature description
+```
+
+### Doxygen Comments in Code
+
+When adding new public APIs:
+
+```cpp
+/**
+ * @brief Brief description
+ * @param param1 Description of first parameter
+ * @return Description of return value
+ */
+```
diff --git a/.claude/skills/qtpass-fixing/SKILL.md b/.claude/skills/qtpass-fixing/SKILL.md
@@ -0,0 +1,414 @@
+---
+name: qtpass-fixing
+description: Bug fixing workflow for QtPass - find, fix, test, PR
+license: GPL-3.0-or-later
+metadata:
+  audience: developers
+  workflow: bugfix
+---
+
+# Bugfix Workflow for QtPass
+
+## Bugfix Workflow
+
+### 1. Investigate
+
+- Search existing issues: `gh issue list --search "<keywords>"`
+- Check CHANGELOG.md for related fixes
+- Search code: `grep -r "pattern" src/`
+
+### 2. Reproduce
+
+- Read issue details, logs, and stack traces
+- Locate relevant source files
+- Identify root cause
+
+### 3. Fix
+
+- Make minimal, targeted changes in source files
+- Keep changes focused on the root cause
+
+### 4. Add Tests
+
+- Add unit tests for the bugfix
+- Follow project testing conventions (see `qtpass-testing` skill)
+- Place tests in `tests/auto/<module>/`
+
+### 5. Verify
+
+```bash
+# Build and run tests
+make check
+
+# Build binary
+make -j4
+```
+
+### 6. Commit & PR
+
+```bash
+# Create branch
+git checkout -b fix/<issue-number>-short-description
+
+# Commit with issue reference (always use -S for signing)
+git commit -S -m "Fix <description> (#issue)"
+
+# Push and create PR
+git push origin fix/<branch>
+gh pr create --title "Fix <description>" --body "## Summary\n- Fix description"
+```
+
+### Handling Static Analysis Findings
+
+When CodeRabbit/CodeAnt-AI flag issues in PRs:
+
+1. **Verify the finding** - Check if it's a real issue or false positive
+2. **If correct, fix it** - Make minimal changes to address
+3. **Push update** - Force push to update the PR
+4. **Respond to comments** - Comment that fix is applied
+
+```bash
+# After fixing, amend commit and force push
+git add -A
+git commit -S --amend --no-edit
+git push --force
+```
+
+## Common Fix Patterns
+
+### Null Pointer Checks
+
+Qt classes like `QGuiApplication::screenAt()` can return null on some platforms.
+Always verify pointers before dereferencing:
+
+```cpp
+QScreen *screen = QGuiApplication::screenAt(pos);
+if (!screen)
+    return;
+```
+
+### CLI Argument Parsing
+
+Use `QCoreApplication::arguments()` instead of raw `argv[]` to let Qt normalize paths and handle quoting:
+
+```cpp
+QStringList args = QCoreApplication::arguments();
+```
+
+### External Tool Availability
+
+Before using optional tools like `pass-otp`, check availability:
+
+```cpp
+if (!passOTPexists) {
+    showError("pass-otp is required for OTP features");
+    return;
+}
+```
+
+### Cross-Platform Path Handling
+
+Use `QDir` for path normalization to handle `/` vs `\` and `.`/`..` components:
+
+```cpp
+QDir dir;
+QString normalized = dir.cleanPath(gpgIdPath);
+```
+
+### String Parsing Edge Cases
+
+For regular expression patterns matching URLs or special characters, use `\\S+` for non-whitespace to avoid matching spaces:
+
+```cpp
+QRegularExpression urlRegex("(\\S+)://(\\S+)");
+```
+
+### UI Font Consistency
+
+For monospace fonts in tables/lists, use `setStyleHint(QFont::Monospace)` to avoid platform-specific defaults.
+
+### Tautology Assertions in Tests
+
+Avoid assertions that always evaluate to true:
+
+```cpp
+// Bad - always true
+QVERIFY(profiles.isEmpty() || !profiles.isEmpty());
+QVERIFY(!store.isEmpty() || store.isEmpty());
+
+// Good - meaningful check
+QVERIFY(profiles.isEmpty());
+QVERIFY2(store.isEmpty() || store.startsWith("/"), "Pass store should be empty or a plausible path");
+```
+
+### Verify Test Setup Return Values
+
+Always verify that test setup operations succeed:
+
+```cpp
+// Bad - ignores return value
+(void)QDir(srcDir.path()).mkdir("source");
+(void)f1.open(QFile::WriteOnly);
+
+// Good - verify success
+QVERIFY(QDir(srcDir.path()).mkdir("source"));
+QVERIFY(f1.open(QFile::WriteOnly));
+```
+
+### Contractions in Comments
+
+Use "cannot" instead of "can't" for formal consistency:
+
+```cpp
+// Bad
+// On Windows, we can't safely backup
+
+// Good
+// On Windows, we cannot safely backup
+```
+
+### Copyright Year in Templates
+
+Use `YYYY` as placeholder instead of current year:
+
+```cpp
+// Bad
+// SPDX-FileCopyrightText: 2026 Your Name
+
+// Good
+// SPDX-FileCopyrightText: YYYY Your Name
+```
+
+### Return After Dialog Rejection
+
+When showing an error dialog followed by `reject()` in a constructor, add `return` to prevent the constructor from continuing with invalid state:
+
+```cpp
+// After error dialog in constructor
+if (users.isEmpty()) {
+    QMessageBox::critical(parent, tr("Error"), tr("No users found"));
+    reject();
+    return;  // Prevent constructor from continuing
+}
+```
+
+### Index Instead of Pointer
+
+When storing references to list items in UI (e.g., Qt::UserRole), prefer indices over pointers to avoid dangling references:
+
+```cpp
+// Instead of storing pointer to local reference
+for (const auto &user : m_userList) {
+    item->setData(Qt::UserRole, QVariant::fromValue(&user));  // DANGLING!
+}
+
+// Store index instead
+for (int i = 0; i < m_userList.size(); ++i) {
+    item->setData(Qt::UserRole, QVariant::fromValue(i));
+}
+```
+
+// Good - store index
+for (int i = 0; i < m_userList.size(); ++i) {
+item->setData(Qt::UserRole, QVariant::fromValue(i));
+}
+
+// Later, lookup by index
+bool success = false;
+const int index = item->data(Qt::UserRole).toInt(&success);
+if (success && index >= 0 && index < m_userList.size()) {
+m_userList[index].enabled = item->checkState() == Qt::Checked;
+}
+}
+
+### Theme-Aware Colors
+
+For list items or labels indicating status (e.g., secret keys), prefer `QPalette` colors over hardcoded values for better accessibility:
+
+```cpp
+// Hardcoded may have poor contrast on some themes
+item->setForeground(Qt::blue);
+
+// Theme-aware alternative
+const QPalette palette = QApplication::palette();
+item->setForeground(palette.color(QPalette::Link));
+```
+
+### Accessibility: Color + Text
+
+When indicating status through colors (invalid, expired, partial), add text prefixes or tooltips for color blind users:
+
+```cpp
+// Color only - not accessible
+item->setBackground(Qt::darkRed);
+
+// Color + text + tooltip - accessible
+item->setBackground(Qt::darkRed);
+item->setText(tr("[INVALID] ") + originalText);
+item->setToolTip(tr("Invalid key"));
+```
+
+### Debug Logging
+
+Add debug logging for validation failures using `#ifdef QT_DEBUG`:
+
+```cpp
+bool success = false;
+const int index = item->data(Qt::UserRole).toInt(&success);
+if (!success) {
+#ifdef QT_DEBUG
+    qWarning() << "UsersDialog::itemChange: invalid user index data for item";
+#endif
+    return;
+}
+if (index < 0 || index >= m_userList.size()) {
+#ifdef QT_DEBUG
+    qWarning() << "UsersDialog::itemChange: user index out of range:" << index;
+#endif
+    return;
+}
+```
+
+### Boolean Logic Bugs
+
+When comparing booleans, use `&&` instead of `==` to avoid unexpected true values:
+
+```cpp
+// Bad - yields true when both are false (e.g., public key case)
+bool secret = false;
+bool isSec = (type == GpgRecordType::Sec);  // false
+handlePubSecRecord(props, secret == isSec);  // false == false = true!
+
+// Good - requires both conditions to be true
+handlePubSecRecord(props, secret && (type == GpgRecordType::Sec));
+```
+
+## Key Source Files
+
+| File                 | Purpose                                 |
+| -------------------- | --------------------------------------- |
+| src/mainwindow.cpp   | Main UI, tree view, dialogs             |
+| src/pass.cpp         | GPG operations, path handling           |
+| src/util.cpp         | Utilities, regular expression, file ops |
+| src/filecontent.cpp  | Password file parsing                   |
+| src/imitatepass.cpp  | CLI pass imitation                      |
+| src/configdialog.cpp | Settings dialog                         |
+| src/executor.cpp     | Command execution                       |
+
+## Linting
+
+See `qtpass-linting` skill for full CI workflow. Pattern:
+
+```bash
+# Run linter locally BEFORE pushing
+act push -W .github/workflows/linter.yml -j build
+```
+
+### Config Files (prettier)
+
+```bash
+npx prettier --write <config-file>
+npx prettier --write .github/workflows/*.yml
+npx prettier --write .opencode/skills/*/SKILL.md
+```
+
+### C++ (clang-format)
+
+```bash
+# Check formatting
+clang-format --style=file --dry-run <source-file>
+
+# Apply formatting
+clang-format --style=file -i <source-file>
+```
+
+## Bug Type Playbooks
+
+### UI Bugs (mainwindow.cpp, dialogs)
+
+UI bugs often involve signal/slot connections, widget state, or clipboard operations.
+
+**Common patterns:**
+
+- Check signal connections are properly connected
+- Verify widget parent/ownership
+- Clipboard operations may fail on some platforms (GNOME, KDE)
+- Theme-aware colors vs hardcoded (see above)
+
+**Debugging:**
+
+```cpp
+// Add debug output
+qDebug() << "Button clicked, state:" << ui->someWidget->isVisible();
+```
+
+### GPG/Pass Bugs (pass.cpp, executor.cpp)
+
+GPG-related bugs often involve command execution, path handling, or key operations.
+
+**Common patterns:**
+
+- Check executor return codes
+- Verify GPG binary is in PATH
+- Watch for path normalization issues (QDir::cleanPath)
+- GPG may lock the keyring - handle retries
+
+**Debugging:**
+
+```cpp
+// Enable verbose GPG output
+// Check /tmp for temporary GPG files
+```
+
+### Path/Model Bugs (storemodel.cpp, configdialog.cpp)
+
+Path handling bugs often involve separators, encoding, or model indexing.
+
+**Common patterns:**
+
+- Use QDir for path operations (handles / vs \)
+- Store indices, not pointers (see above)
+- Check model filter/sort state
+
+**Debugging:**
+
+```cpp
+qDebug() << "Path:" << path << "Cleaned:" << QDir::cleanPath(path);
+```
+
+## IDE/LSP Setup
+
+For proper code analysis (resolving Qt types like `QString`), generate `compile_commands.json`:
+
+```bash
+./scripts/generate-compile-commands.sh
+```
+
+This enables clangd/LSP to provide accurate completions and catch real issues. Without it, the LSP shows false positives about missing Qt headers.
+
+### Using Editor Fix Suggestions
+
+When the LSP shows "(fix available)" on errors:
+
+1. **Visual Studio Code**: Click the 💡 lightbulb or press `Ctrl+.` (Quick Fix)
+2. **JetBrains**: Press `Alt+Enter` on the error
+3. **vim/neovim**: Use clangd's `textDocument/codeAction` via your LSP plugin
+
+**Note:** LSP suggestions are just that - suggestions. Always verify the fix makes sense before applying, especially for complex refactoring.
+
+### Running Clangd from CLI
+
+To check a file directly for issues:
+
+```bash
+# Generate compile_commands.json first (required for Qt headers)
+./scripts/generate-compile-commands.sh
+
+# Check a specific file
+clangd --check=/path/to/file.cpp
+```
+
+Common clangd diagnostics:
+
+- `[performance-unnecessary-copy-initialization]` - Use `const T&` instead of `const T`
+- `[readability-static-definition]` - Consider making static definitions inline
diff --git a/.claude/skills/qtpass-github/SKILL.md b/.claude/skills/qtpass-github/SKILL.md
@@ -0,0 +1,432 @@
+---
+name: qtpass-github
+description: QtPass GitHub interaction - PRs, issues, branches, merging
+license: GPL-3.0-or-later
+metadata:
+  audience: developers
+  workflow: github
+---
+
+# QtPass GitHub Interaction
+
+## Checking PR Status
+
+```bash
+# Check specific PR
+gh pr checks <PR_NUMBER>
+
+# Check all PRs
+gh pr view <PR_NUMBER> --json state,mergeable
+
+# View PR comments
+gh api repos/<owner>/<repo>/pulls/<PR_NUMBER>/comments
+```
+
+## Creating Branches
+
+```bash
+# Create and switch to new branch
+git checkout -b <branch-name>
+
+# Push and set upstream
+git push -u origin <branch-name>
+```
+
+## Creating PRs
+
+```bash
+# Create PR with title and body
+gh pr create --title "Fix description (#issue)" --body "## Summary\n- Fix details\n\nFixes #issue"
+
+# Create PR with specific base branch
+gh pr create --base main --title "Fix" --body "Fixes #issue"
+```
+
+## Updating Branches
+
+**Before pushing or merging, always update with latest main:**
+
+```bash
+# (If not already set) add upstream remote pointing to main repository
+git remote add upstream https://github.com/IJHack/QtPass.git
+# Fetch and rebase on main
+git fetch upstream
+git pull upstream main --rebase
+
+# Force push if needed
+git push -f
+```
+
+This prevents "branch is out-of-date with base branch" errors.
+
+## Signed Commits
+
+Always sign your commits with `-S` flag:
+
+```bash
+git commit -S -m "Fix description"
+```
+
+If a PR has unsigned commits (e.g., from bots), recreate the changes on a new branch with signed commits:
+
+```bash
+# Fetch original branch
+git fetch origin <branch>
+git checkout FETCH_HEAD
+
+# Make changes, commit with signing
+git add -A
+git commit -S -m "chore: description"
+
+# Push and create new PR
+git push -u origin new-branch-name
+```
+
+## Merging PRs
+
+```bash
+# Merge via GitHub CLI (if you have admin rights)
+gh pr merge <PR_NUMBER> --admin --merge
+
+# Or squash merge
+gh pr merge <PR_NUMBER> --squash --auto --delete-branch
+```
+
+## Commenting on Issues/PRs
+
+```bash
+# Comment on issue
+gh issue comment <ISSUE_NUMBER> --body "Comment text"
+
+# Comment on PR
+gh pr comment <PR_NUMBER> --body "## Summary\n- Details"
+```
+
+### Using HEREDOC for Multi-line Comments
+
+For complex comments with Markdown formatting, HEREDOC avoids shell interpretation issues:
+
+```bash
+# Comment on issue/PR using HEREDOC
+gh pr comment <PR_NUMBER> --body "$(cat <<'EOF'
+## Changes in this PR
+
+### .gitignore additions
+- Added test binaries to prevent accidentally committing test executables
+- Added *.bak for test settings backup files
+
+### New skill: qtpass-github
+A comprehensive skill for GitHub interaction workflows:
+- Reading issues and PRs
+- Responding to users
+- CI debugging
+EOF
+)"
+```
+
+**Key points:**
+
+- Use `$(cat <<'EOF' ... EOF)` to capture the content
+- Quote the `EOF` delimiter (`'EOF'`) to prevent variable expansion
+- Use `\n` for newlines in inline strings (less readable)
+- Use HEREDOC for complex/long comments (more readable)
+
+## Reading Issues and PRs
+
+```bash
+# View issue details
+gh issue view <ISSUE_NUMBER>
+
+# View issue with comments
+gh issue view <ISSUE_NUMBER> --comments
+
+# View issue body only
+gh issue view <ISSUE_NUMBER> --json body
+
+# View PR details
+gh pr view <PR_NUMBER>
+
+# View PR with comments
+gh pr view <PR_NUMBER> --json comments
+
+# Get all PR comments via API
+gh api repos/<owner>/<repo>/pulls/<PR_NUMBER>/comments
+
+# Get all issue comments via API
+gh api repos/<owner>/<repo>/issues/<ISSUE_NUMBER>/comments
+```
+
+## Answering User Questions
+
+When responding to users on issues or PRs:
+
+1. **Read the full context** - Check previous comments and related issues
+2. **Be clear and concise** - Answer directly
+3. **Provide next steps** - Let user know what to expect
+4. **Use Markdown** - Format for readability
+
+Example response templates:
+
+```markdown
+## Investigation
+
+I've looked into this issue. The root cause is...
+
+## Fix
+
+I've implemented a fix that...
+
+## Next Steps
+
+- Review the PR when ready
+- Test on your machine
+- Let me know if you have questions
+```
+
+### Good Practices
+
+- Always acknowledge user's report/feedback
+- Explain technical details in simple terms
+- Provide actionable next steps
+- Follow up on unanswered questions
+- Thank contributors for their input
+
+## Common Patterns
+
+### Pre-PR Checklist
+
+```bash
+# 1. Format files
+npx prettier --write "**/*.md" "**/*.yml"
+
+# 2. Verify formatting
+npx prettier --check "**/*.md"
+
+# 3. Update with main
+git fetch upstream
+git pull upstream main --rebase
+
+# 4. Push
+git push
+```
+
+### Post-Merge Cleanup
+
+```bash
+# Switch to main and update
+git checkout main
+git pull upstream main
+
+# Delete merged branch
+git branch -d <branch-name>
+```
+
+## Debugging CI Failures
+
+When CI checks fail on GitHub:
+
+```bash
+# Get run details
+gh run view <RUN_ID>
+
+# Get full log
+gh run view <RUN_ID> --log
+
+# Filter for errors
+gh run view <RUN_ID> --log | grep -iE "error|fail"
+
+# Check specific job logs
+gh run view <RUN_ID> --job <JOB_NAME> --log
+```
+
+### Common CI Failures
+
+| Failure                   | Likely Cause           | Fix                                 |
+| ------------------------- | ---------------------- | ----------------------------------- |
+| Linting errors            | Formatting issues      | Run `npx prettier --write`          |
+| Test failures             | Bug in code or test    | Run tests locally with `make check` |
+| Build failures            | Missing deps or syntax | Build locally with `make -j4`       |
+| act fails on new branches | `HEAD~0` error         | Skip act, rely on prettier check    |
+
+## Resolving Merge Conflicts
+
+When branch is behind main and has conflicts:
+
+```bash
+# Fetch and rebase
+git fetch upstream
+git checkout <branch>
+git rebase upstream/main
+
+# Resolve conflicts in editor, then:
+git add <resolved-files>
+git rebase --continue
+
+# Force push (since we rewrote history)
+git push -f
+```
+
+## Fork Workflow
+
+If you don't have push access:
+
+```bash
+# Fork repository on GitHub first
+
+# Add your fork as remote
+git remote add myfork git@github.com:<your-username>/QtPass.git
+
+# Push to your fork
+git push -u myfork <branch-name>
+
+# Create PR from your fork to upstream
+gh pr create --base upstream/main --head <your-username>:<branch-name>
+```
+
+Note: When working with forks, use `myfork` for pushing and `upstream` for syncing with main repository.
+
+## Troubleshooting
+
+### "Branch is out-of-date"
+
+```bash
+git checkout <branch-name>
+git pull upstream main --rebase
+git push -f
+```
+
+### Merge Failed
+
+Check if:
+
+1. Branch is behind main → rebase and push
+2. CI still running → wait for checks
+3. Conflicts → resolve locally
+
+### Can't Merge PR
+
+- Check branch protection rules
+- Ensure all CI checks pass
+- You may need admin rights to bypass some checks
+
+### Blocked by Unresolved Review Comments
+
+When PR shows "All comments must be resolved" but you've fixed the issues:
+
+**1. Identify unresolved threads via GraphQL:**
+
+```bash
+gh api graphql -f query='{ repository(owner: "OWNER", name: "REPO") { pullRequest(number: N) { id reviewThreads(first: 20) { nodes { id isResolved } } } } }' | jq -r '.data.repository.pullRequest.reviewThreads.nodes[] | "\(.id) \(.isResolved)"'
+```
+
+**2. Resolve threads programmatically:**
+
+```bash
+# Get thread IDs and resolve them
+THREAD_ID="PRRT_xxx"
+gh api graphql -f query="mutation { resolveReviewThread(input: {threadId: \"$THREAD_ID\"}) { thread { isResolved } } }"
+```
+
+**3. Alternative: Submit a review to clear blocking comments:**
+
+```bash
+# Submit a COMMENT review (not APPROVE if it's your own PR)
+gh api "repos/OWNER/REPO/pulls/N/reviews" -X POST -f "body"="All issues addressed in recent commits" -f "event"="COMMENT"
+```
+
+**4. Common causes:**
+
+- Old CodeRabbit review comments not marked resolved
+- Reviewer requested changes but didn't re-review after fixes
+- Branch protection requires all conversations resolved
+
+## GitHub AI-Powered Bug Detection
+
+GitHub provides AI-generated code quality suggestions under **Security → AI findings**.
+
+### Common AI Findings
+
+1. **Tautology assertions** - Tests that always pass
+2. **Ignored return values** - Test setup not verified
+3. **Spelling corrections** - Typos in comments/strings
+4. **Formatting consistency** - Backticks, spacing
+5. **Contractions** - "can't" vs "cannot"
+6. **Copyright years** - Use "YYYY" placeholder
+
+### Fixing AI Findings
+
+1. Create a branch for fixes:
+
+   ```bash
+   git checkout -b fix/ai-findings
+   ```
+
+2. Apply the suggested fixes
+
+3. Test locally if possible
+
+4. Push and create PR:
+
+   ```bash
+   git push -u origin fix/ai-findings
+   cat <<'EOF' > /tmp/ai-findings-body.md
+   ## Summary
+
+   Found by GitHub AI-powered bug detection.
+
+   - Fixed tautology assertions in tests
+   - Added return value verification
+   - Corrected spelling typos
+   EOF
+   gh pr create --title "fix: resolve AI findings" --body-file /tmp/ai-findings-body.md
+   ```
+
+### Checking AI Findings
+
+```bash
+# View repo security settings (requires admin)
+# Go to: https://github.com/<owner>/<repo>/security/ai-findings
+
+# Or check via API (if enabled)
+gh api repos/<owner>/<repo>/code-scanning/alerts
+```
+
+## Checking PR Status Before Merging
+
+Before merging, always verify:
+
+```bash
+# 1. Check if PR is mergeable
+gh pr view <PR_NUMBER> --json state,mergeable
+
+# 2. Check CI status
+gh pr checks <PR_NUMBER>
+
+# 3. Check for approvals
+gh pr view <PR_NUMBER> --json reviews
+
+# 4. Check if branch is up to date
+gh pr view <PR_NUMBER> --json baseRefName,headRefName
+```
+
+## Pre-Merge Checklist
+
+Before merging a PR:
+
+- [ ] CI checks pass (`gh pr checks`)
+- [ ] At least one approval (for non-trivial changes)
+- [ ] Branch is up to date with main
+- [ ] No unresolved conversations
+- [ ] Tests pass locally (`make check`)
+- [ ] Linter passes (`act push -W .github/workflows/linter.yml`)
+
+```bash
+# Run local CI checks before pushing
+act push -W .github/workflows/linter.yml -j build
+
+# Update with latest main before merging
+git fetch upstream
+git checkout <branch>
+git pull upstream main --rebase
+git push -f
+```
diff --git a/.claude/skills/qtpass-linting/SKILL.md b/.claude/skills/qtpass-linting/SKILL.md
@@ -0,0 +1,332 @@
+---
+name: qtpass-linting
+description: QtPass CI/CD workflow - run GitHub Actions locally with act, linters, formatters
+license: GPL-3.0-or-later
+metadata:
+  audience: developers
+  workflow: linting
+---
+
+# QtPass Linting and CI Workflow
+
+## The Act Pattern
+
+**Always run local CI before pushing PRs.** Use `act` to run GitHub Actions workflows locally.
+
+### Why Use act?
+
+- Catch linter failures **before** pushing
+- Validate changes without waiting for CI
+- Faster iteration loop
+
+### The Workflow
+
+```bash
+# 1. Make your changes
+git add .
+
+# 2. Run linter locally (this is the pattern)
+act push -W .github/workflows/linter.yml -j build
+
+# 3. Fix any issues
+# 4. Push only when act passes
+```
+
+### Quick Reference
+
+| Task                      | Command                                             |
+| ------------------------- | --------------------------------------------------- |
+| Run linter                | `act push -W .github/workflows/linter.yml`          |
+| Run linter (specific job) | `act push -W .github/workflows/linter.yml -j build` |
+| Run build & tests         | `act push -W .github/workflows/ccpp.yml`            |
+| Run docs                  | `act push -W .github/workflows/docs.yml`            |
+| Run reuse check           | `act push -W .github/workflows/reuse.yml`           |
+
+## Available Workflows
+
+### Linter Workflow (.github/workflows/linter.yml)
+
+Runs super-linter with many linters:
+
+- **GITLEAKS** - Secret detection
+- **CHECKOV** - Infrastructure scanning
+- **CLANG_FORMAT** - C++ formatting
+- **ACTIONLINT** - GitHub Actions YAML
+- **PRETTIER** - Web/config file formatting
+- **Markdown** - Markdown linting
+- **NATURAL_LANGUAGE** - Natural language checks
+- **YAML** - YAML linting
+
+```bash
+# Run linter locally
+act push -W .github/workflows/linter.yml -j build
+```
+
+### Build & Test Workflow (.github/workflows/ccpp.yml)
+
+QtPass build with Qt5/Qt6 matrix, runs unit tests, generates coverage:
+
+```bash
+# Run build workflow
+act push -W .github/workflows/ccpp.yml
+```
+
+Tests against:
+
+- Ubuntu + Qt 6.8
+- macOS + Qt 6.8
+- Windows + Qt 6.8
+- Ubuntu + Qt 5.15
+
+Note: Qt installation may fail in act due to environment limitations. Real CI handles this.
+
+### Documentation Workflow (.github/workflows/docs.yml)
+
+```bash
+# Run docs workflow
+act push -W .github/workflows/docs.yml
+```
+
+### Reuse Compliance (.github/workflows/reuse.yml)
+
+Check license headers and REUSE compliance:
+
+```bash
+# Run reuse check
+act push -W .github/workflows/reuse.yml
+```
+
+## Common Linters
+
+### Gitleaks (Secret Detection)
+
+Detects API keys, tokens, passwords in code.
+
+```bash
+# Scan for secrets
+gitleaks detect
+```
+
+**Common Fixes:**
+
+- Don't use test values that look like API keys (e.g., "ABC123DEF456", "sk-xxx")
+- Use generic test strings: "testkey123", "/usr/bin/pass", "example.com"
+
+### Clang Format (C++)
+
+```bash
+# Check formatting
+clang-format --style=file --dry-run src/main.cpp
+
+# Apply formatting
+clang-format --style=file -i src/main.cpp
+```
+
+### Shfmt (Shell Scripts)
+
+Formats shell scripts in `scripts/` folder. Uses LLVM style (matches clang-format).
+
+**Installation:**
+
+```bash
+# macOS
+brew install shfmt
+
+# Go
+go install mvdan.cc/sh/v3/cmd/shfmt@latest
+```
+
+```bash
+# Check formatting
+shfmt -d scripts/*.sh
+
+# Apply formatting
+shfmt -w scripts/*.sh
+```
+
+### Clangd (LSP Analysis)
+
+Clangd provides deep static analysis via LSP. Requires `compile_commands.json`:
+
+```bash
+# Generate compile_commands.json (required for Qt headers)
+./scripts/generate-compile-commands.sh
+
+# Check a specific file for issues
+clangd --check=src/gpgkeystate.cpp
+```
+
+Common diagnostics:
+
+- `[performance-unnecessary-copy-initialization]` - Use `const T&` instead of `const T`
+- `[readability-static-definition]` - Consider making static definitions inline
+
+**Using "(fix available)" in editors:**
+
+| Editor             | Command                          |
+| ------------------ | -------------------------------- |
+| Visual Studio Code | Click 💡 or `Ctrl+.`             |
+| JetBrains          | `Alt+Enter`                      |
+| Neovim             | `:lua vim.lsp.buf.code_action()` |
+
+### Prettier (Web/Config)
+
+```bash
+# Format markdown, YAML, JSON, etc.
+npx prettier --write README.md
+npx prettier --write .github/workflows/*.yml
+npx prettier --write FAQ.md
+npx prettier --write .opencode/skills/*/SKILL.md
+```
+
+## Prettier Patterns
+
+Prettier auto-fixes many linting issues. Run before `act`:
+
+```bash
+# Format all common file types
+npx prettier --write "**/*.md" "**/*.yml" "**/*.json" "**/*.html" "**/*.css"
+```
+
+### Markdown Natural Language Issues
+
+If NATURAL_LANGUAGE fails:
+
+- Use single-word forms instead of two-word combinations
+- Use full terms instead of abbreviations
+- Use proper spacing and punctuation
+
+```bash
+# Run prettier first
+npx prettier --write README.md
+
+# Then check again
+act push -W .github/workflows/linter.yml -j build
+```
+
+## Troubleshooting
+
+### Qt Installation Fails in act
+
+The `install-qt-action` may fail in local act due to missing downloads. This is expected - real CI works fine.
+
+### Linter Fails Due to Missing Files
+
+Some checks need files generated during CI. Run full build first:
+
+```bash
+qmake6 -r CONFIG+=coverage
+make -j4
+```
+
+### Gitleaks False Positives
+
+If gitleaks flags test data:
+
+1. Use generic test values (not like "ABC123DEF456")
+2. Add to `.gitleaksignore` if truly non-sensitive
+
+### act Unknown Flag Error
+
+Make sure act is installed and up to date:
+
+```bash
+# Check version
+act --version
+
+# Update if needed
+brew upgrade act  # or your package manager
+```
+
+## CI Environment Variables
+
+Some linters need secrets or tokens. In local act, these may not be available:
+
+```bash
+# Pass fake token for codecov
+act push -W .github/workflows/ccpp.yml --secret-map "CODECOV_TOKEN=fake"
+```
+
+## GitHub Actions Files
+
+| File                           | Purpose                    |
+| ------------------------------ | -------------------------- |
+| `.github/workflows/linter.yml` | Super-linter (many checks) |
+| `.github/workflows/ccpp.yml`   | Build & test with Qt       |
+| `.github/workflows/docs.yml`   | Doxygen docs generation    |
+| `.github/workflows/reuse.yml`  | REUSE compliance           |
+| `.github/super-linter.env`     | Linter configuration       |
+
+## Run Before PR Checklist
+
+**THIS IS THE PATTERN - always run before pushing:**
+
+```bash
+# 1. Format files with prettier (always do this)
+npx prettier --write "**/*.md" "**/*.yml"
+
+# 2. Verify formatting passes (REQUIRED - catches linting issues)
+npx prettier --check "**/*.md"
+
+# 3. Run act linter (recommended before opening PR)
+act push -W .github/workflows/linter.yml -j build
+
+# 4. Update with latest main (if branch is behind)
+git fetch upstream
+git pull upstream main --rebase
+
+# 5. Then push
+git push
+```
+
+**Note:** Prettier catches most issues. act is recommended but may fail on new branches (see below).
+
+### Note on act
+
+**`act` may fail on new branches with error:** `fatal: ambiguous argument 'HEAD~0'`
+
+This is a known issue with the tool, not your code. When this happens:
+
+- Skip the act step
+- The `prettier --check` step is sufficient for most cases
+- Trust that formatting is correct
+- The real GitHub CI will pass
+
+**Recommended alternative - use prettier --check directly:**
+
+```bash
+# This catches most linting issues without needing act
+npx prettier --check "**/*.md"
+npx prettier --check "**/*.yml"
+```
+
+### Before Merging
+
+**Before merging a PR, always update it with latest main:**
+
+```bash
+git checkout <branch-name>
+git pull upstream main --rebase
+git push -f
+```
+
+This prevents "branch is out-of-date with base branch" errors when merging.
+
+## IDE/LSP Setup
+
+For proper code completion and analysis in editors like Visual Studio Code with clangd, generate `compile_commands.json`:
+
+```bash
+# Generate compile_commands.json using bear
+./scripts/generate-compile-commands.sh
+```
+
+This provides Qt include paths so the LSP can resolve types like `QString`, `QProcess`, etc.
+
+**Note:** `compile_commands.json` is in `.gitignore` - regenerate after cleaning or re-configuring.
+
+## Related Skills
+
+- **qtpass-testing** - For testing patterns and `make check`
+- **qtpass-fixing** - For bugfix workflow with tests
+- **qtpass-releasing** - For release process
diff --git a/.claude/skills/qtpass-localization/SKILL.md b/.claude/skills/qtpass-localization/SKILL.md
@@ -0,0 +1,269 @@
+---
+name: qtpass-localization
+description: QtPass localization workflow - translation files, updating, adding languages
+license: GPL-3.0-or-later
+metadata:
+  audience: developers
+  workflow: localization
+---
+
+# QtPass Localization
+
+## Translation Files
+
+Location: `localization/localization_<lang>.ts`
+
+Qt uses Qt Linguist (`.ts` files) for translations.
+
+### Existing Languages
+
+```bash
+ls localization/localization_*.ts
+```
+
+Currently includes: af_ZA, ar_MA, bg_BG, ca_ES, cs_CZ, cy_GB, da_DK, de_DE, de_LU, el_GR, en_GB, en_US, es_ES, et_EE, fi_FI, fr_BE, fr_FR, fr_LU, gl_ES, he_IL, hr_HR, hu_HU, it_IT, ja_JP, ko_KR, lb_LU, nb_NO, nl_BE, nl_NL, pl_PL, pt_PT, ro_RO, ru_RU, sk_SK, sl_SI, sq_AL, sr_RS, sv_SE, ta, tr_TR, uk_UA, zh_CN, zh_Hant
+
+## Updating Translations
+
+### After Code Changes
+
+When source files change (strings added, moved, or refactored), run qmake to update translations:
+
+```bash
+# IMPORTANT: Run distclean first to avoid stale generated files (ui_*.h) in translations
+make distclean
+
+# Run qmake to update translations (uses lupdate internally)
+qmake6
+```
+
+This updates all `.ts` files with:
+
+- Source file line numbers
+- File references (if files renamed)
+- **Source text** (if changed in source files - important!)
+- Translation status (set to "unfinished" when source changed)
+
+### What Stays the Same
+
+- Translated text (in `<translation>` tags)
+- Completed translations remain as-is until re-translated
+
+### Creating a PR for Updates
+
+```bash
+# Create branch
+git checkout -b chore/update-localization
+
+# Add and commit
+git add localization/
+git commit -m "chore: update localization source references"
+
+# Push and create PR
+git push -u origin chore/update-localization
+gh pr create --title "chore: update localization source references" --body "## Summary
+
+- Updated translation files with current source texts and line numbers
+- Translations marked unfinished where source text changed
+"
+```
+
+## Adding New Strings
+
+When you add new user-facing strings in C++:
+
+```cpp
+// Use tr() for translatable strings
+ui->label->setText(tr("New text here"));
+```
+
+### Qt Linguist Workflow
+
+1. Open `localization/localization_en_US.ts` in Qt Linguist
+2. Find untranslated strings
+3. Fill in translations
+4. Save (automatically updates the .ts file)
+
+### Key Conventions
+
+- Use `tr()` for all user-facing strings
+- Don't translate placeholders like `%1`, `%2`, `%3`
+- Preserve `\n` for line breaks
+- Keep technical terms consistent (e.g., "GPG", "clipboard")
+- Use context comments to help translators understand usage
+
+### String Formatting
+
+```cpp
+// Good
+tr("Delete %1?").arg(filename)
+tr("Found %n password(s)", count)
+
+// Avoid
+tr("Delete " + filename + "?")  // Can't be translated properly
+```
+
+## Adding New Language
+
+1. Copy base translation file:
+
+   ```bash
+   cp localization/localization_en_US.ts localization/localization_XX_YY.ts
+   ```
+
+2. Update language code (ISO 639-1 + country code)
+
+3. Add to build config in `qtpass.pro`:
+
+   ```pro
+   TRANSLATIONS += localization/localization_XX_YY.ts
+   ```
+
+4. Run qmake to register:
+
+   ```bash
+   qmake6
+   ```
+
+5. Translate strings using Qt Linguist
+
+## Building Translations
+
+### Generate .qm Files
+
+```bash
+# For development (or part of build process)
+lrelease localization/*.ts
+
+# Or via qmake
+make translations
+```
+
+### .qm Files
+
+- Binary format, loaded at runtime
+- Generated from .ts files
+- Typically not committed (generated during build)
+
+## Localization Testing
+
+### Switch Language
+
+QtPass uses system locale. To test:
+
+```bash
+# Linux
+LANG=nl_NL ./qtpass
+
+# Or set in QtPass settings
+```
+
+### Debug Translation Issues
+
+```cpp
+// Enable verbose translation debugging
+QTranslator translator;
+if (translator.load(QLocale(), "qtpass", "_", ":/languages")) {
+    qDebug() << "Loaded translation for:" << QLocale().name();
+}
+```
+
+## Common Issues
+
+### Strings Not Showing Translated
+
+1. String not wrapped in `tr()` - fix in source
+2. Translation file not loaded - check .pro TRANSLATIONS
+3. .qm file not generated - run lrelease
+4. Wrong locale - check system language settings
+
+### Translation File Conflicts
+
+When merging PRs with translation updates:
+
+```bash
+# Fetch and rebase
+git fetch origin
+git pull origin main --rebase
+
+# Resolve conflicts in .ts files (usually just XML merge)
+# Test with qmake6
+```
+
+## Linting
+
+```bash
+# Format with prettier if needed
+npx prettier --write localization/*.ts
+```
+
+## Common Pitfalls
+
+### Forgetting distclean Before qmake
+
+Always run `make distclean` before `qmake6` when updating translations:
+
+```bash
+# Wrong - may include stale generated files in translations
+qmake6
+
+# Correct - starts fresh
+make distclean
+qmake6
+```
+
+### New Strings Not Showing in Qt Linguist
+
+If you added new `tr()` strings but they don't appear:
+
+1. Run `qmake6` to update the `.ts` files
+2. Close and reopen Qt Linguist
+3. Check the file was actually saved after previous edit
+
+### Translation Files Showing as "Finished"
+
+When source strings change, translations are marked "unfinished" but may still appear correct. Always check:
+
+- The source text in Qt Linguist matches your code
+- Any placeholder formatting (`%1`, `%2`) matches
+
+### Merging Translation Conflicts
+
+When merging translation PRs that conflict:
+
+```bash
+# Use theirs strategy for .ts files (they're XML, prefer incoming)
+git checkout --theirs localization/localization_*.ts
+git add localization/
+git commit -m "Resolve merge conflict - use theirs for translations"
+```
+
+### Weblate vs Local Editing
+
+QtPass uses Weblate for translations. Don't manually edit `.ts` files for translations - let Weblate handle it. Only run `qmake6` locally to update source references.
+
+## Fixing Translation Issues in PRs
+
+When static analysis flags translation issues (e.g., filename preservation):
+
+```bash
+# Fetch the PR branch
+git fetch origin refs/pull/<PR>/head:pr/<PR>-fix
+git checkout pr/<PR>-fix
+
+# Fix the translation
+# Edit the .ts file to preserve exact filename/token
+
+# Commit with signing and push
+git add localization/localization_<lang>.ts
+git commit -S -m "fix: preserve .gpg-id filename in <lang> translation"
+git push -u origin pr/<PR>-fix
+```
+
+### Squash Merge Pattern
+
+Translation PRs often use squash merge:
+
+```bash
+gh pr merge <PR_NUMBER> --squash --auto --delete-branch
+```
diff --git a/.claude/skills/qtpass-releasing/SKILL.md b/.claude/skills/qtpass-releasing/SKILL.md
@@ -0,0 +1,210 @@
+---
+name: qtpass-releasing
+description: Release workflow for QtPass - versioning, builds, publishing
+license: GPL-3.0-or-later
+metadata:
+  audience: developers
+  workflow: release
+---
+
+# Release Workflow for QtPass
+
+## Release Checklist
+
+### 1. Version Bump
+
+Update version in all build files:
+
+- `qtpass.pri` - `VERSION = X.Y.Z` (note: .pri not .pro, unquoted number)
+- `qtpass.spec` - `Version:`
+- `qtpass.iss` - `AppVerName=`
+- `Doxyfile` - `PROJECT_NUMBER`
+- `downloads.html` (gh-pages) - multiple references
+- `index.html` (gh-pages)
+- `getting-started.html` (gh-pages)
+- `changelog.html` (gh-pages)
+- `changelog.1.4.html` (gh-pages)
+- `old.html` (gh-pages)
+
+**NOTE:** `qtpass.appdata.xml` and `appdmg.json` don't have version fields to update.
+
+```bash
+# Find version strings (replace X.Y with actual version)
+grep -rn "X\.Y" qtpass.pri qtpass.spec qtpass.iss Doxyfile
+```
+
+### 2. Changelog
+
+Update `CHANGELOG.md`:
+
+- Add release date
+- List all merged PRs and fixed issues
+- Group by: Added, Changed, Fixed, Removed
+
+### 3. Tests
+
+```bash
+# Run full test suite
+make check
+```
+
+### 4. Build Artifacts
+
+#### Linux
+
+```bash
+# Create source tarball
+./scripts/release-linux.sh
+
+# Or manually:
+git archive --prefix=qtpass-x.y.z/ -o qtpass-x.y.z.tar.gz HEAD
+```
+
+#### macOS
+
+```bash
+./scripts/release-mac.sh
+```
+
+#### Windows
+
+```bash
+# Via GitHub Actions or locally with Inno Setup
+qtpass.iss
+```
+
+### 5. Git Tags
+
+```bash
+git tag -a vX.Y.Z -m "QtPass vX.Y.Z Release"
+git push origin vX.Y.Z
+```
+
+### 6. GitHub Release
+
+```bash
+gh release create vX.Y.Z \
+  --title "QtPass vX.Y.Z" \
+  --notes-file CHANGELOG.md \
+  qtpass-x.y.z.tar.gz
+```
+
+### 7. GitHub Pages (site)
+
+Update version in HTML files on `gh-pages` branch:
+
+```bash
+git checkout gh-pages
+
+# Update downloads.html (download links)
+# Update index.html (main page)
+# Update getting-started.html
+# Update changelog.html (add new release notes + version)
+# Update changelog.1.4.html, old.html (version only)
+
+git add -A
+git commit -m "Release vX.Y.Z"
+git push origin gh-pages
+```
+
+**Common version search:**
+
+```bash
+grep -rn "1\.5" *.html
+```
+
+## Version Numbering
+
+Follow semantic versioning: MAJOR.MINOR.PATCH
+
+- MAJOR: Breaking changes
+- MINOR: New features, backward compatible
+- PATCH: Bugfixes, backward compatible
+
+## Build Locations
+
+| Platform | Output                   |
+| -------- | ------------------------ |
+| Linux    | `qtpass-x.y.z.tar.gz`    |
+| macOS    | `QtPass-x.y.z.dmg`       |
+| Windows  | `QtPass-Setup-x.y.z.exe` |
+
+## CI/CD
+
+Release workflow via GitHub Actions: `.github/workflows/release-installers.yml`
+
+## Linting
+
+See `qtpass-linting` skill for full CI workflow. Pattern:
+
+```bash
+# Run linter locally BEFORE pushing
+act push -W .github/workflows/linter.yml -j build
+```
+
+## Protected Main Branch
+
+`main` is protected - cannot push directly. Must create PR from a release branch:
+
+```bash
+# Create release branch
+git checkout -b release/vX.Y.Z
+
+# Make changes, commit
+git add -A
+git commit -m "Release vX.Y.Z"
+
+# Update with latest main before pushing
+git fetch upstream
+git rebase upstream/main
+
+# Push branch (force-with-lease since we rebased)
+git push origin release/vX.Y.Z --force-with-lease
+
+# Create PR
+gh pr create --base main --head release/vX.Y.Z --title "Release vX.Y.Z"
+```
+
+## Script Best Practices
+
+### Dry Run Option
+
+For scripts that modify remote state (uploading releases, signing files), add a `--dryrun` flag to enable testing without making changes:
+
+```bash
+# Parse arguments at the start
+dryrun=false
+while [ $# -gt 0 ]; do
+    case "$1" in
+        --dryrun)
+            dryrun=true
+            shift
+            ;;
+        *)
+            break
+            ;;
+    esac
+done
+
+# Use in conditional
+if [ "$dryrun" = true ]; then
+    echo "[dryrun] Would upload files: ${files[*]}"
+else
+    gh release upload ...
+fi
+```
+
+### Glob Handling
+
+When iterating over files matched by a glob pattern, use array assignment to handle the case where no files match:
+
+```bash
+# Without nullglob, loops over literal "*" when no files exist
+for file in *; do
+    [ -f "$file" ] || continue
+
+# With array assignment, iterates over empty array when no files
+files=(*)
+for file in "${files[@]}"; do
+    [ -f "$file" ] || continue
+```
diff --git a/.claude/skills/qtpass-testing/SKILL.md b/.claude/skills/qtpass-testing/SKILL.md
@@ -0,0 +1,512 @@
+---
+name: qtpass-testing
+description: Comprehensive guide for QtPass unit testing with Qt Test
+license: GPL-3.0-or-later
+metadata:
+  audience: developers
+  workflow: testing
+---
+
+# QtPass Testing Guide
+
+## Project Overview
+
+QtPass is a Qt6/C++ password manager GUI for `pass`. Tests use Qt Test framework.
+
+## Quick Start
+
+```bash
+# Build and run all tests
+make check
+
+# Build with coverage
+qmake6 -r CONFIG+=coverage
+make -j4
+
+# Generate coverage report
+make lcov
+```
+
+## Existing Test Suites (8 total)
+
+### tests/auto/gpgkeystate/tst_gpgkeystate.cpp
+
+Tests for `src/gpgkeystate.cpp`:
+
+- `parseMultiKeyPublic()` - Multiple public keys parsing
+- `parseSecretKeys()` - Secret key detection (have_secret flag)
+- `parseSingleKey()` - Single key with and without fingerprint
+- `parseKeyRollover()` - Multiple keys in sequence
+- `classifyRecordTypes()` - GPG record type classification (pub, sec, uid, fpr, etc.)
+
+### Test Fixtures
+
+Store sample test data in `tests/fixtures/`:
+
+```bash
+ls tests/fixtures/
+# gpg-colons-multi-key.txt
+# gpg-colons-public.txt
+# gpg-colons-secret.txt
+```
+
+These contain real GPG `--with-colons` output for deterministic testing.
+
+### tests/auto/util/tst_util.cpp
+
+Tests for `src/util.cpp`:
+
+- `normalizeFolderPath()` - Path normalization
+- `fileContent()` / `fileContentEdgeCases()` - FileContent parsing
+- `regexPatterns()` / `regexPatternEdgeCases()` - URL detection regular expression
+- `totpHiddenFromDisplay()` - OTP field hiding
+- `userInfoValidity()` - User key validation
+- `passwordConfigurationCharacters()` - Password character sets
+- `simpleTransaction*()` - SimpleTransaction tests
+
+### tests/auto/filecontent/tst_filecontent.cpp
+
+Tests for `src/filecontent.h`:
+
+- `parsePlainPassword()` - Single-line password
+- `parsePasswordWithNamedFields()` - Password with key:value
+- `parseWithTemplateFields()` - Template field parsing
+- `parseWithAllFields()` - All fields mode
+- `getRemainingData()` - Non-template fields
+- `getRemainingDataForDisplay()` - Hides otpauth://
+- `namedValuesTakeValue()` / `namedValuesTakeValueNotFound()`
+
+### tests/auto/passwordconfig/tst_passwordconfig.cpp
+
+Tests for `src/passwordconfiguration.h`:
+
+- `passwordConfigurationDefaults()` - Default values
+- `passwordConfigurationSetters()` - Setter methods
+- `passwordConfigurationCharacterSets()` - Character set config
+
+### tests/auto/executor/tst_executor.cpp
+
+Tests for `src/executor.h`:
+
+- `executeBlockingEcho()` - Basic execution
+- `executeBlockingWithArgs()` - Arguments handling
+- `executeBlockingExitCode()` - Exit code checking (Unix only)
+- `executeBlockingStderr()` - Error output capture (Unix only)
+
+### tests/auto/model/tst_storemodel.cpp
+
+Tests for `src/storemodel.h`:
+
+- `dataRemovesGpgExtension()` - Display name filtering
+- `flagsWithValidIndex()` / `flagsWithInvalidIndex()` - Item flags
+- `mimeTypes()` - Drag/drop MIME types
+- `lessThan()` - Sorting comparison
+- `supportedDropActions()` / `supportedDragActions()`
+- `filterAcceptsRowHidden()` / `filterAcceptsRowVisible()`
+
+### tests/auto/settings/tst_settings.cpp
+
+Tests for `src/qtpasssettings.h`:
+
+- Uses set+get pattern for each setting
+- Tests isUseGit(), setUseGit(), etc.
+
+### tests/auto/ui/tst_ui.cpp
+
+UI tests:
+
+- `contentRemainsSame()` - Password content integrity
+- `emptyPassword()` - Empty password handling
+- `multilineRemainingData()` - Multiline field handling
+
+## Test File Template
+
+```cpp
+// SPDX-FileCopyrightText: YYYY Your Name
+// SPDX-License-Identifier: GPL-3.0-or-later
+#include <QtTest>
+
+#include "../../../src/mymodule.h"
+
+class tst_mymodule : public QObject {
+  Q_OBJECT
+
+private Q_SLOTS:
+  void initTestCase();
+  void testBasicFunction();
+  void testEdgeCase();
+  void cleanupTestCase();
+};
+
+void tst_mymodule::initTestCase() {}
+
+void tst_mymodule::testBasicFunction() {
+    // Use set+get pattern or direct input/output
+    QString result = MyModule::process("input");
+    QVERIFY2(result == "expected", "Should return expected output");
+}
+
+void tst_mymodule::testEdgeCase() {
+    // Test empty, null, boundary conditions
+    QVERIFY(MyModule::process("").isEmpty());
+}
+
+void tst_mymodule::cleanupTestCase() {}
+
+QTEST_MAIN(tst_mymodule)
+#include "tst_mymodule.moc"
+```
+
+## .pro File Template
+
+```pro
+!include(../auto.pri) { error("Couldn't find the auto.pri file!") }
+
+SOURCES += tst_mymodule.cpp
+
+LIBS = -L"$$OUT_PWD/../../../src/$(OBJECTS_DIR)" -lqtpass $$LIBS
+clang|gcc:PRE_TARGETDEPS += "$$OUT_PWD/../../../src/$(OBJECTS_DIR)/libqtpass.a"
+
+HEADERS   += mymodule.h
+
+OBJ_PATH += ../../../src/$(OBJECTS_DIR)
+
+VPATH += ../../../src
+INCLUDEPATH += ../../../src
+
+win32 {
+    RC_FILE = ../../../windows.rc
+    QMAKE_LINK_OBJECT_MAX=24
+}
+```
+
+## Test plist File Template (qtpass.plist)
+
+```xml
+<?xml version="1.0" encoding="UTF-8"?>
+<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
+<plist version="1.0">
+<dict>
+    <key>QMTestSpecification</key>
+    <dict>
+        <key>Type</key>
+        <string>Bundle</string>
+        <key>UIElement</key>
+        <dict>
+            <key>Modified</key>
+            <false/>
+            <key>SystemEntity</key>
+            <string>Test</string>
+        </dict>
+    </dict>
+</dict>
+</plist>
+```
+
+## Adding a New Test Suite
+
+1. Create directory: `tests/auto/<name>/`
+2. Add `<name>.pro` file (copy pattern above)
+3. Add `qtpass.plist` (copy from model/)
+4. Add `tst_<name>.cpp` test file
+5. Add to `tests/auto/auto.pro`: `SUBDIRS += <name>`
+6. Rebuild: `qmake6 -r && make -j4`
+7. Run: `make check`
+
+## Best Practices
+
+### Test Naming
+
+- Test file: `tst_<classname>.cpp`
+- Test class: `tst_<classname>`
+- Test methods: `testMethodName()` or `methodDoesWhat()`
+
+### Test Organization
+
+- `initTestCase()` - Setup (runs once before all tests)
+- `init()` - Setup before each test
+- Test methods in logical order
+- `cleanupTestCase()` - Teardown (runs once after all tests)
+
+### Assertions
+
+```cpp
+// Basic
+QVERIFY(condition);
+QVERIFY2(condition, "failure message");
+
+// Equality
+QCOMPARE(actual, expected);
+QCOMPARE2(actual, expected, "message");
+
+// String matching
+QVERIFY2(output.contains("needle"), "should contain needle");
+QCOMPARE(QString("hello").toUpper(), QString("HELLO"));
+```
+
+### Never use `||` in assertions
+
+Bad (tautology or ambiguous):
+
+```cpp
+QVERIFY(result == expected || result == INVALID);  // unclear intent
+QVERIFY(result != INVALID || result == INVALID);  // ALWAYS TRUE - tautology!
+```
+
+Good - just call the method to verify it doesn't crash:
+
+```cpp
+simpleTransaction trans;
+trans.transactionAdd(Enums::PASS_INSERT);
+trans.transactionIsOver(Enums::PASS_INSERT);  // verify it runs without crash
+```
+
+Or use deterministic setup with `QCOMPARE`:
+
+```cpp
+simpleTransaction st;
+st.transactionAdd(Enums::PASS_INSERT);
+Enums::PROCESS result = st.transactionIsOver(Enums::PASS_INSERT);
+QCOMPARE(result, Enums::PASS_INSERT);  // deterministic
+```
+
+### QtTest Macros
+
+- `QFAIL("message")` - Fail with message
+- `QSKIP("message")` - Skip test
+- `QCOMPARE(a, b)` - Assert equality
+- `QVERIFY(a)` - Assert true
+- `QVERIFY2(a, msg)` - Assert with message
+
+### Windows Compatibility
+
+```cpp
+void tst_executor::unixOnlyTest() {
+#ifndef Q_OS_WIN
+    // Test code here
+#endif
+}
+```
+
+### Path Comparison on Windows
+
+Windows uses backslashes (`\`) while Unix uses forward slashes (`/`). When comparing paths, use `QDir::cleanPath()` to normalize:
+
+```cpp
+void tst_util::testPathComparison() {
+    QString path = Pass::getGpgIdPath(passStore);
+    QString expected = passStore + "/.gpg-id";
+    // Use cleanPath to normalize for cross-platform compatibility
+    QVERIFY2(QDir::cleanPath(path) == QDir::cleanPath(expected),
+             qPrintable(QString("Expected %1, got %2")
+                        .arg(QDir::cleanPath(expected), QDir::cleanPath(path))));
+}
+```
+
+### Test Settings Pollution
+
+Tests that modify QtPass settings can pollute the user's live config. This is especially problematic on Windows where settings use the registry.
+
+**Solution: Backup and restore settings in tests**
+
+```cpp
+// In tst_settings::initTestCase()
+void tst_settings::initTestCase() {
+    // Check for portable mode (qtpass.ini in app directory)
+    QString portable_ini = QCoreApplication::applicationDirPath() +
+                         QDir::separator() + "qtpass.ini";
+    bool isPortableMode = QFile::exists(portable_ini);
+
+    if (isPortableMode) {
+        // Backup settings file
+        QtPassSettings::getInstance()->sync();
+        QString settingsFile = QtPassSettings::getInstance()->fileName();
+        m_settingsBackupPath = settingsFile + ".bak";
+        QFile::remove(m_settingsBackupPath);
+        QFile::copy(settingsFile, m_settingsBackupPath);
+    } else {
+        // Warn on non-portable mode (registry on Windows)
+        qWarning() << "Non-portable mode detected. Tests may modify registry settings.";
+    }
+}
+
+// In tst_settings::cleanupTestCase()
+void tst_settings::cleanupTestCase() {
+    // Restore original settings after all tests
+    if (isPortableMode && !m_settingsBackupPath.isEmpty()) {
+        QString settingsFile = QtPassSettings::getInstance()->fileName();
+        QFile::remove(settingsFile);
+        QFile::copy(m_settingsBackupPath, settingsFile);
+        QFile::remove(m_settingsBackupPath);
+    }
+}
+```
+
+**Key points:**
+
+- Only backup in portable mode (file-based settings)
+- On registry mode (Windows non-portable), warn but cannot back up
+- Always restore after tests to prevent pollution
+
+### Gitleaks-Safe Test Values
+
+- DON'T: "ABC123DEF456", "sk-xxx", real API keys
+- DO: "testkey123", "/usr/bin/pass", "example.com"
+
+### Qt5/Qt6 Compatibility
+
+When checking variant types, prefer `canConvert<T>()` over `metaType().id()` for broader compatibility:
+
+```cpp
+// Qt6-only (fails on Qt5)
+QVERIFY(displayData.metaType().id() == QMetaType::QString);
+
+// Qt5/Qt6 compatible
+QVERIFY(displayData.canConvert<QString>());
+```
+
+### Temporary Files/Directories
+
+```cpp
+void tst_mymodule::testWithTempFile() {
+    QTemporaryDir tempDir;
+    QString filePath = tempDir.path() + "/test.txt";
+    QFile file(filePath);
+    QVERIFY(file.open(QIODevice::WriteOnly));
+    file.write("test data");
+    file.close();
+    // Test reads/modifies file
+}
+```
+
+### Testing Getters with Default Parameters
+
+When testing settings that have getters with default parameters, pass a _different_ default value to verify persistence:
+
+```cpp
+// Bad - returns default if persistence fails
+setter(testValue);
+QCOMPARE(getter(testValue), testValue);
+
+// Good - uses different default, must return stored value
+setter(testValue);
+QCOMPARE(getter(!testValue), testValue);        // bool: use negation
+QCOMPARE(getter(-1), testValue);                 // int: use sentinel
+QCOMPARE(getter(QString()), testValue);          // string: use empty
+```
+
+### Compound Types Don't Always Fit Data-Driven
+
+Data-driven tests work well for simple bool/int/string settings. Compound types like `PasswordConfiguration` often don't fit:
+
+- Different tests test different fields (length vs selected vs characters)
+- Nested data (QMap, structs) complicates the table
+- Keep tests explicit and readable over forcing a pattern
+
+### Qt Test Macro Reminder
+
+Always use the proper Qt Test macros:
+
+```cpp
+// Good
+QCOMPARE(actual, expected);
+QVERIFY(condition);
+QVERIFY2(condition, "failure message");
+
+// Bad - won't compile or is confusing
+COMPARE(actual, expected);      // missing Q
+QQCOMPARE(actual, expected);     // extra Q
+```
+
+## Testable Source Files
+
+### src/util.h/cpp
+
+- `normalizeFolderPath()` - Path normalization
+- `protocolRegex()` - URL detection
+- `endsWithGpg()` - Extension matching
+- `newLinesRegex()` - Newline detection
+
+### src/filecontent.h/cpp
+
+- `FileContent::parse()` - Parse password file
+- `getPassword()` - Get main password
+- `getNamedValues()` - Get key:value fields
+- `getRemainingData()` - Non-template fields
+- `getRemainingDataForDisplay()` - Display-safe (hides OTP)
+- `NamedValues::takeValue()` - Extract and remove value
+
+### src/passwordconfiguration.h
+
+- `PasswordConfiguration` class
+- Character set definitions
+- Length configuration
+
+### src/executor.h/cpp
+
+- `Executor::executeBlocking()` - Run command synchronously
+- Returns exit code, captures output/stderr
+
+### src/storemodel.h/cpp
+
+- `StoreModel` extends QFileSystemModel
+- `setModelAndStore()` - Initialize with model and path
+- `data()` - Returns display name (removes .gpg)
+- `flags()` - Item flags
+- `lessThan()` - Sorting
+
+### src/qtpasssettings.h
+
+- 26+ settings: isUseGit(), setUseGit(), isUseMonospace(), etc.
+
+## CI Integration
+
+Tests run via `make check` in CI. Coverage reported with `make lcov`.
+
+## Linting
+
+See `qtpass-linting` skill for full CI workflow. Pattern:
+
+```bash
+# Run linter locally BEFORE pushing
+act push -W .github/workflows/linter.yml -j build
+```
+
+### Web/Config Files (prettier)
+
+Formats: .md, .yml, .html, .css, .js, .json, etc.
+
+```bash
+npx prettier --write <file>
+npx prettier --write .github/workflows/*.yml
+npx prettier --write .opencode/skills/*/SKILL.md
+```
+
+### C++ (clang-format)
+
+```bash
+# Check formatting
+clang-format --style=file --dry-run src/main.cpp
+
+# Apply formatting
+clang-format --style=file -i src/main.cpp
+```
+
+### Project Lint
+
+```bash
+make check  # Runs tests and builds
+```
+
+## Debugging Failed Tests
+
+```bash
+# Run single test
+./tests/auto/util/tst_util testName
+
+# Verbose output
+./tests/auto/util/tst_util -v2
+
+# Detailed timing
+./tests/auto/util/tst_util -vs
+```
PATCH

echo "Gold patch applied."
