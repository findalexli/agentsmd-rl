#!/usr/bin/env bash
set -euo pipefail

cd /workspace/qtpass

# Idempotency guard
if grep -qF "In ConfigDialog, use `getProfiles()`/`setProfiles()` to preserve non-selected pr" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -229,6 +229,86 @@ returns `\\`.
 See `Pass::getGpgIdPath` in `src/pass.cpp` for the canonical implementation;
 this pattern supports nested folder inheritance.
 
+### Profile Git Settings
+
+Git options (useGit, autoPush, autoPull) are stored per-profile:
+
+```cpp
+bool useGit = QtPassSettings::getProfileUseGit(profileName, false);
+QtPassSettings::setProfileUseGit(profileName, true);
+QtPassSettings::setProfileAutoPush(profileName, true);
+QtPassSettings::setProfileAutoPull(profileName, false);
+```
+
+In ConfigDialog, use `getProfiles()`/`setProfiles()` to preserve non-selected profile settings:
+
+```cpp
+setProfiles(QtPassSettings::getProfiles(), QtPassSettings::getProfile());
+QtPassSettings::setProfiles(getProfiles());
+```
+
+### QSettings Singleton Pattern
+
+QtPass uses `QtPassSettings::getInstance()` instead of raw `QSettings`:
+
+```cpp
+QtPassSettings::getInstance()->setValue("key", value);
+QtPassSettings::getInstance()->beginGroup("profile");
+QtPassSettings::getInstance()->remove(profileName);
+QtPassSettings::getInstance()->endGroup();
+```
+
+Always match the settings backend used by QtPass in tests.
+
+### MainWindow Add Entry Pattern
+
+```cpp
+void MainWindow::addPassword() {
+    bool ok;
+    QString dir =
+        Util::getDir(ui->treeView->currentIndex(), true, model, proxyModel);
+    QString file =
+        QInputDialog::getText(this, tr("New file"),
+                              tr("New password file: \n(Will be placed in %1 )")
+                                  .arg(QtPassSettings::getPassStore() +
+                                       Util::getDir(ui->treeView->currentIndex(),
+                                                    true, model, proxyModel)),
+                              QLineEdit::Normal, "", &ok);
+    if (!ok || file.isEmpty()) {
+        return;
+    }
+    file = dir + file;
+    setPassword(file);
+}
+```
+
+### ConfigDialog Profile Table Selection
+
+```cpp
+void ConfigDialog::onProfileTableSelectionChanged() {
+    QList<QTableWidgetItem *> selected = ui->profileTable->selectedItems();
+    if (selected.isEmpty()) return;
+    QString profileName = ui->profileTable->item(selected.first()->row(), 0)->text();
+    loadGitSettingsForProfile(profileName, m_profiles);
+}
+```
+
+Cache profiles in `m_profiles` member and update on `getProfiles()`.
+
+### Avoid Setter Side Effects in Loops
+
+```cpp
+// Bad - triggers update logic for each profile
+for (const auto &profile : profiles) {
+    setUseGit(profile.useGit);  // Side effects!
+}
+// Good
+for (const auto &profile : profiles) {
+    ui->checkBoxUseGit->setChecked(profile.useGit);
+}
+useGit(selected.useGit);
+```
+
 ## Handling AI Findings
 
 When CodeRabbit/CodeAnt AI flags issues in PRs:
PATCH

echo "Gold patch applied."
