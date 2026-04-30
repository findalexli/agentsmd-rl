#!/usr/bin/env bash
set -euo pipefail

cd /workspace/qtpass

# Idempotency guard
if grep -qF "AGENTS.md" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -229,109 +229,6 @@ returns `\\`.
 See `Pass::getGpgIdPath` in `src/pass.cpp` for the canonical implementation;
 this pattern supports nested folder inheritance.
 
-### Profile Git Settings
-
-Git options (useGit, autoPush, autoPull) are now stored per-profile:
-
-```cpp
-// Get profile git settings
-QString useGitStr = QtPassSettings::getProfileUseGit(profileName, false);
-
-// Set profile git settings
-QtPassSettings::setProfileUseGit(profileName, true);
-QtPassSettings::setProfileAutoPush(profileName, true);
-QtPassSettings::setProfileAutoPull(profileName, false);
-```
-
-In ConfigDialog, use `QtPassSettings::getProfiles()` to get all profiles, and
-`setProfiles()` to save. The `getProfiles()`/`setProfiles()` cycle preserves
-Git settings for non-selected profiles:
-
-```cpp
-// Load profiles into dialog
-setProfiles(QtPassSettings::getProfiles(), QtPassSettings::getProfile());
-
-// Save profiles from dialog (preserves non-selected git settings)
-QtPassSettings::setProfiles(getProfiles());
-```
-
-### QSettings Singleton Pattern
-
-QtPass uses `QtPassSettings::getInstance()` instead of raw `QSettings`:
-
-```cpp
-// Good - uses singleton
-QtPassSettings::getInstance()->setValue("key", value);
-
-// Test cleanup - also use singleton
-QtPassSettings::getInstance()->beginGroup("profile");
-QtPassSettings::getInstance()->remove(profileName);
-QtPassSettings::getInstance()->endGroup();
-```
-
-Always match the settings backend used by QtPass in tests.
-
-### MainWindow Add Entry Pattern
-
-When adding new password entries, call `setTemplate()` on the dialog:
-
-```cpp
-void MainWindow::addPasswordEntry() {
-    PasswordDialog passDialog(this);
-    // Check for per-folder template
-    QString templateName = Util::getFolderTemplate(currentDir, storePath);
-    QHash<QString, QStringList> templates = Util::readTemplates(storePath);
-    passDialog.setAvailableTemplates(templates, templateName);
-    passDialog.exec();
-}
-```
-
-### ConfigDialog Profile Table Selection
-
-When handling profile table selection changes:
-
-```cpp
-void ConfigDialog::onProfileTableSelectionChanged() {
-    QList<QTableWidgetItem *> selected = ui->profileTable->selectedItems();
-    if (selected.isEmpty()) return;
-
-    QString profileName = ui->profileTable->item(selected.first()->row(), 0)->text();
-    // Use cached m_profiles for in-dialog state
-    loadGitSettingsForProfile(profileName, m_profiles);
-}
-```
-
-Cache profiles in `m_profiles` member variable and update on `getProfiles()`.
-
-### Avoid Setter Side Effects in Loops
-
-When loading settings, avoid calling setters that trigger side effects inside loops:
-
-```cpp
-// Bad - triggers update logic for each profile
-for (const auto &profile : profiles) {
-    setUseGit(profile.useGit);  // Side effects!
-}
-
-// Good - direct access to selected profile, apply side effects once
-int selectedProfileIndex = getSelectedProfileIndex();
-if (selectedProfileIndex >= 0 && selectedProfileIndex < profiles.size()) {
-    ui->checkBoxUseGit->setChecked(profiles[selectedProfileIndex].useGit);
-    useGit(profiles[selectedProfileIndex].useGit);
-}
-
-// Or, if you need to collect profiles first:
-QVector<ProfileConfig> collectedProfiles;
-for (const auto &profile : profiles) {
-    collectedProfiles.append(profile);  // Collect into m_profiles or local container
-}
-int selectedProfileIndex = getSelectedProfileIndex();
-if (selectedProfileIndex >= 0 && selectedProfileIndex < collectedProfiles.size()) {
-    ui->checkBoxUseGit->setChecked(collectedProfiles[selectedProfileIndex].useGit);
-    useGit(collectedProfiles[selectedProfileIndex].useGit);
-}
-```
-
 ## Handling AI Findings
 
 When CodeRabbit/CodeAnt AI flags issues in PRs:
PATCH

echo "Gold patch applied."
