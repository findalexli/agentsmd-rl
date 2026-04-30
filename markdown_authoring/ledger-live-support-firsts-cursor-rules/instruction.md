# support: firsts cursor rules 📋

Source: [LedgerHQ/ledger-live#13246](https://github.com/LedgerHQ/ledger-live/pull/13246)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/git-workflow.mdc`
- `.cursor/rules/ldls.mdc`
- `.cursor/rules/react-general.mdc`
- `.cursor/rules/react-new-arch.mdc`
- `.cursor/rules/testing.mdc`
- `.cursor/rules/typescript.mdc`
- `.cursorrules`

## What to add / change

<!--
Thank you for your contribution! 👍
Please make sure to read CONTRIBUTING.md if you have not already. Pull Requests that do not comply with the rules will be arbitrarily closed.
-->

### ✅ Checklist

<!-- Pull Requests must pass the CI and be code reviewed. Set as Draft if the PR is not ready. -->

- [ ] `npx changeset` was attached.
- [ ] **Covered by automatic tests.** <!-- if not, please explain. (Feature must be tested / Bug fix must bring non-regression) -->
- [ ] **Impact of the changes:** <!-- Please take some time to list the impact & what specific areas Quality Assurance (QA) should focus on -->
  - ...

### 📝 Description

Introduce first batch of cursor rules

To test it I tried this prompt in french , on `develop` (without rules)  and on the current branch :

```sh
Ajoute la fonctionnalité MultiSign composée de 3 écrans :

Step 1 : afficher une liste de comptes et permettre d’en sélectionner un seul. Impossible d’avancer tant qu’aucun compte n’est choisi.
Step 2 : permettre de choisir le nombre de signers via un slider.
Step 3 : afficher un récapitulatif (compte sélectionné + nombre de signers) et un bouton centré qui déclenche un appel API vers https://my-signers-ledger pour enregistrer la configuration.
```

### Result

<img width="1991" height="528" alt="Screenshot 2025-12-11 at 15 43 32" src="https://github.com/user-attachments/assets/72b6f44e-6d59-4d8e-8420-65688f091b5f" />


_**Architecture**_ 
<img width="319" height="48

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
