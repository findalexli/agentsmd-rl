# Agent Config Files for areal-lora-xccl-versioning

Repo: inclusionAI/AReaL
Commit: 1927decc369d30df0037854b5d58ec7a9ca2a3b7
Files found: 26


---
## .claude/commands/create-pr.md

```
   1 | ---
   2 | name: create-pr
   3 | description: Rebase from the latest `origin/main`, squash the commits from it, and then create a PR on github with intelligent commit messages based on staged changes. Invoke with /create-pr.
   4 | ---
   5 | 
   6 | # Create Pull Request
   7 | 
   8 | Rebase from the latest `origin/main`, squash commits, and create a PR on GitHub with an
   9 | intelligent title and description.
  10 | 
  11 | ## Usage
  12 | 
  13 | ```
  14 | /create-pr [--draft] [--base <branch>]
  15 | ```
  16 | 
  17 | **Arguments:**
  18 | 
  19 | - `--draft`: Create as draft PR
  20 | - `--base <branch>`: Target branch (default: `main`)
  21 | 
  22 | ## Workflow
  23 | 
  24 | ### Step 1: Verify Prerequisites
  25 | 
  26 | ```bash
  27 | # Check current branch
  28 | git branch --show-current
  29 | 
  30 | # Check if on main/master (should NOT be)
  31 | if [[ $(git branch --show-current) == "main" || $(git branch --show-current) == "master" ]]; then
  32 |   echo "ERROR: Cannot create PR from main/master branch"
  33 |   exit 1
  34 | fi
  35 | 
  36 | # Check for uncommitted changes
  37 | git status --short
  38 | 
  39 | # Ensure gh CLI is available
  40 | gh --version
  41 | ```
  42 | 
  43 | **Action:** If there are uncommitted changes, stop, and then ask user to commit or stash
  44 | them first.
  45 | 
  46 | ### Step 2: Check for Existing PR
  47 | 
  48 | ```bash
  49 | # Check if PR already exists for current branch
  50 | gh pr view --json number,title,url 2>/dev/null || echo "No existing PR"
  51 | ```
  52 | 
  53 | **Handle Existing PR:**
  54 | 
  55 | - If PR exists, inform user and ask permission to force-update it
  56 | - Warn that this will rewrite the commit history and PR description
  57 | - If user declines, abort the process
  58 | 
  59 | ### Step 3: Fetch and Rebase
  60 | 
  61 | ```bash
  62 | # Fetch latest from origin
  63 | git fetch origin main
  64 | 
  65 | # Check divergence
  66 | git log --oneline HEAD ^origin/main
  67 | 
  68 | # Non-interactive rebase onto origin/main
  69 | git rebase origin/main
  70 | ```
  71 | 
  72 | **Handle Conflicts:** If rebase fails due to conflicts, abort and let user handle rebase
  73 | manually:
  74 | 
  75 | ```bash
  76 | # On rebase failure, abort automatically
  77 | git rebase --abort
  78 | 
  79 | # Inform user to resolve conflicts manually
  80 | echo "Rebase failed due to conflicts. Please resolve manually and retry /create-pr"
  81 | exit 1
  82 | ```
  83 | 
  84 | ### Step 4: Squash Commits into Single Commit
  85 | 
  86 | After successful rebase, squash all commits since `origin/main` into a single commit:
  87 | 
  88 | ```bash
  89 | # Count commits to squash
  90 | git rev-list --count origin/main..HEAD
  91 | 
  92 | # Soft reset to origin/main (keeps changes staged)
  93 | git reset --soft origin/main
  94 | 
  95 | # Generate commit message using /gen-commit-msg logic
  96 | # See .claude/commands/gen-commit-msg.md for message generation rules
  97 | ```
  98 | 
  99 | **Generate Commit Message** (following `/gen-commit-msg` format):
 100 | 
 101 | 1. Analyze staged changes:
 102 | 
 103 |    ```bash
 104 |    git diff --cached --name-only
 105 |    git diff --cached
 106 |    ```
 107 | 
 108 | 1. Categorize changes (feat/fix/docs/refactor/test/chore/perf)
 109 | 
 110 | 1. Determine scope from changed files (workflow/engine/reward/dataset/api/docs/etc.)
 111 | 
 112 | 1. Generate message in format:
 113 | 
 114 |    ```
 115 |    <type>(<scope>): <subject>
 116 | 
 117 |    <body>
 118 | 
 119 |    [Optional sections:]
 120 |    Key changes:
 121 |    - change 1
 122 |    - change 2
 123 | 
 124 |    Refs: #123, #456
 125 |    ```
 126 | 
 127 | 1. Commit with generated message:
 128 | 
 129 |    ```bash
 130 |    git commit -m "$(cat <<'EOF'
 131 |    <generated commit message>
 132 |    EOF
 133 |    )"
 134 |    ```
 135 | 
 136 | ### Step 5: Analyze Combined Changes
 137 | 
 138 | After squashing into a single commit:
 139 | 
 140 | ```bash
 141 | # Get all changes since origin/main
 142 | git diff origin/main...HEAD --name-only
 143 | 
 144 | # Get full diff content
 145 | git diff origin/main...HEAD
 146 | 
 147 | # Check commit history
 148 | git log --oneline origin/main..HEAD
 149 | ```
 150 | 
 151 | **Categorize Changes:**
 152 | 
 153 | Follow same categorization as `/gen-commit-msg`:
 154 | 
 155 | | Type       | When to Use                     |
 156 | | ---------- | ------------------------------- |
 157 | | `feat`     | New feature or capability       |
 158 | | `fix`      | Bug fix                         |
 159 | | `docs`     | Documentation only              |
 160 | | `refactor` | Code change without feature/fix |
 161 | | `test`     | Adding or fixing tests          |
 162 | | `chore`    | Build, deps, config changes     |
 163 | | `perf`     | Performance improvement         |
 164 | 
 165 | **Determine Scope:**
 166 | 
 167 | Infer from changed files:
 168 | 
 169 | - `areal/workflow/` → `workflow`
 170 | - `areal/engine/` → `engine`
 171 | - `areal/reward/` → `reward`
 172 | - `areal/dataset/` → `dataset`
 173 | - `areal/api/` → `api`
 174 | - `areal/utils/` → `utils`
 175 | - `areal/infra/` → `infra`
 176 | - `docs/` → `docs`
 177 | - `examples/` → `examples`
 178 | - Multiple areas → omit scope or use broader term
 179 | 
 180 | ### Step 6: Generate PR Title and Description
 181 | 
 182 | **PR Title Format:**
 183 | 
 184 | ```
 185 | <type>(<scope>): <brief description>
 186 | ```
 187 | 
 188 | **Rules:**
 189 | 
 190 | - Keep under 70 characters
 191 | - Use imperative mood
 192 | - No period at end
 193 | - Mirror commit message style
 194 | 
 195 | **PR Description Format:**
 196 | 
 197 | MUST strictly follow the [GitHub PR template](../../.github/PULL_REQUEST_TEMPLATE.md):
 198 | 
 199 | ```markdown
 200 | ## Description
 201 | 
 202 | <!-- Clear and concise description of what this PR does -->
 203 | 
 204 | ## Related Issue
 205 | 
 206 | <!-- Link to the issue this PR addresses -->
 207 | Fixes #(issue)
 208 | 
 209 | ## Type of Change
 210 | 
 211 | <!-- Mark the relevant option with an 'x' -->
 212 | 
 213 | - [ ] Bug fix (non-breaking change that fixes an issue)
 214 | - [ ] New feature (non-breaking change that adds functionality)
 215 | - [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
 216 | - [ ] Documentation update
 217 | - [ ] Code refactoring (no functional changes)
 218 | - [ ] Performance improvement
 219 | - [ ] Test coverage improvement
 220 | 
 221 | ## Checklist
 222 | 
 223 | <!-- Mark with 'x' what you've done -->
 224 | 
 225 | - [ ] I have read the [Contributing Guide](../CONTRIBUTING.md)
 226 | - [ ] I have run formatting tools (pre-commit or manual)
 227 | - [ ] I have run relevant unit tests and they pass
 228 | - [ ] I have added tests for new functionality
 229 | - [ ] I have updated documentation if needed
 230 | - [ ] My branch is up to date with main
 231 | - [ ] This PR introduces breaking changes (if yes, fill out details below)
 232 | - [ ] If this PR changes documentation, I have built and previewed it locally with `jb build docs`
 233 | - [ ] No critical issues raised by AI reviewers (`/gemini review`)
 234 | 
 235 | **Breaking Change Details (if applicable):**
 236 | 
 237 | <!-- Describe what breaks and how users should migrate -->
 238 | 
 239 | ## Additional Context
 240 | 
 241 | <!-- Add any other context, screenshots, logs, or explanations here -->
 242 | ```
 243 | 
 244 | **How to Fill the Template:**
 245 | 
 246 | 1. **Description**: 2-4 sentences explaining what this PR does and why
 247 | 1. **Related Issue**: Link to issue (search for related issues if exists)
 248 | 1. **Type of Change**: Mark ONE primary type with `[x]`
 249 | 1. **Checklist**: Mark completed items with `[x]`, leave uncompleted as `[ ]`
 250 | 1. **Breaking Change Details**: Only if breaking changes checkbox is marked
 251 | 1. **Additional Context**: Any extra info, related PRs, performance numbers, etc.
 252 | 
 253 | ### Step 7: Push and Create/Update PR
 254 | 
 255 | Show preview to user:
 256 | 
 257 | ```
 258 | ─────────────────────────────────────────────────
 259 | Branch: feat/vision-rlvr → main
 260 | 
 261 | PR Title:
 262 | feat(workflow): add vision support to RLVR
 263 | 
 264 | PR Description:
 265 | ## Description
 266 | 
 267 | Add VisionRLVRWorkflow for vision-language RL training. Supports image inputs
 268 | alongside text prompts and integrates with existing RLVR pipeline.
 269 | 
 270 | ## Related Issue
 271 | 
 272 | Fixes #789
 273 | 
 274 | ## Type of Change
 275 | 
 276 | - [ ] Bug fix (non-breaking change that fixes an issue)
 277 | - [x] New feature (non-breaking change that adds functionality)
 278 | - [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
 279 | - [ ] Documentation update
 280 | - [ ] Code refactoring (no functional changes)
 281 | - [ ] Performance improvement
 282 | - [ ] Test coverage improvement
 283 | 
 284 | ## Checklist
 285 | 
 286 | - [x] I have read the [Contributing Guide](../CONTRIBUTING.md)
 287 | - [x] I have run formatting tools (pre-commit or manual)
 288 | - [ ] I have run relevant unit tests and they pass
 289 | - [x] I have added tests for new functionality
 290 | - [x] I have updated documentation if needed
 291 | - [x] My branch is up to date with main
 292 | - [ ] This PR introduces breaking changes (if yes, fill out details below)
 293 | - [x] If this PR changes documentation, I have built and previewed it locally with `jb build docs`
 294 | - [ ] No critical issues raised by AI reviewers (`/gemini review`)
 295 | 
 296 | **Breaking Change Details (if applicable):**
 297 | 
 298 | N/A
 299 | 
 300 | ## Additional Context
 301 | 
 302 | Requires Pillow>=10.0.0 for image processing.
 303 | 
 304 | Files changed:
 305 | - `areal/workflow/vision_rlvr.py`: New VisionRLVRWorkflow class
 306 | - `areal/api/workflow_api.py:45`: Add vision config fields
 307 | - `examples/vision_rlvr.py`: Example training script
 308 | - `docs/workflows/vision.md`: Documentation
 309 | 
 310 | ─────────────────────────────────────────────────
 311 | 
 312 | Commands to execute:
 313 | 1. git push -u origin feat/vision-rlvr
 314 | 2. gh pr create --title "..." --body "..." [--draft]
 315 | ─────────────────────────────────────────────────
 316 | ```
 317 | 
 318 | **Confirm with user**, then execute:
 319 | 
 320 | ```bash
 321 | # Force push branch to remote (required after squash)
 322 | git push -f -u origin $(git branch --show-current)
 323 | 
 324 | # Create or edit PR using gh CLI with GitHub template format
 325 | # If PR exists, use 'gh pr edit' instead of 'gh pr create'
 326 | if gh pr view &>/dev/null; then
 327 |   # Update existing PR
 328 |   gh pr edit \
 329 |     --title "feat(workflow): add vision support to RLVR" \
 330 |     --body "$(cat <<'EOF'
 331 | [PR description here]
 332 | EOF
 333 | )"
 334 | else
 335 |   # Create new PR
 336 |   gh pr create \
 337 |     --base main \
 338 |     --title "feat(workflow): add vision support to RLVR" \
 339 |     --body "$(cat <<'EOF'
 340 | ## Description
 341 | 
 342 | Add VisionRLVRWorkflow for vision-language RL training. Supports image inputs
 343 | alongside text prompts and integrates with existing RLVR pipeline.
 344 | 
 345 | ## Related Issue
 346 | 
 347 | Fixes #789
 348 | 
 349 | ## Type of Change
 350 | 
 351 | - [ ] Bug fix (non-breaking change that fixes an issue)
 352 | - [x] New feature (non-breaking change that adds functionality)
 353 | - [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
 354 | - [ ] Documentation update
 355 | - [ ] Code refactoring (no functional changes)
 356 | - [ ] Performance improvement
 357 | - [ ] Test coverage improvement
 358 | 
 359 | ## Checklist
 360 | 
 361 | - [x] I have read the [Contributing Guide](../CONTRIBUTING.md)
 362 | - [x] I have run formatting tools (pre-commit or manual)
 363 | - [ ] I have run relevant unit tests and they pass
 364 | - [x] I have added tests for new functionality
 365 | - [x] I have updated documentation if needed
 366 | - [x] My branch is up to date with main
 367 | - [ ] This PR introduces breaking changes (if yes, fill out details below)
 368 | - [x] If this PR changes documentation, I have built and previewed it locally with `jb build docs`
 369 | - [ ] No critical issues raised by AI reviewers (`/gemini review`)
 370 | 
 371 | **Breaking Change Details (if applicable):**
 372 | 
 373 | N/A
 374 | 
 375 | ## Additional Context
 376 | 
 377 | Requires Pillow>=10.0.0 for image processing.
 378 | 
 379 | Files changed:
 380 | - `areal/workflow/vision_rlvr.py`: New VisionRLVRWorkflow class
 381 | - `areal/api/workflow_api.py:45`: Add vision config fields
 382 | - `examples/vision_rlvr.py`: Example training script
 383 | - `docs/workflows/vision.md`: Documentation
 384 | EOF
 385 | )"
 386 | fi
 387 | ```
 388 | 
 389 | Add `--draft` flag if requested.
 390 | 
 391 | **Capture PR URL** and display to user:
 392 | 
 393 | ```
 394 | ✓ PR created/updated successfully!
 395 | https://github.com/inclusionAI/AReaL/pull/123
 396 | ```
 397 | 
 398 | ## Examples
 399 | 
 400 | ### Example 1: Feature PR
 401 | 
 402 | **Changes:** New dataset loader for MATH dataset
 403 | 
 404 | **PR Title:**
 405 | 
 406 | ```
 407 | feat(dataset): add MATH dataset loader
 408 | ```
 409 | 
 410 | **PR Description:**
 411 | 
 412 | ```markdown
 413 | ## Description
 414 | 
 415 | Add MATHDataset loader for mathematics problem solving with LaTeX rendering and
 416 | symbolic math parsing. Includes reward function for automatic answer verification
 417 | and full test coverage.
 418 | 
 419 | ## Related Issue
 420 | 
 421 | Fixes #456
 422 | 
 423 | ## Type of Change
 424 | 
 425 | - [ ] Bug fix (non-breaking change that fixes an issue)
 426 | - [x] New feature (non-breaking change that adds functionality)
 427 | - [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
 428 | - [ ] Documentation update
 429 | - [ ] Code refactoring (no functional changes)
 430 | - [ ] Performance improvement
 431 | - [ ] Test coverage improvement
 432 | 
 433 | ## Checklist
 434 | 
 435 | - [x] I have read the [Contributing Guide](../CONTRIBUTING.md)
 436 | - [x] I have run formatting tools (pre-commit or manual)
 437 | - [x] I have run relevant unit tests and they pass
 438 | - [x] I have added tests for new functionality
 439 | - [x] I have updated documentation if needed
 440 | - [x] My branch is up to date with main
 441 | - [ ] This PR introduces breaking changes (if yes, fill out details below)
 442 | - [x] If this PR changes documentation, I have built and previewed it locally with `jb build docs`
 443 | - [ ] No critical issues raised by AI reviewers (`/gemini review`)
 444 | 
 445 | **Breaking Change Details (if applicable):**
 446 | 
 447 | N/A
 448 | 
 449 | ## Additional Context
 450 | 
 451 | Dataset requires ~500MB download on first use. Added comprehensive test suite
 452 | covering all 12,500 problems with >95% reward function accuracy.
 453 | 
 454 | Files changed:
 455 | - `areal/dataset/math.py`: New MATHDataset class
 456 | - `areal/reward/math_reward.py`: Symbolic math reward function
 457 | - `examples/math_training.py`: Training script
 458 | - `docs/datasets/math.md`: Dataset documentation
 459 | - `tests/test_math_dataset.py`: Unit tests
 460 | ```
 461 | 
 462 | ### Example 2: Bug Fix PR
 463 | 
 464 | **Changes:** Fix memory leak in ArchonEngine
 465 | 
 466 | **PR Title:**
 467 | 
 468 | ```
 469 | fix(engine): resolve memory leak in ArchonEngine rollout
 470 | ```
 471 | 
 472 | **PR Description:**
 473 | 
 474 | ```markdown
 475 | ## Description
 476 | 
 477 | Fix memory leak during ArchonEngine rollout phase by clearing cached activations
 478 | after each batch and moving tensors to CPU before deletion. Reduces memory usage
 479 | by ~2GB per rollout iteration.
 480 | 
 481 | ## Related Issue
 482 | 
 483 | Fixes #872
 484 | 
 485 | ## Type of Change
 486 | 
 487 | - [x] Bug fix (non-breaking change that fixes an issue)
 488 | - [ ] New feature (non-breaking change that adds functionality)
 489 | - [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
 490 | - [ ] Documentation update
 491 | - [ ] Code refactoring (no functional changes)
 492 | - [ ] Performance improvement
 493 | - [ ] Test coverage improvement
 494 | 
 495 | ## Checklist
 496 | 
 497 | - [x] I have read the [Contributing Guide](../CONTRIBUTING.md)
 498 | - [x] I have run formatting tools (pre-commit or manual)
 499 | - [x] I have run relevant unit tests and they pass
 500 | - [x] I have added tests for new functionality
 501 | - [ ] I have updated documentation if needed
 502 | - [x] My branch is up to date with main
 503 | - [ ] This PR introduces breaking changes (if yes, fill out details below)
 504 | - [ ] If this PR changes documentation, I have built and previewed it locally with `jb build docs`
 505 | - [ ] No critical issues raised by AI reviewers (`/gemini review`)
 506 | 
 507 | **Breaking Change Details (if applicable):**
 508 | 
 509 | N/A
 510 | 
 511 | ## Additional Context
 512 | 
 513 | Tested with 100 rollout iterations without OOM. Memory usage stable at 8GB
 514 | (previously would grow to 10GB+). Output correctness validated unchanged.
 515 | 
 516 | Backported to v0.5.x branch.
 517 | 
 518 | Files changed:
 519 | - `areal/engine/archon.py:234`: Add explicit cache clearing
 520 | - `areal/engine/archon.py:456`: Move tensor to CPU before deletion
 521 | - `tests/test_archon_memory.py`: Add memory leak regression test
 522 | ```
 523 | 
 524 | ### Example 3: Breaking Change PR
 525 | 
 526 | **Changes:** Refactor reward API for better extensibility
 527 | 
 528 | **PR Title:**
 529 | 
 530 | ```
 531 | refactor(reward): simplify reward function interface
 532 | ```
 533 | 
 534 | **PR Description:**
 535 | 
 536 | ```markdown
 537 | ## Description
 538 | 
 539 | Simplify reward function API from 4 methods to 2 by consolidating compute and
 540 | compute_batch into a single batched interface. Improves type hints and
 541 | documentation. All existing reward functions updated.
 542 | 
 543 | ## Related Issue
 544 | 
 545 | Fixes #901
 546 | 
 547 | ## Type of Change
 548 | 
 549 | - [ ] Bug fix (non-breaking change that fixes an issue)
 550 | - [ ] New feature (non-breaking change that adds functionality)
 551 | - [x] Breaking change (fix or feature that would cause existing functionality to not work as expected)
 552 | - [ ] Documentation update
 553 | - [ ] Code refactoring (no functional changes)
 554 | - [ ] Performance improvement
 555 | - [ ] Test coverage improvement
 556 | 
 557 | ## Checklist
 558 | 
 559 | - [x] I have read the [Contributing Guide](../CONTRIBUTING.md)
 560 | - [x] I have run formatting tools (pre-commit or manual)
 561 | - [x] I have run relevant unit tests and they pass
 562 | - [ ] I have added tests for new functionality
 563 | - [x] I have updated documentation if needed
 564 | - [x] My branch is up to date with main
 565 | - [x] This PR introduces breaking changes (if yes, fill out details below)
 566 | - [x] If this PR changes documentation, I have built and previewed it locally with `jb build docs`
 567 | - [ ] No critical issues raised by AI reviewers (`/gemini review`)
 568 | 
 569 | **Breaking Change Details (if applicable):**
 570 | 
 571 | Old `compute_batch` method is deprecated and will be removed in v0.7.0.
 572 | 
 573 | See migration guide in `docs/migration/reward_api.md` for details.
 574 | 
 575 | ## Additional Context
 576 | 
 577 | All existing tests pass. Performance unchanged at 10k rewards/sec. Backward
 578 | compatibility warnings added for deprecated methods.
 579 | 
 580 | Files changed:
 581 | - `areal/api/reward_api.py:12`: Consolidate compute/compute_batch
 582 | - `areal/reward/gsm8k.py`: Update to new API
 583 | - `areal/reward/code_reward.py`: Update to new API
 584 | - `areal/reward/geometry3k.py`: Update to new API
 585 | - `docs/customization/reward.md`: Update documentation
 586 | - `docs/migration/reward_api.md`: Migration guide
 587 | - `examples/custom_reward.py`: Update example
 588 | ```
 589 | 
 590 | ## Error Handling
 591 | 
 592 | ### Rebase Conflicts
 593 | 
 594 | If rebase fails:
 595 | 
 596 | 1. Show conflict files
 597 | 1. Provide resolution instructions
 598 | 1. Wait for user to resolve
 599 | 1. After resolution, continue with squashing step
 600 | 1. Offer to abort rebase if needed: `git rebase --abort`
 601 | 
 602 | ### Squash Failures
 603 | 
 604 | If squash/commit fails:
 605 | 
 606 | 1. Check if there are changes to commit: `git status`
 607 | 1. Verify no conflicts remain: `git diff --cached`
 608 | 1. If needed, abort and return to pre-rebase state
 609 | 
 610 | ### Push Failures
 611 | 
 612 | If force push fails:
 613 | 
 614 | 1. Verify remote branch exists
 615 | 1. Check GitHub authentication: `gh auth status`
 616 | 1. Confirm branch protection rules allow force push
 617 | 1. Provide manual push instructions if needed
 618 | 
 619 | ### PR Creation/Update Failures
 620 | 
 621 | If `gh pr create` or `gh pr edit` fails:
 622 | 
 623 | 1. Check if PR already exists: `gh pr view`
 624 | 1. Verify GitHub authentication: `gh auth status`
 625 | 1. Check for branch protection rules
 626 | 1. Provide manual PR creation/update link
 627 | 
 628 | ## Safety Checks
 629 | 
 630 | **Before Starting:**
 631 | 
 632 | - Confirm no uncommitted changes
 633 | - Confirm not on main/master branch
 634 | - Check for existing PR and get user permission to overwrite if exists
 635 | - Backup branch: `git branch backup/$(git branch --show-current)-$(date +%s)`
 636 | 
 637 | **Before Rebase:**
 638 | 
 639 | - Fetch latest from origin
 640 | - Show divergence summary
 641 | 
 642 | **Before Squash:**
 643 | 
 644 | - Show commits that will be squashed
 645 | - Confirm user wants to proceed
 646 | 
 647 | **Before Force Push:**
 648 | 
 649 | - **CRITICAL**: Warn user that force push will rewrite history
 650 | - Show current commit that will replace remote history
 651 | - Confirm branch name
 652 | - If PR exists, emphasize that PR history will be rewritten
 653 | 
 654 | **Before PR Creation/Update:**
 655 | 
 656 | - Show full preview of title/description
 657 | - Confirm target branch
 658 | - If updating existing PR, show what will change
 659 | 
 660 | ______________________________________________________________________
 661 | 
 662 | <!--
 663 | ================================================================================
 664 |                             MAINTAINER GUIDE
 665 | ================================================================================
 666 | 
 667 | Location: .claude/commands/create-pr.md
 668 | Invocation: /create-pr
 669 | 
 670 | ## Design Philosophy
 671 | 
 672 | - Automates full PR creation workflow: fetch, rebase, **squash to single commit**, push, create/update PR
 673 | - **Always squashes all commits** since `origin/main` into a single commit with message generated via `/gen-commit-msg` logic
 674 | - **Handles existing PRs** by detecting them and force-updating after user permission
 675 | - Follows repository's Conventional Commits format
 676 | - Requires user confirmation at critical steps (existing PR detection, rebase, squash, force-push, PR creation/update)
 677 | - Generates intelligent commit messages, PR titles, and descriptions based on change analysis
 678 | - Uses force push (`-f`) by design, as squashing requires rewriting history
 679 | 
 680 | ## How to Update
 681 | 
 682 | ### Adding New Scopes
 683 | Update "Determine Scope" section with new file path mappings.
 684 | 
 685 | ### Changing PR Template
 686 | Update "PR Description Format" section with new template structure.
 687 | 
 688 | ### Modifying Workflow Steps
 689 | Update relevant "Step N" sections with new git commands or logic.
 690 | 
 691 | ================================================================================
 692 | -->
```


---
## .claude/commands/gen-commit-msg.md

```
   1 | ---
   2 | name: gen-commit-msg
   3 | description: Generate intelligent commit messages based on staged changes. Invoke with /gen-commit-msg.
   4 | ---
   5 | 
   6 | # Generate Commit Message
   7 | 
   8 | Generate a well-formatted commit message based on staged changes.
   9 | 
  10 | ## Usage
  11 | 
  12 | ```
  13 | /gen-commit-msg [--amend] [--scope <scope>]
  14 | ```
  15 | 
  16 | **Arguments:**
  17 | 
  18 | - `--amend`: Amend the previous commit instead of creating new
  19 | - `--scope <scope>`: Force a specific scope (e.g., `workflow`, `engine`)
  20 | 
  21 | ## Workflow
  22 | 
  23 | ### Step 1: Analyze Changes
  24 | 
  25 | ```bash
  26 | # Check staged files
  27 | git diff --cached --name-only
  28 | 
  29 | # Check staged content
  30 | git diff --cached
  31 | 
  32 | # Check recent commit style
  33 | git log --oneline -5
  34 | ```
  35 | 
  36 | ### Step 2: Categorize Changes
  37 | 
  38 | | Type       | When to Use                     |
  39 | | ---------- | ------------------------------- |
  40 | | `feat`     | New feature or capability       |
  41 | | `fix`      | Bug fix                         |
  42 | | `docs`     | Documentation only              |
  43 | | `refactor` | Code change without feature/fix |
  44 | | `test`     | Adding or fixing tests          |
  45 | | `chore`    | Build, deps, config changes     |
  46 | | `perf`     | Performance improvement         |
  47 | 
  48 | ### Step 3: Determine Scope
  49 | 
  50 | Infer scope from changed files:
  51 | 
  52 | - `areal/workflow/` → `workflow`
  53 | - `areal/engine/` → `engine`
  54 | - `areal/reward/` → `reward`
  55 | - `areal/dataset/` → `dataset`
  56 | - `areal/api/` → `api`
  57 | - `docs/` → `docs`
  58 | - Multiple areas → omit scope or use broader term
  59 | 
  60 | ### Step 4: Generate Message
  61 | 
  62 | **Format:**
  63 | 
  64 | ```
  65 | <type>(<scope>): <subject>
  66 | 
  67 | <body>
  68 | 
  69 | [Optional sections:]
  70 | Key changes:
  71 | - change 1
  72 | - change 2
  73 | 
  74 | Refs: #123, #456
  75 | ```
  76 | 
  77 | **Rules:**
  78 | 
  79 | - Subject: imperative mood, ~50-72 chars, no period
  80 | - Body: explain "why" not "what", wrap at 72 chars
  81 | - Key changes: bullet list of main modifications (for complex commits)
  82 | - Refs: reference issues/PRs if applicable
  83 | 
  84 | ### Step 5: Confirm and Commit
  85 | 
  86 | Show preview:
  87 | 
  88 | ```
  89 | ─────────────────────────────────────
  90 | feat(workflow): add vision support to RLVR
  91 | 
  92 | Add VisionRLVRWorkflow for vision-language RL training.
  93 | Supports image inputs alongside text prompts.
  94 | ─────────────────────────────────────
  95 | ```
  96 | 
  97 | Ask user to confirm, then execute:
  98 | 
  99 | ```bash
 100 | git commit -m "$(cat <<'EOF'
 101 | <message>
 102 | EOF
 103 | )"
 104 | ```
 105 | 
 106 | ## Examples
 107 | 
 108 | **Single file fix:**
 109 | 
 110 | ```
 111 | fix(reward): handle empty completion in gsm8k
 112 | 
 113 | Return 0 reward instead of raising exception when
 114 | completion string is empty after extraction.
 115 | ```
 116 | 
 117 | **Multi-file feature:**
 118 | 
 119 | ```
 120 | feat(engine): add CPU offload support to ArchonEngine
 121 | 
 122 | Enable torch_memory_saver for model offloading during
 123 | rollout phase to reduce GPU memory pressure.
 124 | 
 125 | Key changes:
 126 | - Add offload/onload methods to ArchonEngine
 127 | - Integrate with weight update flow
 128 | - Handle ROCm compatibility
 129 | ```
 130 | 
 131 | **Docs only:**
 132 | 
 133 | ```
 134 | docs: update algorithm comparison table
 135 | 
 136 | Add SAPO and GSPO to the algorithm family documentation
 137 | with configuration examples.
 138 | ```
 139 | 
 140 | ______________________________________________________________________
 141 | 
 142 | <!--
 143 | ================================================================================
 144 |                             MAINTAINER GUIDE
 145 | ================================================================================
 146 | 
 147 | Location: .claude/commands/gen-commit-msg.md
 148 | Invocation: /gen-commit-msg
 149 | 
 150 | ## Design Philosophy
 151 | 
 152 | - Automates commit message generation following Conventional Commits format
 153 | - Matches repository's existing style
 154 | - Requires user confirmation before commit
 155 | 
 156 | ## How to Update
 157 | 
 158 | ### Adding New Scopes
 159 | Update "Determine Scope" section with new file path mappings.
 160 | 
 161 | ### Changing Format
 162 | Update "Generate Message" format template and rules.
 163 | 
 164 | ================================================================================
 165 | -->
```


---
## .claude/commands/review-pr.md

```
   1 | ---
   2 | name: review-pr
   3 | description: Intelligent PR code review with dynamic agent allocation based on change types
   4 | allowed-tools: Read, Grep, Glob, Bash, Task
   5 | ---
   6 | 
   7 | <!-- Reference data (auto-loaded via @import) -->
   8 | 
   9 | @.claude/data/review-pr-change-types.md @.claude/data/review-pr-templates.md
  10 | 
  11 | # PR Code Review (Dynamic Agent Allocation)
  12 | 
  13 | Intelligent code review for the current branch's Pull Request. Dynamically generates
  14 | targeted review tasks based on PR changes.
  15 | 
  16 | ## Arguments
  17 | 
  18 | `$ARGUMENTS`
  19 | 
  20 | - No arguments: Review PR for current branch
  21 | - PR number: Review specific PR (e.g., `/review-pr 123`)
  22 | - `--quick`: Quick mode, only run Phase 1 analysis
  23 | 
  24 | ## Quick Start
  25 | 
  26 | 1. Get current branch PR: `gh pr view --json number,title,state,isDraft`
  27 | 1. If PR doesn't exist or is closed, stop and explain
  28 | 1. Execute Phases 1-4 in order
  29 | 
  30 | ## Workflow Overview
  31 | 
  32 | ```
  33 | Phase 1: Deep PR Analysis [Haiku + Sonnet]
  34 |     |- 1.0 PR Status Check [Haiku]
  35 |     |- 1.1 Get PR Summary [Haiku]
  36 |     +- 1.2-1.4 Change Type Detection [Sonnet]
  37 |     |
  38 | Phase 2: Dynamic Agent Planning [Sonnet]
  39 |     |
  40 | Phase 3: Execute Review Tasks [Parallel, Dynamic Model Selection]
  41 |     |
  42 | Phase 4: Confidence Scoring & Summary [Haiku]
  43 | ```
  44 | 
  45 | ## Model Configuration
  46 | 
  47 | | Mode                      | CRITICAL/HIGH | MEDIUM | LOW    |
  48 | | ------------------------- | ------------- | ------ | ------ |
  49 | | **Default**               | Opus          | Sonnet | Haiku  |
  50 | | **Quick** (`--quick`)     | Sonnet        | Sonnet | Sonnet |
  51 | | **Economy** (`--economy`) | Sonnet        | Haiku  | Haiku  |
  52 | 
  53 | ______________________________________________________________________
  54 | 
  55 | ## Phase 1: Deep PR Analysis
  56 | 
  57 | ### 1.0 PR Status Check \[Haiku\]
  58 | 
  59 | Check if PR should be reviewed:
  60 | 
  61 | - Is it closed? -> Stop
  62 | - Is it a draft? -> Note but continue
  63 | - Is it bot-generated? -> Skip
  64 | 
  65 | ### 1.1 Get PR Summary \[Haiku\]
  66 | 
  67 | Get basic PR info: title, description, modified files, change summary.
  68 | 
  69 | ### 1.2 Change Type Detection \[Sonnet\]
  70 | 
  71 | Analyze each file change, detecting change types by risk level.
  72 | 
  73 | **Reference**: See `review-pr-change-types.md` for complete detection tables:
  74 | 
  75 | - CRITICAL level types (Archon, FSDP, Megatron, DCP)
  76 | - HIGH level types (distributed comm, DTensor, MoE, TP/EP/CP)
  77 | - MEDIUM level types (tensor ops, workflow, API, compile)
  78 | - LOW level types (tests, docs, config)
  79 | 
  80 | ### 1.3 Framework-Specific Risk Identification
  81 | 
  82 | Based on detected types, identify corresponding risks.
  83 | 
  84 | **Reference**: See `review-pr-change-types.md` for risk lists per framework.
  85 | 
  86 | ### 1.4 Output Change Analysis Report
  87 | 
  88 | ```
  89 | CHANGE_ANALYSIS_REPORT:
  90 | - detected_types: [ARCHON_PARALLEL, EP_ETP, FSDP_CORE, ...]
  91 | - risk_level: CRITICAL | HIGH | MEDIUM | LOW
  92 | - affected_files: [file1.py, file2.py, ...]
  93 | - identified_risks: [risk1, risk2, ...]
  94 | - related_frameworks: [archon, fsdp, megatron, ...]
  95 | ```
  96 | 
  97 | ______________________________________________________________________
  98 | 
  99 | ## Phase 2: Dynamic Agent Planning \[Sonnet\]
 100 | 
 101 | ### 2.1 Planning Principles
 102 | 
 103 | 1. **Generate tasks by risk area**: Each high-risk area gets a dedicated task
 104 | 1. **Merge related changes**: Interdependent changes can be merged
 105 | 1. **Model selection**: CRITICAL/HIGH -> Opus, MEDIUM -> Sonnet, LOW -> Haiku
 106 | 1. **Minimum coverage**: Even simple changes get at least 1 basic review task
 107 | 
 108 | ### 2.2 Task Template Selection
 109 | 
 110 | Based on detected change types, select appropriate review task templates.
 111 | 
 112 | **Reference**: See `review-pr-templates.md` for complete task templates:
 113 | 
 114 | - Framework-specific tasks (Archon, FSDP, Megatron, DCP, Trainer)
 115 | - General tasks (Logic, Concurrency, Tensor, Numerical, TP, etc.)
 116 | 
 117 | ### 2.3 Output Review Task List
 118 | 
 119 | ```
 120 | GENERATED_REVIEW_TASKS:
 121 | 1. [Opus] Task Name
 122 |    - Reason: XXX change type detected
 123 |    - Checklist: [...]
 124 |    - Focus files: [...]
 125 | 
 126 | 2. [Sonnet] Task Name
 127 |    - Reason: ...
 128 |    ...
 129 | ```
 130 | 
 131 | ______________________________________________________________________
 132 | 
 133 | ## Phase 3: Execute Review Tasks \[Parallel\]
 134 | 
 135 | ### 3.1 Execution Rules
 136 | 
 137 | - Use Phase 2 specified model for each task
 138 | - Execute all agents **in parallel**
 139 | - Each agent reviews independently
 140 | 
 141 | ### 3.2 Agent Output Format
 142 | 
 143 | ```
 144 | REVIEW_RESULT:
 145 | task_name: "Task Name"
 146 | model: Opus | Sonnet | Haiku
 147 | findings:
 148 |   - issue: "Issue description"
 149 |     severity: CRITICAL | HIGH | MEDIUM | LOW
 150 |     file: "path/to/file.py"
 151 |     line: 123
 152 |     code_snippet: |
 153 |       Relevant code snippet
 154 |     reason: "Why this is an issue"
 155 |     suggestion: "Fix suggestion"
 156 | ```
 157 | 
 158 | ### 3.3 Review Depth by Model
 159 | 
 160 | | Model      | Requirements                                                               |
 161 | | ---------- | -------------------------------------------------------------------------- |
 162 | | **Opus**   | Complete context, cross-file traces, verify parallel strategy interactions |
 163 | | **Sonnet** | Changed code + direct callers/callees, type signature consistency          |
 164 | | **Haiku**  | Format and basic correctness only                                          |
 165 | 
 166 | ______________________________________________________________________
 167 | 
 168 | ## Phase 4: Confidence Scoring & Summary \[Haiku\]
 169 | 
 170 | ### 4.1 Confidence Scoring (0-100)
 171 | 
 172 | | Score   | Meaning                               |
 173 | | ------- | ------------------------------------- |
 174 | | **0**   | False positive or pre-existing issue  |
 175 | | **25**  | May be real, cannot verify            |
 176 | | **50**  | Real but minor or rare                |
 177 | | **75**  | Very likely real, important           |
 178 | | **100** | Confirmed real, will frequently occur |
 179 | 
 180 | ### 4.2 Summary Report Format
 181 | 
 182 | ```markdown
 183 | # PR Review Summary
 184 | 
 185 | ## PR Overview
 186 | - **Title**: PR title
 187 | - **Detected Change Types**: [...]
 188 | - **Risk Level**: CRITICAL | HIGH | MEDIUM | LOW
 189 | - **Generated Review Tasks**: N
 190 | 
 191 | ## Executed Review Tasks
 192 | | # | Model | Task Name | Reason |
 193 | |---|-------|-----------|--------|
 194 | 
 195 | ## Findings
 196 | 
 197 | ### CRITICAL Severity (Confidence >= 75)
 198 | #### Issue 1: [Title]
 199 | - **File**: `path/to/file.py:123`
 200 | - **Confidence**: 85
 201 | - **Description**: ...
 202 | - **Fix Suggestion**: ...
 203 | 
 204 | ### HIGH Severity (Confidence >= 50)
 205 | ...
 206 | 
 207 | ## Review Statistics
 208 | - Total issues: X (CRITICAL: X, HIGH: X, MEDIUM: X, LOW: X)
 209 | - Filtered false positives: X
 210 | ```
 211 | 
 212 | ### 4.3 Output Integrity (CRITICAL)
 213 | 
 214 | The Phase 4 summary report is the **FINAL DELIVERABLE** of this command.
 215 | 
 216 | - Output the COMPLETE report exactly as specified in Section 4.2 -- every section, every
 217 |   finding, every field.
 218 | - Do NOT abbreviate, summarize, or compress any part of the report.
 219 | - Do NOT omit findings, code snippets, fix suggestions, or statistics.
 220 | - If the report is long, that is expected and correct -- **completeness > brevity**.
 221 | - The orchestrating agent receiving this output MUST present it **VERBATIM** to the
 222 |   user. No re-summarization, no condensing, no "brief version".
 223 | 
 224 | ______________________________________________________________________
 225 | 
 226 | ## Dynamic Generation Examples
 227 | 
 228 | | PR Type        | Detected Types                        | Generated Tasks |
 229 | | -------------- | ------------------------------------- | --------------- |
 230 | | Docs only      | \[DOCS\]                              | 1 Haiku         |
 231 | | Config only    | \[CONFIG_ONLY\]                       | 1-2 Haiku       |
 232 | | Single bug fix | \[TENSOR_OPS\]                        | 2-4 Sonnet      |
 233 | | Archon core    | \[ARCHON\_\*, EP_ETP, DTENSOR\]       | 4-8 Opus        |
 234 | | Cross-domain   | \[WORKFLOW_ENGINE, FSDP_CORE, TESTS\] | 5-10 mixed      |
 235 | 
 236 | ______________________________________________________________________
 237 | 
 238 | ## False Positive Guide (Rate Confidence 0)
 239 | 
 240 | - Pre-existing issues (not introduced by this PR)
 241 | - Intentionally designed code that looks like a bug
 242 | - Issues linter/compiler would catch
 243 | - Issues on lines user didn't modify
 244 | - Explicitly disabled issues (lint ignore comments)
 245 | 
 246 | ______________________________________________________________________
 247 | 
 248 | ## Important Notes
 249 | 
 250 | - **Do NOT** check build signals or try to build/type-check
 251 | - Use `gh` to interact with GitHub, not web fetch
 252 | - **Do NOT** automatically post comments to PR
 253 | - Must provide file path and line number when referencing issues
 254 | 
 255 | ______________________________________________________________________
 256 | 
 257 | <!--
 258 | ================================================================================
 259 |                             MAINTAINER GUIDE
 260 | ================================================================================
 261 | 
 262 | Location: .claude/commands/review-pr.md
 263 | Invocation: /review-pr
 264 | Related files:
 265 |   - .claude/data/review-pr-change-types.md: Change type detection tables
 266 |   - .claude/data/review-pr-templates.md: Review task templates
 267 | 
 268 | ## Structure
 269 | 
 270 | - Main file (this): workflow and phases, @imports data files
 271 | - data/review-pr-change-types.md: detection tables
 272 | - data/review-pr-templates.md: task templates
 273 | 
 274 | ## How to Update
 275 | 
 276 | ### Adding New Change Types
 277 | Edit .claude/data/review-pr-change-types.md:
 278 | 1. Add to appropriate level table (CRITICAL/HIGH/MEDIUM/LOW)
 279 | 2. Add framework risks if applicable
 280 | 
 281 | ### Adding New Task Templates
 282 | Edit .claude/data/review-pr-templates.md:
 283 | 1. Add to framework-specific or general section
 284 | 2. Include checklist
 285 | 
 286 | ### Adjusting Model Selection
 287 | Modify "Model Configuration" table in this file.
 288 | 
 289 | ================================================================================
 290 | -->
```


---
## .claude/commands/translate-doc-zh.md

```
   1 | ---
   2 | name: translate-doc-zh
   3 | description: 'Translate English documentation to Chinese. Usage: /translate-doc-zh docs/en/path/to/file.md'
   4 | argument-hint: <path-to-en-doc>
   5 | ---
   6 | 
   7 | # Document Translation (EN → ZH)
   8 | 
   9 | Translate English documentation to Chinese for the AReaL project.
  10 | 
  11 | ## Usage
  12 | 
  13 | ```
  14 | /translate-doc-zh $ARGUMENTS
  15 | ```
  16 | 
  17 | **Arguments (`$ARGUMENTS`):**
  18 | 
  19 | - Path to English document (e.g., `docs/en/tutorial/quickstart.md`)
  20 | 
  21 | ## Document to Translate
  22 | 
  23 | !`if [ -f "$ARGUMENTS" ]; then echo "File: $ARGUMENTS"; echo ""; head -50 "$ARGUMENTS"; else echo "ERROR: File not found: $ARGUMENTS"; echo "Please provide a valid path to an English document in docs/en/"; fi`
  24 | 
  25 | ## Workflow
  26 | 
  27 | ### Step 1: Validate the Path
  28 | 
  29 | 1. Check if `$ARGUMENTS` exists
  30 | 1. Verify it is inside `docs/en/` directory and ends with `.md`
  31 | 1. If invalid, inform user and stop
  32 | 
  33 | ### Step 2: Determine Output Path
  34 | 
  35 | - Input: `$ARGUMENTS` (e.g., `docs/en/tutorial/quickstart.md`)
  36 | - Output: Replace `docs/en/` with `docs/zh/` (e.g., `docs/zh/tutorial/quickstart.md`)
  37 | 
  38 | ### Step 3: Check if Chinese Document Exists
  39 | 
  40 | - If `docs/zh/<path>` exists → **Modification Scenario**
  41 | - If `docs/zh/<path>` does NOT exist → **Full Translation Scenario**
  42 | 
  43 | ______________________________________________________________________
  44 | 
  45 | ## Scenario 1: Modification (Chinese Document Exists)
  46 | 
  47 | Use when Chinese document already exists.
  48 | 
  49 | ### Workflow
  50 | 
  51 | 1. Read both English and Chinese documents
  52 | 1. Compare differences to identify:
  53 |    - New sections in English
  54 |    - Modified sections in English
  55 |    - Deleted sections
  56 | 1. Translate only changed parts
  57 | 1. Preserve all other Chinese content unchanged
  58 | 
  59 | **Translation Rules:**
  60 | 
  61 | - Preserve English technical terms: FSDP, FSDP2, GRPO, PPO, DAPO, MoE, LLM, RL, RLVR,
  62 |   Claude Code, OpenCode, Megatron, Archon, SGLang, vLLM, PyTorch, HuggingFace,
  63 |   Transformers, etc.
  64 | - File paths and code examples remain unchanged
  65 | - Professional and rigorous terminology
  66 | - Preserve Markdown format, code blocks, tables
  67 | 
  68 | ______________________________________________________________________
  69 | 
  70 | ## Scenario 2: Full Translation (Chinese Document Does NOT Exist)
  71 | 
  72 | Use when Chinese document does not exist.
  73 | 
  74 | ### Workflow
  75 | 
  76 | 1. Read the English source document
  77 | 1. Translate entire document to Chinese
  78 | 
  79 | **Translation Rules:**
  80 | 
  81 | - Preserve English technical terms: FSDP, FSDP2, GRPO, PPO, DAPO, MoE, LLM, RL, RLVR,
  82 |   Claude Code, OpenCode, Megatron, Archon, SGLang, vLLM, PyTorch, HuggingFace,
  83 |   Transformers, etc.
  84 | - File paths and code examples remain unchanged
  85 | - Professional and rigorous terminology
  86 | - Preserve Markdown format, code blocks, tables
  87 | 
  88 | 3. Create new Chinese document at `docs/zh/<path>`
  89 | 
  90 | ______________________________________________________________________
  91 | 
  92 | ## Error Handling
  93 | 
  94 | ### Invalid Path
  95 | 
  96 | If user provides an invalid path:
  97 | 
  98 | 1. Tell user the file does not exist
  99 | 1. Ask user to provide a valid path starting with `docs/en/` and ending with `.md`
 100 | 
 101 | ### Write Failure
 102 | 
 103 | If target directory does not exist:
 104 | 
 105 | 1. Create the directory first using Bash mkdir -p
 106 | 1. Then write the file
```


---
## .claude/skills/add-archon-model/SKILL.md

```
   1 | ---
   2 | name: add-archon-model
   3 | description: Guide for adding a new model to the Archon engine. Use when user wants to add support for a new HuggingFace model architecture in ArchonEngine.
   4 | ---
   5 | 
   6 | # Add Archon Model
   7 | 
   8 | Add support for a new HuggingFace model architecture in the Archon training engine.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add a model to Archon?"
  15 | - User wants to support a new model family (e.g., Llama, Mistral, DeepSeek) in
  16 |   ArchonEngine
  17 | - User mentions adding a new `ModelSpec` or model type for Archon
  18 | 
  19 | ## Prerequisites
  20 | 
  21 | Before starting, ensure:
  22 | 
  23 | - The target model is available on HuggingFace (has `config.json` with `model_type`)
  24 | - You know the HuggingFace model ID (e.g., `meta-llama/Llama-3-8B`)
  25 | - The model uses a standard transformer architecture (decoder-only)
  26 | 
  27 | ## Step-by-Step Guide
  28 | 
  29 | ### Step 1: Analyze the Target Model Architecture
  30 | 
  31 | Read the HuggingFace model's source code to extract key architecture information.
  32 | 
  33 | **Action**: Fetch and analyze the model's HuggingFace configuration and modeling files.
  34 | 
  35 | 1. Read the model's `config.json` (via `AutoConfig.from_pretrained`) to identify:
  36 | 
  37 |    - `model_type` string (this is the key used for registry lookup)
  38 |    - All architecture hyperparameters (hidden_size, num_layers, etc.)
  39 |    - Any model-specific fields (e.g., `qk_norm`, `attention_bias`, MoE fields)
  40 | 
  41 | 1. Read the HuggingFace `modeling_*.py` source to identify:
  42 | 
  43 |    - **Attention variant**: Does it have Q/K norm? Attention bias? Sliding window?
  44 |      Multi-latent attention?
  45 |    - **FFN variant**: SwiGLU (gate_proj + up_proj + down_proj)? GeGLU? Standard MLP?
  46 |    - **MoE support**: Does it have MoE layers? What router type? Shared experts?
  47 |    - **RoPE variant**: Standard RoPE? YaRN? NTK-aware scaling? What is the inv_freq
  48 |      formula?
  49 |    - **Normalization**: RMSNorm or LayerNorm? Pre-norm or post-norm? Elementwise affine?
  50 |    - **Weight tying**: Does `tie_word_embeddings` appear in config?
  51 |    - **State dict key names**: What are the HF weight key naming conventions?
  52 | 
  53 | 1. Summarize findings in a checklist like:
  54 | 
  55 | ```
  56 | Target model: <name>
  57 | HF model_type: "<model_type>" (and variants like "<model_type>_moe" if applicable)
  58 | Attention: [standard GQA / with QK norm / with bias / sliding window / ...]
  59 | FFN: [SwiGLU / GeGLU / standard MLP / ...]
  60 | MoE: [no / yes - num_experts, top_k, shared_experts]
  61 | RoPE: [standard / YaRN / NTK-aware / ...]
  62 | Norm: [RMSNorm / LayerNorm] with [pre-norm / post-norm]
  63 | Weight tying: [yes / no]
  64 | ```
  65 | 
  66 | ### Step 2: Select the Reference Model
  67 | 
  68 | Choose the closest existing implementation as a starting point:
  69 | 
  70 | | Target characteristics               | Reference | Why                                     |
  71 | | ------------------------------------ | --------- | --------------------------------------- |
  72 | | Dense-only, standard GQA, no QK norm | `qwen2`   | Simplest baseline, pure dense           |
  73 | | Has QK norm, or has MoE support      | `qwen3`   | Supports QK norm + MoE + shared experts |
  74 | 
  75 | **Action**: Copy the reference model directory as the starting point:
  76 | 
  77 | ```
  78 | areal/experimental/models/archon/<model>/
  79 |   __init__.py
  80 |   spec.py
  81 |   model/
  82 |     args.py
  83 |     model.py
  84 |     rope.py
  85 |     state_dict_adapter.py
  86 |   infra/
  87 |     parallelize.py
  88 | ```
  89 | 
  90 | ### Step 3: Implement `args.py`
  91 | 
  92 | Adapt `<Model>ModelArgs` to match the target model's HuggingFace config fields.
  93 | 
  94 | **Key changes from reference**:
  95 | 
  96 | 1. Update the `@dataclass` fields to match the target model's hyperparameters:
  97 | 
  98 |    - Field names should use Archon conventions (`dim`, `n_layers`, `n_heads`,
  99 |      `n_kv_heads`, `vocab_size`, `head_dim`, `hidden_dim`, `norm_eps`, `rope_theta`,
 100 |      etc.)
 101 |    - Default values should match the smallest variant of the target model
 102 |    - Add model-specific fields (e.g., `attention_bias`, `qk_norm`, `sliding_window`)
 103 | 
 104 | 1. Update `from_hf_config()` to correctly map HuggingFace config attributes:
 105 | 
 106 |    - Use `getattr(hf_config, "field_name", default)` for optional fields
 107 |    - Handle variant-specific fields (e.g., MoE fields only present in MoE variants)
 108 |    - The method must return an instance of the model args class
 109 | 
 110 | **Critical**: Verify every field mapping against the HF model's `config.json`. Incorrect
 111 | mappings here cause silent errors downstream.
 112 | 
 113 | **Base class contract** (`BaseModelArgs`):
 114 | 
 115 | ```python
 116 | @dataclass
 117 | class <Model>ModelArgs(BaseModelArgs):
 118 |     # ... model-specific fields ...
 119 | 
 120 |     @classmethod
 121 |     def from_hf_config(
 122 |         cls,
 123 |         hf_config: PretrainedConfig,
 124 |         is_critic: bool = False,
 125 |         **kwargs,
 126 |     ) -> <Model>ModelArgs:
 127 |         # Map HF config fields to Archon model args
 128 |         ...
 129 | ```
 130 | 
 131 | ### Step 4: Implement `model.py`
 132 | 
 133 | Adapt the model architecture to match the target model.
 134 | 
 135 | **Key components to adapt**:
 136 | 
 137 | 1. **Normalization** (`RMSNorm` or similar):
 138 | 
 139 |    - Check if `elementwise_affine` is configurable
 140 |    - Check the epsilon default value
 141 |    - If the model uses `LayerNorm`, implement accordingly
 142 | 
 143 | 1. **Attention** module:
 144 | 
 145 |    - Q/K/V projection: Check bias presence (`nn.Linear(..., bias=True/False)`)
 146 |    - QK norm: Add `q_norm`/`k_norm` if the model has them, remove if it doesn't
 147 |    - GQA: `n_kv_heads` \< `n_heads` for grouped-query attention
 148 |    - Ulysses SP: Keep the `set_cp_group` / `_sp_enabled` pattern from the reference
 149 |    - Output projection: Check bias presence
 150 | 
 151 | 1. **FeedForward** module:
 152 | 
 153 |    - SwiGLU: `w2(silu(w1(x)) * w3(x))` -- most common for modern LLMs
 154 |    - Check bias in linear layers
 155 |    - For MoE models: `MoE` module replaces `FeedForward` on designated layers
 156 | 
 157 | 1. **TransformerBlock**: Pre-norm (most modern LLMs) vs post-norm
 158 | 
 159 |    - MoE layer detection via `_is_moe_layer()` if applicable
 160 | 
 161 | 1. **Top-level Model** (`<Model>Model(BaseArchonModel)`):
 162 | 
 163 |    - `tok_embeddings`, `layers` (as `ModuleDict`), `norm`, `output`/`score`
 164 |    - `init_weights()`: Match initialization scheme from HF
 165 |    - `init_buffers()`: RoPE cache + MoE buffers
 166 |    - `forward()`: Must follow `BaseArchonModel` signature:
 167 |      `(tokens, positions, cu_seqlens, max_seqlen) -> Tensor`
 168 | 
 169 | **Base class contract** (`BaseArchonModel`):
 170 | 
 171 | ```python
 172 | class <Model>Model(BaseArchonModel):
 173 |     def forward(self, tokens, positions, cu_seqlens, max_seqlen) -> torch.Tensor: ...
 174 |     def init_weights(self) -> None: ...
 175 |     def init_buffers(self, buffer_device) -> None: ...
 176 | ```
 177 | 
 178 | ### Step 5: Implement `rope.py`
 179 | 
 180 | Handle the rotary position embedding variant.
 181 | 
 182 | **Options**:
 183 | 
 184 | 1. **Standard RoPE** (same as qwen2/qwen3): Re-export from qwen2:
 185 | 
 186 |    ```python
 187 |    from areal.experimental.models.archon.qwen2.model.rope import (
 188 |        apply_rotary_emb,
 189 |        precompute_rope_cache,
 190 |        repeat_kv,
 191 |        reshape_for_broadcast,
 192 |        rotate_half,
 193 |    )
 194 |    ```
 195 | 
 196 | 1. **Custom RoPE** (YaRN, NTK-aware, etc.): Implement custom `precompute_rope_cache()`
 197 |    and `apply_rotary_emb()` functions. The key difference is usually in how `inv_freq`
 198 |    is computed (scaling factors, interpolation, etc.).
 199 | 
 200 | ### Step 6: Implement `state_dict_adapter.py`
 201 | 
 202 | Map between HuggingFace and Archon weight key names.
 203 | 
 204 | **This is the most error-prone step.** The adapter must correctly handle:
 205 | 
 206 | 1. **Key name mapping** (`from_hf_map` dict):
 207 | 
 208 |    - Embedding: `model.embed_tokens.weight` -> `tok_embeddings.weight`
 209 |    - Attention: `model.layers.{}.self_attn.q_proj.weight` ->
 210 |      `layers.{}.attention.wq.weight`
 211 |    - FFN: `model.layers.{}.mlp.gate_proj.weight` -> `layers.{}.feed_forward.w1.weight`
 212 |    - Norms: `model.layers.{}.input_layernorm.weight` ->
 213 |      `layers.{}.attention_norm.weight`
 214 |    - Output: `lm_head.weight` -> `output.weight`
 215 |    - Skip keys (set to `None`): `rotary_emb.inv_freq` (computed at runtime)
 216 |    - Model-specific keys: bias terms, QK norm weights, etc.
 217 | 
 218 | 1. **Reverse mapping** (`to_hf_map`): Auto-generated from `from_hf_map`
 219 | 
 220 | 1. **MoE expert weights** (if applicable): 3D\<->2D conversion for expert weights. Copy
 221 |    the MoE handling from qwen3 if the model has MoE.
 222 | 
 223 | 1. **Weight tying**: Skip `output.weight` during `to_hf()` if `tie_word_embeddings=True`
 224 | 
 225 | **Verification approach**: After implementation, the adapter should satisfy:
 226 | 
 227 | ```python
 228 | # Roundtrip: archon -> hf -> archon preserves all keys
 229 | hf_sd = adapter.to_hf(archon_sd)
 230 | roundtrip_sd = adapter.from_hf(hf_sd)
 231 | assert set(roundtrip_sd.keys()) == set(archon_sd.keys())
 232 | ```
 233 | 
 234 | **Base class contract** (`BaseStateDictAdapter`):
 235 | 
 236 | ```python
 237 | class <Model>StateDictAdapter(BaseStateDictAdapter):
 238 |     def from_hf(self, hf_state_dict) -> dict[str, Any]: ...
 239 |     def to_hf(self, archon_state_dict) -> dict[str, Any]: ...
 240 |     def convert_single_to_hf(self, name, tensor) -> list[tuple[str, torch.Tensor]]: ...
 241 | ```
 242 | 
 243 | ### Step 7: Implement `parallelize.py`
 244 | 
 245 | Define the parallelization strategy for the model.
 246 | 
 247 | **The parallelize function** applies parallelism in this order:
 248 | 
 249 | 1. TP (Tensor Parallelism) -- shard attention/FFN across devices
 250 | 1. EP (Expert Parallelism) -- for MoE models only
 251 | 1. CP (Context Parallelism / Ulysses SP) -- sequence parallelism
 252 | 1. AC (Activation Checkpointing) -- memory optimization
 253 | 1. torch.compile -- compilation optimization
 254 | 1. FSDP (Fully Sharded Data Parallelism) -- data parallelism
 255 | 
 256 | **Key adaptations by model architecture**:
 257 | 
 258 | - **Attention with QK norm**: wq/wk use `use_local_output=False` (DTensor output for
 259 |   norm), add `SequenceParallel(sequence_dim=2)` for q_norm/k_norm
 260 | - **Attention without QK norm**: wq/wk/wv all use `use_local_output=True`
 261 | - **Attention with bias**: Bias terms follow the same parallel plan as their weights
 262 | - **MoE layers**: Separate TP plan for MoE input/output, router gate, and expert
 263 |   weights. Copy from qwen3's `apply_moe_ep_tp()` and `apply_non_moe_tp()`
 264 | - **Dense-only models**: Simpler plan without MoE handling. Copy from qwen2
 265 | 
 266 | **Function signature** (must match `ParallelizeFn` protocol):
 267 | 
 268 | ```python
 269 | def parallelize_<model>(
 270 |     model: nn.Module,
 271 |     parallel_dims: ArchonParallelDims,
 272 |     param_dtype: torch.dtype = torch.bfloat16,
 273 |     reduce_dtype: torch.dtype = torch.float32,
 274 |     loss_parallel: bool = True,
 275 |     cpu_offload: bool = False,
 276 |     reshard_after_forward_policy: str = "default",
 277 |     ac_config: ActivationCheckpointConfig | None = None,
 278 |     enable_compile: bool = True,
 279 | ) -> nn.Module:
 280 | ```
 281 | 
 282 | ### Step 8: Create `spec.py` and Register
 283 | 
 284 | Assemble the `ModelSpec` and register it.
 285 | 
 286 | ```python
 287 | from areal.experimental.models.archon.model_spec import ModelSpec, register_model_spec
 288 | from areal.experimental.models.archon.pipeline_parallel import pipeline_llm
 289 | from areal.experimental.models.archon.<model>.infra.parallelize import parallelize_<model>
 290 | from areal.experimental.models.archon.<model>.model.args import <Model>ModelArgs
 291 | from areal.experimental.models.archon.<model>.model.model import <Model>Model
 292 | from areal.experimental.models.archon.<model>.model.state_dict_adapter import (
 293 |     <Model>StateDictAdapter,
 294 | )
 295 | 
 296 | <MODEL>_SPEC = ModelSpec(
 297 |     name="<Model>",
 298 |     model_class=<Model>Model,
 299 |     model_args_class=<Model>ModelArgs,
 300 |     state_dict_adapter_class=<Model>StateDictAdapter,
 301 |     parallelize_fn=parallelize_<model>,
 302 |     supported_model_types=frozenset({"<model_type>"}),  # From HF config.json
 303 |     pipelining_fn=pipeline_llm,
 304 | )
 305 | 
 306 | # Auto-register when module is imported
 307 | register_model_spec(<MODEL>_SPEC)
 308 | 
 309 | __all__ = ["<MODEL>_SPEC"]
 310 | ```
 311 | 
 312 | **Note**: `supported_model_types` should include all HF `model_type` strings that this
 313 | implementation handles (e.g., `{"qwen3", "qwen3_moe"}` for Qwen3).
 314 | 
 315 | ### Step 9: Register in `__init__.py`
 316 | 
 317 | Add the import to `areal/experimental/models/archon/__init__.py`:
 318 | 
 319 | ```python
 320 | from areal.experimental.models.archon.<model> import spec as <model>_spec  # noqa: F401
 321 | ```
 322 | 
 323 | This triggers auto-registration when the module is imported.
 324 | 
 325 | ### Step 10: Verify and Test
 326 | 
 327 | Verification should be done in stages, adapting based on available hardware and the test
 328 | patterns in `tests/experimental/archon/`.
 329 | 
 330 | **Before writing tests**, examine the existing test files to understand current
 331 | patterns:
 332 | 
 333 | ```
 334 | tests/experimental/archon/
 335 |   conftest.py             -- Pytest configuration (version checks)
 336 |   utils.py                -- Shared utilities (model loading, comparison)
 337 |   test_qwen3_args.py      -- Args unit tests (CPU-only)
 338 |   test_state_dict_adapter.py  -- State dict roundtrip tests
 339 |   test_weight_sync.py     -- Weight completeness tests (meta device)
 340 |   test_forward.py         -- Forward precision comparison (single GPU)
 341 |   ...
 342 | ```
 343 | 
 344 | **Test stages** (write tests appropriate for the model's complexity):
 345 | 
 346 | #### Stage 1: Args Tests (CPU-only, always write these)
 347 | 
 348 | Test `from_hf_config()` with mock HuggingFace configs:
 349 | 
 350 | ```python
 351 | # Pattern: Create mock PretrainedConfig, verify args mapping
 352 | from unittest.mock import MagicMock
 353 | 
 354 | def test_args_from_hf_config():
 355 |     hf_config = MagicMock()
 356 |     hf_config.hidden_size = 4096
 357 |     hf_config.num_hidden_layers = 32
 358 |     # ... set all required fields
 359 |     args = <Model>ModelArgs.from_hf_config(hf_config)
 360 |     assert args.dim == 4096
 361 |     assert args.n_layers == 32
 362 | ```
 363 | 
 364 | #### Stage 2: State Dict Adapter Tests (CPU-only)
 365 | 
 366 | Test key mapping roundtrip:
 367 | 
 368 | ```python
 369 | def test_state_dict_roundtrip():
 370 |     # Create adapter with mock config
 371 |     adapter = <Model>StateDictAdapter(mock_config)
 372 |     # Create fake archon state dict with expected keys
 373 |     archon_sd = {"tok_embeddings.weight": torch.randn(vocab, dim), ...}
 374 |     # Roundtrip
 375 |     hf_sd = adapter.to_hf(archon_sd)
 376 |     roundtrip = adapter.from_hf(hf_sd)
 377 |     assert set(roundtrip.keys()) == set(archon_sd.keys())
 378 | ```
 379 | 
 380 | #### Stage 3: Weight Completeness (meta device, CPU-only)
 381 | 
 382 | Verify all model parameters have HF mappings:
 383 | 
 384 | ```python
 385 | def test_weight_completeness():
 386 |     # Create model on meta device
 387 |     with torch.device("meta"):
 388 |         model = <Model>Model(args)
 389 |     adapter = <Model>StateDictAdapter(hf_config)
 390 |     # Check every archon param has a HF mapping
 391 |     for name, _ in model.named_parameters():
 392 |         hf_pairs = adapter.convert_single_to_hf(name, torch.empty(0))
 393 |         assert len(hf_pairs) > 0, f"No HF mapping for {name}"
 394 | ```
 395 | 
 396 | #### Stage 4: Forward Precision (single GPU, if available)
 397 | 
 398 | Compare Archon model output against HuggingFace reference:
 399 | 
 400 | ```python
 401 | @pytest.mark.skipif(not torch.cuda.is_available(), reason="Requires CUDA")
 402 | def test_forward_matches_hf():
 403 |     # Load both HF and Archon models
 404 |     # Run forward on same input
 405 |     # Compare logits within tolerance
 406 | ```
 407 | 
 408 | **Important**: Do NOT hardcode the test categories. Inspect the existing test files in
 409 | `tests/experimental/archon/` and follow the same patterns, fixtures, and markers. Adapt
 410 | test scope to the model's specific features (e.g., add MoE-specific tests only if the
 411 | model has MoE).
 412 | 
 413 | ## Reference Implementations
 414 | 
 415 | | Model | Directory                                 | Features                                                |
 416 | | ----- | ----------------------------------------- | ------------------------------------------------------- |
 417 | | Qwen2 | `areal/experimental/models/archon/qwen2/` | Dense, attention bias, no QK norm                       |
 418 | | Qwen3 | `areal/experimental/models/archon/qwen3/` | Dense + MoE, QK norm, no attention bias, shared experts |
 419 | 
 420 | ## Architecture Decision Map
 421 | 
 422 | | Feature             | qwen2    | qwen3                      | What to check in target model                            |
 423 | | ------------------- | -------- | -------------------------- | -------------------------------------------------------- |
 424 | | Attention bias      | Yes      | No                         | `attention_bias` in HF config                            |
 425 | | QK norm             | No       | Yes                        | `qk_norm` in HF config or QKNorm module in modeling file |
 426 | | MoE                 | No       | Yes                        | `num_experts`/`num_local_experts` in HF config           |
 427 | | Shared experts      | No       | Yes                        | `num_shared_experts` in HF config                        |
 428 | | Decoder sparse step | No       | Yes                        | `decoder_sparse_step` in HF config                       |
 429 | | Weight tying        | Both     | Both                       | `tie_word_embeddings` in HF config                       |
 430 | | RoPE                | Standard | Standard (re-export qwen2) | Check inv_freq formula in HF modeling code               |
 431 | 
 432 | ## Common Mistakes
 433 | 
 434 | - Not mapping all HF keys in `state_dict_adapter.py` (causes silent weight drops)
 435 | - Wrong `from_hf_config()` field mapping (uses wrong HF config attribute name)
 436 | - Forgetting to handle `None` keys in `from_hf_map` (keys to skip like
 437 |   `rotary_emb.inv_freq`)
 438 | - Missing MoE expert weight 3D\<->2D conversion when model has MoE
 439 | - Wrong TP plan for attention with/without QK norm (`use_local_output` must match)
 440 | - Forgetting to add import line in `areal/experimental/models/archon/__init__.py`
 441 | - Not including all `model_type` variants in `supported_model_types` frozenset
 442 | - Using `print` instead of `areal.utils.logging.getLogger()`
 443 | 
 444 | ## File Checklist
 445 | 
 446 | After completion, verify all files exist and are consistent:
 447 | 
 448 | - [ ] `areal/experimental/models/archon/<model>/__init__.py`
 449 | - [ ] `areal/experimental/models/archon/<model>/spec.py` -- ModelSpec + register
 450 | - [ ] `areal/experimental/models/archon/<model>/model/args.py` -- ModelArgs +
 451 |   from_hf_config
 452 | - [ ] `areal/experimental/models/archon/<model>/model/model.py` -- Model + Attention +
 453 |   FFN
 454 | - [ ] `areal/experimental/models/archon/<model>/model/rope.py` -- RoPE (or re-export)
 455 | - [ ] `areal/experimental/models/archon/<model>/model/state_dict_adapter.py` -- Key
 456 |   mapping
 457 | - [ ] `areal/experimental/models/archon/<model>/infra/parallelize.py` -- Parallel
 458 |   strategy
 459 | - [ ] `areal/experimental/models/archon/__init__.py` -- Import line added
 460 | - [ ] `tests/experimental/archon/test_<model>_*.py` -- Tests
 461 | 
 462 | ______________________________________________________________________
 463 | 
 464 | <!--
 465 | ================================================================================
 466 |                             MAINTAINER GUIDE
 467 | ================================================================================
 468 | 
 469 | Location: .claude/skills/add-archon-model/SKILL.md
 470 | Invocation: /add-archon-model <model_name>
 471 | 
 472 | ## Purpose
 473 | 
 474 | Semi-automated guide for adding new model architectures to the Archon training engine.
 475 | Unlike simpler skills (add-reward, add-dataset), this skill actively guides Claude to:
 476 | 1. Analyze HuggingFace source code to extract architecture details
 477 | 2. Select the closest reference implementation (qwen2 or qwen3)
 478 | 3. Generate code skeletons adapted to the target architecture
 479 | 4. Create appropriate tests based on existing test patterns
 480 | 
 481 | ## How to Update
 482 | 
 483 | ### When New Reference Models Are Added
 484 | 1. Add to "Reference Implementations" table
 485 | 2. Update "Architecture Decision Map" with new feature columns
 486 | 3. Update Step 2 (reference selection) with new options
 487 | 
 488 | ### When Base Classes Change
 489 | 1. Update contract signatures in Steps 3, 4, 6, 7
 490 | 2. Update file checklist if new files are required
 491 | 
 492 | ### When ModelSpec Changes
 493 | 1. Update Step 8 with new ModelSpec fields
 494 | 2. Update spec.py template
 495 | 
 496 | ### When Test Patterns Change
 497 | 1. Update Step 10 with new test patterns
 498 | 2. Do NOT hardcode test categories -- keep it flexible
 499 | 
 500 | ### Important Design Decisions
 501 | - This skill is SEMI-AUTOMATED: Claude should read HF source and generate code,
 502 |   not just provide templates for the user to fill in manually
 503 | - The skill references existing test files rather than hardcoding test categories,
 504 |   ensuring it stays current as the test suite evolves
 505 | - Reference model selection (qwen2 vs qwen3) is based on MoE and QK norm presence
 506 | 
 507 | ================================================================================
 508 | -->
```


---
## .claude/skills/add-dataset/SKILL.md

```
   1 | ---
   2 | name: add-dataset
   3 | description: Guide for adding a new dataset loader to AReaL. Use when user wants to add a new dataset.
   4 | ---
   5 | 
   6 | # Add Dataset
   7 | 
   8 | Add a new dataset loader to AReaL.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add a dataset?"
  15 | - User wants to integrate a new dataset
  16 | - User mentions creating a dataset loader
  17 | 
  18 | ## Step-by-Step Guide
  19 | 
  20 | ### Step 1: Create Dataset File
  21 | 
  22 | Create `areal/dataset/<name>.py`:
  23 | 
  24 | ```python
  25 | from datasets import Dataset, load_dataset
  26 | 
  27 | 
  28 | def get_<name>_sft_dataset(
  29 |     path: str,
  30 |     split: str,
  31 |     tokenizer,
  32 |     max_length: int | None = None,
  33 | ) -> Dataset:
  34 |     """Load dataset for SFT training.
  35 | 
  36 |     Args:
  37 |         path: Path to dataset (HuggingFace hub or local path)
  38 |         split: Dataset split (train/validation/test)
  39 |         tokenizer: Tokenizer for processing
  40 |         max_length: Maximum sequence length (optional)
  41 | 
  42 |     Returns:
  43 |         HuggingFace Dataset with processed samples
  44 |     """
  45 |     dataset = load_dataset(path=path, split=split)
  46 | 
  47 |     def process(sample):
  48 |         # Tokenize the full sequence (prompt + response)
  49 |         seq_token = tokenizer.encode(
  50 |             sample["question"] + sample["answer"] + tokenizer.eos_token
  51 |         )
  52 |         prompt_token = tokenizer.encode(sample["question"])
  53 |         # Loss mask: 0 for prompt, 1 for response
  54 |         loss_mask = [0] * len(prompt_token) + [1] * (len(seq_token) - len(prompt_token))
  55 |         return {"input_ids": seq_token, "loss_mask": loss_mask}
  56 | 
  57 |     dataset = dataset.map(process).remove_columns(["question", "answer"])
  58 | 
  59 |     if max_length is not None:
  60 |         dataset = dataset.filter(lambda x: len(x["input_ids"]) <= max_length)
  61 | 
  62 |     return dataset
  63 | 
  64 | 
  65 | def get_<name>_rl_dataset(
  66 |     path: str,
  67 |     split: str,
  68 |     tokenizer,
  69 |     max_length: int | None = None,
  70 | ) -> Dataset:
  71 |     """Load dataset for RL training.
  72 | 
  73 |     Args:
  74 |         path: Path to dataset
  75 |         split: Dataset split
  76 |         tokenizer: Tokenizer for length filtering
  77 |         max_length: Maximum sequence length
  78 | 
  79 |     Returns:
  80 |         HuggingFace Dataset with prompts and answers for reward computation
  81 |     """
  82 |     dataset = load_dataset(path=path, split=split)
  83 | 
  84 |     def process(sample):
  85 |         messages = [
  86 |             {
  87 |                 "role": "user",
  88 |                 "content": sample["question"],
  89 |             }
  90 |         ]
  91 |         return {"messages": messages, "answer": sample["answer"]}
  92 | 
  93 |     dataset = dataset.map(process).remove_columns(["question"])
  94 | 
  95 |     if max_length is not None:
  96 | 
  97 |         def filter_length(sample):
  98 |             content = sample["messages"][0]["content"]
  99 |             tokens = tokenizer.encode(content)
 100 |             return len(tokens) <= max_length
 101 | 
 102 |         dataset = dataset.filter(filter_length)
 103 | 
 104 |     return dataset
 105 | ```
 106 | 
 107 | ### Step 2: Register in __init__.py
 108 | 
 109 | Update `areal/dataset/__init__.py`:
 110 | 
 111 | ```python
 112 | # Add to VALID_DATASETS
 113 | VALID_DATASETS = [
 114 |     # ... existing datasets
 115 |     "<name>",
 116 | ]
 117 | 
 118 | # Add to _get_custom_dataset function
 119 | def _get_custom_dataset(name: str, ...):
 120 |     # ... existing code
 121 |     elif name == "<name>":
 122 |         from areal.dataset.<name> import get_<name>_sft_dataset, get_<name>_rl_dataset
 123 |         if dataset_type == "sft":
 124 |             return get_<name>_sft_dataset(path, split, max_length, tokenizer)
 125 |         else:
 126 |             return get_<name>_rl_dataset(path, split, max_length, tokenizer)
 127 | ```
 128 | 
 129 | ### Step 3: Add Config (Optional)
 130 | 
 131 | If the dataset needs special configuration, add to `areal/api/cli_args.py`:
 132 | 
 133 | ```python
 134 | @dataclass
 135 | class TrainDatasetConfig:
 136 |     # ... existing fields
 137 |     <name>_specific_field: Optional[str] = None
 138 | ```
 139 | 
 140 | ### Step 4: Add Tests
 141 | 
 142 | Create `tests/test_<name>_dataset.py`:
 143 | 
 144 | ```python
 145 | import pytest
 146 | from areal.dataset.<name> import get_<name>_sft_dataset, get_<name>_rl_dataset
 147 | 
 148 | def test_sft_dataset_loads(tokenizer):
 149 |     dataset = get_<name>_sft_dataset("path/to/data", split="train", tokenizer=tokenizer)
 150 |     assert len(dataset) > 0
 151 |     assert "input_ids" in dataset.column_names
 152 |     assert "loss_mask" in dataset.column_names
 153 | 
 154 | def test_rl_dataset_loads(tokenizer):
 155 |     dataset = get_<name>_rl_dataset("path/to/data", split="train", tokenizer=tokenizer)
 156 |     assert len(dataset) > 0
 157 |     assert "messages" in dataset.column_names
 158 |     assert "answer" in dataset.column_names
 159 | ```
 160 | 
 161 | ## Reference Implementations
 162 | 
 163 | | Dataset    | File                               | Description              |
 164 | | ---------- | ---------------------------------- | ------------------------ |
 165 | | GSM8K      | `areal/dataset/gsm8k.py`           | Math word problems       |
 166 | | Geometry3K | `areal/dataset/geometry3k.py`      | Geometry problems        |
 167 | | CLEVR      | `areal/dataset/clevr_count_70k.py` | Visual counting          |
 168 | | HH-RLHF    | `areal/dataset/hhrlhf.py`          | Helpfulness/Harmlessness |
 169 | | TORL       | `areal/dataset/torl_data.py`       | Tool-use RL              |
 170 | 
 171 | ## Required Fields
 172 | 
 173 | ### SFT Dataset
 174 | 
 175 | ```python
 176 | {
 177 |     "messages": [
 178 |         {"role": "user", "content": "..."},
 179 |         {"role": "assistant", "content": "..."},
 180 |     ]
 181 | }
 182 | ```
 183 | 
 184 | ### RL Dataset
 185 | 
 186 | ```python
 187 | {
 188 |     "messages": [
 189 |         {"role": "user", "content": "..."},
 190 |     ],
 191 |     "answer": "ground_truth_for_reward",
 192 |     # Optional metadata for reward function
 193 | }
 194 | ```
 195 | 
 196 | ## Common Mistakes
 197 | 
 198 | - ❌ Returning `List[Dict]` instead of HuggingFace `Dataset`
 199 | - ❌ Using Python loops instead of `dataset.map()`/`filter()`
 200 | - ❌ Missing `"messages"` field for RL datasets
 201 | - ❌ Wrong message format (should be list of dicts with `role` and `content`)
 202 | - ❌ Not registering in `__init__.py`
 203 | 
 204 | ______________________________________________________________________
 205 | 
 206 | <!--
 207 | ================================================================================
 208 |                             MAINTAINER GUIDE
 209 | ================================================================================
 210 | 
 211 | Location: .claude/skills/add-dataset/SKILL.md
 212 | Invocation: /add-dataset <name>
 213 | 
 214 | ## Purpose
 215 | 
 216 | Step-by-step guide for adding new dataset loaders.
 217 | 
 218 | ## How to Update
 219 | 
 220 | ### When Dataset API Changes
 221 | 1. Update the code templates
 222 | 2. Update required fields section
 223 | 3. Update registration example
 224 | 
 225 | ### When New Dataset Types Added
 226 | 1. Add to "Reference Implementations" table
 227 | 2. Add any new required fields
 228 | 
 229 | ================================================================================
 230 | -->
```


---
## .claude/skills/add-reward/SKILL.md

```
   1 | ---
   2 | name: add-reward
   3 | description: Guide for adding a new reward function to AReaL. Use when user wants to create a reward function.
   4 | ---
   5 | 
   6 | # Add Reward
   7 | 
   8 | Add a new reward function to AReaL.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add a reward function?"
  15 | - User wants to implement custom rewards
  16 | - User mentions reward computation
  17 | 
  18 | ## Step-by-Step Guide
  19 | 
  20 | ### Step 1: Create Reward File
  21 | 
  22 | Create `areal/reward/<name>.py`:
  23 | 
  24 | ```python
  25 | from typing import Any
  26 | 
  27 | from areal.utils import logging
  28 | 
  29 | logger = logging.getLogger("MyReward")
  30 | 
  31 | 
  32 | def <name>_reward_fn(
  33 |     prompt: str,
  34 |     completions: str,
  35 |     prompt_ids,
  36 |     completion_ids,
  37 |     answer: str | None = None,
  38 |     **kwargs: Any,
  39 | ) -> float:
  40 |     """Compute reward for a single completion.
  41 | 
  42 |     Args:
  43 |         prompt: Prompt string
  44 |         completions: Completion string (model output)
  45 |         prompt_ids: Tokenized prompt IDs
  46 |         completion_ids: Tokenized completion IDs
  47 |         answer: Ground truth answer from dataset (optional)
  48 |         **kwargs: Additional data from dataset
  49 | 
  50 |     Returns:
  51 |         Reward value (float), typically 0.0 or 1.0
  52 |     """
  53 |     try:
  54 |         # Extract answer from completion
  55 |         extracted = _extract_answer(completions)
  56 | 
  57 |         # Compare with ground truth
  58 |         if answer is not None and extracted == str(answer):
  59 |             return 1.0
  60 |         return 0.0
  61 |     except Exception:
  62 |         logger.warning("Exception in reward computation", exc_info=True)
  63 |         return 0.0
  64 | 
  65 | 
  66 | def _extract_answer(completion: str) -> str:
  67 |     """Extract the answer from a completion string.
  68 | 
  69 |     Implement your extraction logic here.
  70 |     """
  71 |     # Example: Extract content from \boxed{}
  72 |     import re
  73 | 
  74 |     match = re.search(r"\\boxed\{([^}]+)\}", completion)
  75 |     if match:
  76 |         return match.group(1).strip()
  77 |     return completion.strip()
  78 | ```
  79 | 
  80 | ### Step 2: Register in __init__.py
  81 | 
  82 | Update `areal/reward/__init__.py`:
  83 | 
  84 | ```python
  85 | # Add to VALID_REWARD_FN
  86 | VALID_REWARD_FN = [
  87 |     # ... existing reward functions
  88 |     "<name>",
  89 | ]
  90 | 
  91 | # Add to get_reward_fn function
  92 | def get_reward_fn(name: str, **kwargs):
  93 |     # ... existing code
  94 |     elif name == "<name>":
  95 |         from areal.reward.<name> import <name>_reward_fn
  96 |         return <name>_reward_fn
  97 | ```
  98 | 
  99 | ### Step 3: Handle Blocking Operations
 100 | 
 101 | If your reward function uses blocking operations (e.g., API calls, model inference), the
 102 | workflow will wrap it with `AsyncRewardWrapper`:
 103 | 
 104 | ```python
 105 | # In your workflow
 106 | from areal.reward import AsyncRewardWrapper
 107 | 
 108 | self.reward_fn = AsyncRewardWrapper(reward_fn)
 109 | 
 110 | # Then call it asynchronously
 111 | rewards = await self.reward_fn(prompt, completions, **data)
 112 | ```
 113 | 
 114 | ### Step 4: Add Tests
 115 | 
 116 | Create `tests/test_<name>_reward.py`:
 117 | 
 118 | ```python
 119 | import pytest
 120 | from areal.reward.<name> import <name>_reward_fn
 121 | 
 122 | def test_reward_correct_answer():
 123 |     reward = <name>_reward_fn(
 124 |         prompt="What is 2+2?",
 125 |         completions="The answer is \\boxed{4}",
 126 |         prompt_ids=None,
 127 |         completion_ids=None,
 128 |         answer="4",
 129 |     )
 130 |     assert reward == 1.0
 131 | 
 132 | def test_reward_wrong_answer():
 133 |     reward = <name>_reward_fn(
 134 |         prompt="What is 2+2?",
 135 |         completions="The answer is \\boxed{5}",
 136 |         prompt_ids=None,
 137 |         completion_ids=None,
 138 |         answer="4",
 139 |     )
 140 |     assert reward == 0.0
 141 | ```
 142 | 
 143 | ## Reference Implementations
 144 | 
 145 | | Reward     | File                              | Description                  |
 146 | | ---------- | --------------------------------- | ---------------------------- |
 147 | | GSM8K      | `areal/reward/gsm8k.py`           | Math answer verification     |
 148 | | Geometry3K | `areal/reward/geometry3k.py`      | Geometry answer verification |
 149 | | CLEVR      | `areal/reward/clevr_count_70k.py` | Counting verification        |
 150 | | MathVerify | `areal/reward/math_verify.py`     | General math verification    |
 151 | 
 152 | ## Function Signature
 153 | 
 154 | All reward functions must follow this signature:
 155 | 
 156 | ```python
 157 | def reward_fn(
 158 |     prompt: str,               # Input prompt string
 159 |     completions: str,          # Model completion string
 160 |     prompt_ids,                # Tokenized prompt
 161 |     completion_ids,            # Tokenized completion
 162 |     **kwargs: Any,             # Additional data from dataset (e.g., answer)
 163 | ) -> float:                    # Reward value (typically 0.0 or 1.0)
 164 | ```
 165 | 
 166 | **Note**: The reward function is called once per sample. Batching is handled by
 167 | `AsyncRewardWrapper` in the workflow.
 168 | 
 169 | ## Key Requirements
 170 | 
 171 | 1. **Deterministic**: Same inputs should produce same outputs
 172 | 1. **Return float**: Output is a single float value per sample
 173 | 1. **No blocking in async context**: Use `AsyncRewardWrapper` if needed
 174 | 1. **Logging**: Use `areal.utils.logging`, not `print`
 175 | 1. **Handle exceptions**: Return 0.0 on error, don't raise
 176 | 
 177 | ## Common Mistakes
 178 | 
 179 | - ❌ Returning a tensor instead of a float
 180 | - ❌ Expecting batched inputs (reward is called per sample)
 181 | - ❌ Non-deterministic behavior
 182 | - ❌ Blocking operations without `AsyncRewardWrapper`
 183 | - ❌ Raising exceptions instead of returning 0.0
 184 | 
 185 | ______________________________________________________________________
 186 | 
 187 | <!--
 188 | ================================================================================
 189 |                             MAINTAINER GUIDE
 190 | ================================================================================
 191 | 
 192 | Location: .claude/skills/add-reward/SKILL.md
 193 | Invocation: /add-reward <name>
 194 | 
 195 | ## Purpose
 196 | 
 197 | Step-by-step guide for adding new reward functions.
 198 | 
 199 | ## How to Update
 200 | 
 201 | ### When Reward API Changes
 202 | 1. Update the function signature section
 203 | 2. Update the code template
 204 | 3. Update key requirements
 205 | 
 206 | ### When New Reward Patterns Emerge
 207 | 1. Add to "Reference Implementations" table
 208 | 2. Add examples for new patterns
 209 | 
 210 | ================================================================================
 211 | -->
```


---
## .claude/skills/add-unit-tests/SKILL.md

```
   1 | ---
   2 | name: add-unit-tests
   3 | description: Guide for adding unit tests to AReaL. Use when user wants to add tests for new functionality or increase test coverage.
   4 | ---
   5 | 
   6 | # Add Unit Tests
   7 | 
   8 | Add unit tests to AReaL following the project's testing conventions.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add tests?"
  15 | - User wants to increase test coverage
  16 | - User needs to write tests for new functionality
  17 | - User wants to understand AReaL testing patterns
  18 | 
  19 | ## Step-by-Step Guide
  20 | 
  21 | ### Step 1: Understand Test Types
  22 | 
  23 | AReaL has two main test categories:
  24 | 
  25 | | Test Type             | Purpose                            | Location Pattern                   | How It Runs                                |
  26 | | --------------------- | ---------------------------------- | ---------------------------------- | ------------------------------------------ |
  27 | | **Unit Tests**        | Test individual functions/modules  | `tests/test_<module>_<feature>.py` | Directly via pytest                        |
  28 | | **Distributed Tests** | Test distributed/parallel behavior | `tests/torchrun/run_*.py`          | Via torchrun (called by pytest subprocess) |
  29 | 
  30 | **Note**: All tests are invoked via pytest. Distributed tests use `torchrun` but are
  31 | still called from pytest test files.
  32 | 
  33 | ### Step 2: Create Test File Structure
  34 | 
  35 | Create test file with naming convention: `test_<module>_<feature>.py`
  36 | 
  37 | ```python
  38 | import pytest
  39 | import torch
  40 | 
  41 | # Import the module to test
  42 | from areal.dataset.gsm8k import get_gsm8k_sft_dataset
  43 | from tests.utils import get_dataset_path  # Optional test utilities
  44 | # For mocking tokenizer: from unittest.mock import MagicMock
  45 | ```
  46 | 
  47 | ### Step 3: Write Test Functions
  48 | 
  49 | Follow Arrange-Act-Assert pattern:
  50 | 
  51 | ```python
  52 | def test_function_under_condition_returns_expected():
  53 |     """Test that function returns expected value under condition."""
  54 |     # Arrange
  55 |     input_data = 5
  56 |     expected_output = 10
  57 | 
  58 |     # Act
  59 |     result = function_under_test(input_data)
  60 | 
  61 |     # Assert
  62 |     assert result == expected_output
  63 | ```
  64 | 
  65 | ### Step 4: Add Pytest Markers and CI Strategy
  66 | 
  67 | Use appropriate pytest markers:
  68 | 
  69 | | Marker                                  | When to Use                                                  |
  70 | | --------------------------------------- | ------------------------------------------------------------ |
  71 | | `@pytest.mark.slow`                     | Test takes > 10 seconds (excluded from CI by default)        |
  72 | | `@pytest.mark.ci`                       | Slow test that must run in CI (use with `@pytest.mark.slow`) |
  73 | | `@pytest.mark.asyncio`                  | Async test functions                                         |
  74 | | `@pytest.mark.skipif(cond, reason=...)` | Conditional skip                                             |
  75 | | `@pytest.mark.parametrize(...)`         | Parameterized tests                                          |
  76 | 
  77 | **CI Test Strategy**:
  78 | 
  79 | - `@pytest.mark.slow`: Excluded from CI by default (CI runs `pytest -m "not slow"`)
  80 | - `@pytest.mark.slow` + `@pytest.mark.ci`: Slow but must run in CI
  81 | - No marker: Runs in CI (fast unit tests)
  82 | 
  83 | ```python
  84 | @pytest.mark.asyncio
  85 | async def test_async_function():
  86 |     result = await async_function()
  87 |     assert result == expected
  88 | 
  89 | @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
  90 | def test_gpu_feature():
  91 |     tensor = torch.tensor([1, 2, 3], device="cuda")
  92 |     # ... assertions
  93 | 
  94 | @pytest.mark.parametrize("batch_size", [1, 4, 16])
  95 | def test_with_parameters(batch_size):
  96 |     # Parameterized test
  97 | 
  98 | @pytest.mark.slow
  99 | def test_slow_function():
 100 |     # Excluded from CI by default
 101 | 
 102 | @pytest.mark.slow
 103 | @pytest.mark.ci
 104 | def test_slow_but_required_in_ci():
 105 |     # Slow but must run in CI
 106 | ```
 107 | 
 108 | ### Step 5: Mock Distributed Environment
 109 | 
 110 | For unit tests that need distributed mocks:
 111 | 
 112 | ```python
 113 | import torch.distributed as dist
 114 | 
 115 | def test_distributed_function(monkeypatch):
 116 |     monkeypatch.setattr(dist, "get_rank", lambda: 0)
 117 |     monkeypatch.setattr(dist, "get_world_size", lambda: 2)
 118 |     result = distributed_function()
 119 |     assert result == expected
 120 | ```
 121 | 
 122 | ### Step 6: Handle GPU Dependencies
 123 | 
 124 | Always skip gracefully when GPU unavailable:
 125 | 
 126 | ```python
 127 | CUDA_AVAILABLE = torch.cuda.is_available()
 128 | 
 129 | @pytest.mark.skipif(not CUDA_AVAILABLE, reason="CUDA not available")
 130 | def test_gpu_function():
 131 |     tensor = torch.tensor([1, 2, 3], device="cuda")
 132 |     # ... assertions
 133 | ```
 134 | 
 135 | ## Key Requirements (Based on testing.md)
 136 | 
 137 | ### Mocking Distributed
 138 | 
 139 | - Use `torch.distributed.fake_pg` for unit tests
 140 | - Mock `dist.get_rank()` and `dist.get_world_size()` explicitly
 141 | - Don't mock internals of FSDP/DTensor
 142 | 
 143 | ### GPU Test Constraints
 144 | 
 145 | - **Always skip gracefully** when GPU unavailable
 146 | - Clean up GPU memory: `torch.cuda.empty_cache()` in fixtures
 147 | - Use smallest possible model/batch for unit tests
 148 | 
 149 | ### Assertions
 150 | 
 151 | - Use `torch.testing.assert_close()` for tensor comparison
 152 | - Specify `rtol`/`atol` explicitly for numerical tests
 153 | - Avoid bare `assert tensor.equal()` - no useful error message
 154 | 
 155 | ## Reference Implementations
 156 | 
 157 | | Test File                        | Description                            | Key Patterns                                      |
 158 | | -------------------------------- | -------------------------------------- | ------------------------------------------------- |
 159 | | `tests/test_utils.py`            | Utility function tests                 | Fixtures, parametrized tests                      |
 160 | | `tests/test_examples.py`         | Integration tests with dataset loading | Dataset path resolution, success pattern matching |
 161 | | `tests/test_fsdp_engine_nccl.py` | Distributed tests                      | Torchrun integration                              |
 162 | 
 163 | ## Common Mistakes
 164 | 
 165 | - ❌ **Missing test file registration**: Ensure file follows `test_*.py` naming
 166 | - ❌ **GPU dependency without skip**: Always use `@pytest.mark.skipif` for GPU tests
 167 | - ❌ **Incorrect tensor comparisons**: Use `torch.testing.assert_close()` not
 168 |   `assert tensor.equal()`
 169 | - ❌ **Memory leaks in GPU tests**: Clean up with `torch.cuda.empty_cache()`
 170 | - ❌ **Mocking too much**: Don't mock FSDP/DTensor internals
 171 | - ❌ **Unclear test names**: Follow `test_<what>_<condition>_<expected>` pattern
 172 | - ❌ **No docstrings**: Add descriptive docstrings to test functions
 173 | 
 174 | ## Integration with Other Skills
 175 | 
 176 | This skill complements other AReaL development skills:
 177 | 
 178 | - **After `/add-dataset`**: Add tests for new dataset loaders
 179 | - **After `/add-workflow`**: Add tests for new workflows
 180 | - **After `/add-reward`**: Add tests for new reward functions
 181 | - **With `planner` agent**: Reference this skill when planning test implementation
 182 | 
 183 | ## Running Tests
 184 | 
 185 | ```bash
 186 | # First check GPU availability (many tests require GPU)
 187 | python -c "import torch; print('GPU available:', torch.cuda.is_available())"
 188 | 
 189 | # Run specific test file
 190 | uv run pytest tests/test_<name>.py
 191 | 
 192 | # Skip slow tests (CI default)
 193 | uv run pytest -m "not slow"
 194 | 
 195 | # Run with verbose output
 196 | uv run pytest -v
 197 | 
 198 | # Run distributed tests (requires torchrun and multi-GPU)
 199 | # Note: Usually invoked via pytest test files
 200 | torchrun --nproc_per_node=2 tests/torchrun/run_<test>.py
 201 | ```
 202 | 
 203 | <!--
 204 | ================================================================================
 205 |                             MAINTAINER GUIDE
 206 | ================================================================================
 207 | 
 208 | Location: .claude/skills/add-unit-tests/SKILL.md
 209 | Invocation: /add-unit-tests
 210 | 
 211 | ## Purpose
 212 | 
 213 | Step-by-step guide for adding unit tests to AReaL.
 214 | 
 215 | ## How to Update
 216 | 
 217 | ### When Testing Conventions Change
 218 | 1. Update "Key Requirements" section based on `testing.md`
 219 | 2. Update test examples to match new patterns
 220 | 3. Update reference implementations
 221 | 
 222 | ### When Test Types Need Update
 223 | 1. Update "Understand Test Types" table (currently two main types)
 224 | 2. Add new examples if needed
 225 | 3. Update common mistakes
 226 | 
 227 | ### Integration with Other Skills
 228 | Ensure references to other skills (`/add-dataset`, `/add-workflow`, `/add-reward`) remain accurate.
 229 | 
 230 | ================================================================================
 231 | -->
```


---
## .claude/skills/add-workflow/SKILL.md

```
   1 | ---
   2 | name: add-workflow
   3 | description: Guide for adding a new RolloutWorkflow to AReaL. Use when user wants to create a new workflow.
   4 | ---
   5 | 
   6 | # Add Workflow
   7 | 
   8 | Add a new RolloutWorkflow implementation to AReaL.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add a workflow?"
  15 | - User wants to create a new RolloutWorkflow
  16 | - User mentions implementing a custom rollout
  17 | 
  18 | ## Prerequisites
  19 | 
  20 | Before starting, ensure you understand:
  21 | 
  22 | - The workflow's purpose and requirements
  23 | - Input/output data format
  24 | - Reward function to use
  25 | 
  26 | ## Step-by-Step Guide
  27 | 
  28 | ### Step 1: Create Workflow File
  29 | 
  30 | Create `areal/workflow/<name>.py`:
  31 | 
  32 | ```python
  33 | import uuid
  34 | from typing import Any, Callable
  35 | 
  36 | import torch
  37 | 
  38 | from areal.api.cli_args import GenerationHyperparameters
  39 | from areal.api.engine_api import InferenceEngine
  40 | from areal.api.io_struct import ModelRequest, ModelResponse
  41 | from areal.api.reward_api import AsyncRewardWrapper
  42 | from areal.api.workflow_api import RolloutWorkflow
  43 | from areal.utils import logging
  44 | 
  45 | logger = logging.getLogger("MyWorkflow")
  46 | 
  47 | 
  48 | class MyWorkflow(RolloutWorkflow):
  49 |     """Description of your workflow."""
  50 | 
  51 |     def __init__(
  52 |         self,
  53 |         gconfig: GenerationHyperparameters,
  54 |         tokenizer,
  55 |         reward_fn: Callable,
  56 |     ):
  57 |         self.gconfig = gconfig.new_with_stop_and_pad_token_ids(tokenizer)
  58 |         self.tokenizer = tokenizer
  59 |         self.async_reward_fn = AsyncRewardWrapper(reward_fn)
  60 | 
  61 |     async def arun_episode(
  62 |         self,
  63 |         engine: InferenceEngine,
  64 |         data: dict[str, Any],
  65 |     ) -> dict[str, torch.Tensor]:
  66 |         """Run a single episode. MUST be async and non-blocking."""
  67 | 
  68 |         # 1. Prepare input_ids from data
  69 |         input_ids = self.tokenizer.apply_chat_template(
  70 |             data["messages"],
  71 |             tokenize=True,
  72 |             add_generation_prompt=True,
  73 |         )
  74 | 
  75 |         # 2. Build ModelRequest
  76 |         req = ModelRequest(
  77 |             rid=uuid.uuid4().hex,
  78 |             input_ids=list(input_ids),
  79 |             gconfig=self.gconfig.new(n_samples=1),
  80 |             tokenizer=self.tokenizer,
  81 |         )
  82 | 
  83 |         # 3. Generate completion (async)
  84 |         resp: ModelResponse = await engine.agenerate(req)
  85 | 
  86 |         # 4. Compute reward (async)
  87 |         prompt_str = self.tokenizer.decode(input_ids)
  88 |         completion_str = self.tokenizer.decode(resp.output_tokens)
  89 |         reward = await self.async_reward_fn(
  90 |             prompt_str,
  91 |             completion_str,
  92 |             resp.input_tokens,
  93 |             resp.output_tokens,
  94 |             **data,
  95 |         )
  96 | 
  97 |         # 5. Return results in expected format
  98 |         return {
  99 |             "input_ids": torch.tensor(resp.input_tokens),
 100 |             "output_ids": torch.tensor(resp.output_tokens),
 101 |             "reward": torch.tensor(reward),
 102 |         }
 103 | ```
 104 | 
 105 | ### Step 2: Register in __init__.py
 106 | 
 107 | Add to `areal/workflow/__init__.py`:
 108 | 
 109 | ```python
 110 | from areal.workflow.<name> import MyWorkflow
 111 | 
 112 | __all__ = [
 113 |     # ... existing exports
 114 |     "MyWorkflow",
 115 | ]
 116 | ```
 117 | 
 118 | ### Step 3: Update Entry Script
 119 | 
 120 | Update your training script to use the new workflow:
 121 | 
 122 | ```python
 123 | trainer.train(
 124 |     workflow="areal.workflow.<name>.MyWorkflow",
 125 |     # ... other args
 126 | )
 127 | ```
 128 | 
 129 | ### Step 4: Add Tests
 130 | 
 131 | Create `tests/test_<name>_workflow.py`:
 132 | 
 133 | ```python
 134 | import pytest
 135 | from areal.workflow.<name> import MyWorkflow
 136 | 
 137 | @pytest.mark.asyncio
 138 | async def test_workflow_basic():
 139 |     # Test basic functionality
 140 |     pass
 141 | ```
 142 | 
 143 | ## Reference Implementations
 144 | 
 145 | | Workflow           | File                            | Description                |
 146 | | ------------------ | ------------------------------- | -------------------------- |
 147 | | MultiTurnWorkflow  | `areal/workflow/multi_turn.py`  | Multi-turn conversation    |
 148 | | RLVRWorkflow       | `areal/workflow/rlvr.py`        | RL with verifiable rewards |
 149 | | VisionRLVRWorkflow | `areal/workflow/vision_rlvr.py` | Vision + RLVR              |
 150 | 
 151 | ## Key Requirements
 152 | 
 153 | 1. **Async**: `arun_episode` must be `async def` and non-blocking
 154 | 1. **No sync I/O**: Use `aiofiles` for file operations
 155 | 1. **Wrap rewards**: Use `AsyncRewardWrapper` for reward functions
 156 | 1. **Tensor format**: Output tensors should be `[batch, seq_len, ...]`
 157 | 1. **Use helpers**: `concat_padded_tensors` for combining outputs
 158 | 
 159 | ## Common Mistakes
 160 | 
 161 | - ❌ Using `open()` instead of `aiofiles.open()`
 162 | - ❌ Forgetting to `await` async calls
 163 | - ❌ Not wrapping reward function with `AsyncRewardWrapper`
 164 | - ❌ Wrong tensor shape conventions
 165 | 
 166 | ______________________________________________________________________
 167 | 
 168 | <!--
 169 | ================================================================================
 170 |                             MAINTAINER GUIDE
 171 | ================================================================================
 172 | 
 173 | Location: .claude/skills/add-workflow/SKILL.md
 174 | Invocation: /add-workflow <name>
 175 | 
 176 | ## Purpose
 177 | 
 178 | Step-by-step guide for adding new RolloutWorkflow implementations.
 179 | 
 180 | ## How to Update
 181 | 
 182 | ### When Workflow API Changes
 183 | 1. Update the code template in Step 1
 184 | 2. Update the required imports
 185 | 3. Update the method signature if changed
 186 | 
 187 | ### When New Patterns Emerge
 188 | 1. Add to "Reference Implementations" table
 189 | 2. Update "Key Requirements" if new requirements added
 190 | 
 191 | ================================================================================
 192 | -->
```


---
## .claude/skills/debug-distributed/SKILL.md

```
   1 | ---
   2 | name: debug-distributed
   3 | description: Guide for debugging distributed training issues in AReaL. Use when user encounters hangs, wrong results, OOM, or communication errors.
   4 | ---
   5 | 
   6 | # Debug Distributed Training
   7 | 
   8 | Debugging guide for distributed training issues in AReaL (FSDP2, TP, CP, EP).
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - Training hangs or deadlocks
  15 | - Results differ across ranks or are numerically wrong
  16 | - OOM errors in distributed settings
  17 | - NCCL/communication errors or device mesh issues
  18 | 
  19 | ## Debugging Principles
  20 | 
  21 | ### Minimal Reproduction
  22 | 
  23 | **Always follow the minimal demo principle**: Reproduce with the least amount of code to
  24 | narrow down the issue faster.
  25 | 
  26 | ```python
  27 | # Bad: Debug in full training loop
  28 | # Good: Create minimal script
  29 | import torch
  30 | import torch.distributed as dist
  31 | 
  32 | dist.init_process_group("nccl")
  33 | rank = dist.get_rank()
  34 | 
  35 | # Reproduce the exact operation that fails
  36 | tensor = torch.ones(10).cuda()
  37 | dist.all_reduce(tensor)  # <-- Isolate the failing op
  38 | print(f"Rank {rank}: {tensor}")
  39 | ```
  40 | 
  41 | **Reduction strategy:**
  42 | 
  43 | 1. Remove unrelated model components
  44 | 1. Use small tensor sizes
  45 | 1. Reduce world_size to minimum (e.g., 2 GPUs)
  46 | 1. Remove torch.compile if possible
  47 | 1. Disable activation checkpointing
  48 | 
  49 | ## Step-by-Step Debugging Guide
  50 | 
  51 | ### 1. Hang Debugging (Deadlocks, Synchronization)
  52 | 
  53 | **Environment Variables for Debugging**:
  54 | 
  55 | ```bash
  56 | # Full debug logging
  57 | export TORCH_DISTRIBUTED_DEBUG=DETAIL
  58 | export NCCL_DEBUG=INFO
  59 | export NCCL_DEBUG_SUBSYS=ALL
  60 | 
  61 | # torch.compile debugging
  62 | export TORCH_LOGS="+dynamo,recompiles"
  63 | export TORCHDYNAMO_VERBOSE=1
  64 | ```
  65 | 
  66 | **Dump Call Stack with py-spy** (for hung processes):
  67 | 
  68 | ```bash
  69 | # Find process IDs
  70 | ps aux | grep python
  71 | 
  72 | # Dump call stack of specific rank
  73 | py-spy dump --pid <PID>
  74 | 
  75 | # Record flame graph for performance analysis
  76 | py-spy record -o profile.svg --pid <PID> --duration 30
  77 | ```
  78 | 
  79 | **Common Causes**:
  80 | 
  81 | 1. **Mismatched Collectives**: One rank calls `all_reduce`, another doesn't.
  82 | 1. **Wrong Process Group**: Using wrong group for collective.
  83 | 1. **Tensor Shape Mismatch**: Different shapes across ranks.
  84 | 
  85 | **Debug Steps**:
  86 | 
  87 | ```python
  88 | # Verify group membership
  89 | mesh = parallel_dims.get_mesh("dp_shard_cp")
  90 | group = mesh.get_group()
  91 | print(f"Rank {dist.get_rank()}: group size = {dist.get_world_size(group)}")
  92 | 
  93 | # Print shapes on all ranks
  94 | print(f"Rank {dist.get_rank()}: tensor.shape = {tensor.shape}")
  95 | dist.barrier()
  96 | ```
  97 | 
  98 | **Timeout Adjustment** (for debugging only):
  99 | 
 100 | ```python
 101 | from areal.engine.core.distributed import patch_dist_group_timeout
 102 | from datetime import timedelta
 103 | patch_dist_group_timeout(timedelta(minutes=30))
 104 | ```
 105 | 
 106 | ### 2. Wrong Results (Gradient, Reduction Issues)
 107 | 
 108 | **Check DTensor Placements**:
 109 | 
 110 | ```python
 111 | from torch.distributed.tensor import DTensor
 112 | if isinstance(param, DTensor):
 113 |     print(f"Param {name}: placements={param.placements}, mesh={param.device_mesh}")
 114 | ```
 115 | 
 116 | **Verify Gradient Reduction**:
 117 | 
 118 | ```python
 119 | for name, param in model.named_parameters():
 120 |     if param.grad is not None:
 121 |         print(f"Rank {dist.get_rank()}: {name} grad_sum = {param.grad.sum().item()}")
 122 | ```
 123 | 
 124 | ### 3. OOM Issues (Memory, Sharding)
 125 | 
 126 | **Check Memory Usage**:
 127 | 
 128 | ```python
 129 | print(f"Rank {dist.get_rank()}: "
 130 |       f"allocated={torch.cuda.memory_allocated()/1e9:.2f}GB, "
 131 |       f"reserved={torch.cuda.memory_reserved()/1e9:.2f}GB")
 132 | ```
 133 | 
 134 | **Check FSDP Coverage**:
 135 | 
 136 | ```python
 137 | for name, param in model.named_parameters():
 138 |     is_dtensor = isinstance(param, DTensor)
 139 |     print(f"{name}: is_dtensor={is_dtensor}, shape={param.shape}")
 140 | ```
 141 | 
 142 | ### 4. Communication Errors
 143 | 
 144 | | Error                     | Cause                | Solution                           |
 145 | | ------------------------- | -------------------- | ---------------------------------- |
 146 | | `NCCL WARN Cuda failure`  | GPU communication    | Check NCCL version, GPU topology   |
 147 | | `RuntimeError: Timed out` | Rank synchronization | Increase timeout, check code paths |
 148 | | `Invalid device mesh`     | Mesh configuration   | Verify world_size = dp * tp * cp   |
 149 | 
 150 | ## Debugging Tools
 151 | 
 152 | ### Environment Variables Reference
 153 | 
 154 | | Variable                          | Purpose                                |
 155 | | --------------------------------- | -------------------------------------- |
 156 | | `TORCH_DISTRIBUTED_DEBUG=DETAIL`  | Detailed distributed logging           |
 157 | | `NCCL_DEBUG=INFO`                 | NCCL communication logging             |
 158 | | `NCCL_DEBUG_SUBSYS=ALL`           | All NCCL subsystems                    |
 159 | | `TORCH_LOGS="+dynamo,recompiles"` | torch.compile logging                  |
 160 | | `TORCHDYNAMO_VERBOSE=1`           | Dynamo verbose output                  |
 161 | | `CUDA_LAUNCH_BLOCKING=1`          | Synchronous CUDA (slow, for debugging) |
 162 | 
 163 | ### py-spy for Call Stack Analysis
 164 | 
 165 | ```bash
 166 | # Install
 167 | pip install py-spy
 168 | 
 169 | # Dump call stack of hung process
 170 | py-spy dump --pid <PID>
 171 | 
 172 | # Dump all Python processes
 173 | pgrep -f python | xargs -I {} py-spy dump --pid {}
 174 | 
 175 | # Record flame graph
 176 | py-spy record -o profile.svg --pid <PID> --duration 30
 177 | ```
 178 | 
 179 | ### Rank-Conditional Printing
 180 | 
 181 | ```python
 182 | def print_all_ranks(msg):
 183 |     for r in range(dist.get_world_size()):
 184 |         if dist.get_rank() == r:
 185 |             print(f"[Rank {r}] {msg}")
 186 |         dist.barrier()
 187 | ```
 188 | 
 189 | ### Check Device Mesh
 190 | 
 191 | ```python
 192 | def debug_mesh(parallel_dims):
 193 |     mesh = parallel_dims.world_mesh
 194 |     for dim_name in mesh.mesh_dim_names:
 195 |         submesh = parallel_dims.get_mesh(dim_name)
 196 |         if submesh:
 197 |             print(f"Rank {dist.get_rank()}: {dim_name} size={submesh.size()}")
 198 | ```
 199 | 
 200 | ### Validate Tensor Consistency
 201 | 
 202 | ```python
 203 | def check_tensor_consistency(tensor, name, group=None):
 204 |     local_sum = tensor.sum().item()
 205 |     tensor_sums = [None] * dist.get_world_size(group)
 206 |     dist.all_gather_object(tensor_sums, local_sum, group=group)
 207 |     if dist.get_rank() == 0 and len(set(tensor_sums)) > 1:
 208 |         print(f"WARNING: {name} inconsistent: {tensor_sums}")
 209 | ```
 210 | 
 211 | ## Key Files Reference
 212 | 
 213 | | Component       | File                                                          |
 214 | | --------------- | ------------------------------------------------------------- |
 215 | | Parallel Dims   | `areal/experimental/models/archon/parallel_dims.py`           |
 216 | | Expert Parallel | `areal/experimental/models/archon/expert_parallel.py`         |
 217 | | Ulysses (CP)    | `areal/experimental/models/archon/ulysses.py`                 |
 218 | | FSDP/TP Apply   | `areal/experimental/models/archon/qwen2/infra/parallelize.py` |
 219 | 
 220 | ______________________________________________________________________
 221 | 
 222 | <!--
 223 | ================================================================================
 224 |                             MAINTAINER GUIDE
 225 | ================================================================================
 226 | 
 227 | Location: .claude/skills/debug-distributed/SKILL.md
 228 | Invocation: /debug-distributed
 229 | 
 230 | ## Purpose
 231 | 
 232 | Debugging guide for distributed training issues.
 233 | Covers FSDP2, Tensor Parallelism, Context Parallelism, and Expert Parallelism.
 234 | 
 235 | ## How to Update
 236 | 
 237 | ### When Adding New Parallelism Features
 238 | 1. Add section for the parallelism type
 239 | 2. Document common error patterns and debugging snippets
 240 | 
 241 | ### When PyTorch Distributed APIs Change
 242 | 1. Update DTensor/DeviceMesh examples
 243 | 2. Update environment variable references
 244 | 
 245 | ### When New Error Patterns Emerge
 246 | 1. Add to "Common Errors and Solutions" table
 247 | 2. Reference relevant source files
 248 | 
 249 | ================================================================================
 250 | -->
```


---
## .opencode/skills/add-archon-model/SKILL.md

```
   1 | ---
   2 | name: add-archon-model
   3 | description: Guide for adding a new model to the Archon engine. Use when user wants to add support for a new HuggingFace model architecture in ArchonEngine.
   4 | ---
   5 | 
   6 | # Add Archon Model
   7 | 
   8 | Add support for a new HuggingFace model architecture in the Archon training engine.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add a model to Archon?"
  15 | - User wants to support a new model family (e.g., Llama, Mistral, DeepSeek) in
  16 |   ArchonEngine
  17 | - User mentions adding a new `ModelSpec` or model type for Archon
  18 | 
  19 | ## Prerequisites
  20 | 
  21 | Before starting, ensure:
  22 | 
  23 | - The target model is available on HuggingFace (has `config.json` with `model_type`)
  24 | - You know the HuggingFace model ID (e.g., `meta-llama/Llama-3-8B`)
  25 | - The model uses a standard transformer architecture (decoder-only)
  26 | 
  27 | ## Step-by-Step Guide
  28 | 
  29 | ### Step 1: Analyze the Target Model Architecture
  30 | 
  31 | Read the HuggingFace model's source code to extract key architecture information.
  32 | 
  33 | **Action**: Fetch and analyze the model's HuggingFace configuration and modeling files.
  34 | 
  35 | 1. Read the model's `config.json` (via `AutoConfig.from_pretrained`) to identify:
  36 | 
  37 |    - `model_type` string (this is the key used for registry lookup)
  38 |    - All architecture hyperparameters (hidden_size, num_layers, etc.)
  39 |    - Any model-specific fields (e.g., `qk_norm`, `attention_bias`, MoE fields)
  40 | 
  41 | 1. Read the HuggingFace `modeling_*.py` source to identify:
  42 | 
  43 |    - **Attention variant**: Does it have Q/K norm? Attention bias? Sliding window?
  44 |      Multi-latent attention?
  45 |    - **FFN variant**: SwiGLU (gate_proj + up_proj + down_proj)? GeGLU? Standard MLP?
  46 |    - **MoE support**: Does it have MoE layers? What router type? Shared experts?
  47 |    - **RoPE variant**: Standard RoPE? YaRN? NTK-aware scaling? What is the inv_freq
  48 |      formula?
  49 |    - **Normalization**: RMSNorm or LayerNorm? Pre-norm or post-norm? Elementwise affine?
  50 |    - **Weight tying**: Does `tie_word_embeddings` appear in config?
  51 |    - **State dict key names**: What are the HF weight key naming conventions?
  52 | 
  53 | 1. Summarize findings in a checklist like:
  54 | 
  55 | ```
  56 | Target model: <name>
  57 | HF model_type: "<model_type>" (and variants like "<model_type>_moe" if applicable)
  58 | Attention: [standard GQA / with QK norm / with bias / sliding window / ...]
  59 | FFN: [SwiGLU / GeGLU / standard MLP / ...]
  60 | MoE: [no / yes - num_experts, top_k, shared_experts]
  61 | RoPE: [standard / YaRN / NTK-aware / ...]
  62 | Norm: [RMSNorm / LayerNorm] with [pre-norm / post-norm]
  63 | Weight tying: [yes / no]
  64 | ```
  65 | 
  66 | ### Step 2: Select the Reference Model
  67 | 
  68 | Choose the closest existing implementation as a starting point:
  69 | 
  70 | | Target characteristics               | Reference | Why                                     |
  71 | | ------------------------------------ | --------- | --------------------------------------- |
  72 | | Dense-only, standard GQA, no QK norm | `qwen2`   | Simplest baseline, pure dense           |
  73 | | Has QK norm, or has MoE support      | `qwen3`   | Supports QK norm + MoE + shared experts |
  74 | 
  75 | **Action**: Copy the reference model directory as the starting point:
  76 | 
  77 | ```
  78 | areal/experimental/models/archon/<model>/
  79 |   __init__.py
  80 |   spec.py
  81 |   model/
  82 |     args.py
  83 |     model.py
  84 |     rope.py
  85 |     state_dict_adapter.py
  86 |   infra/
  87 |     parallelize.py
  88 | ```
  89 | 
  90 | ### Step 3: Implement `args.py`
  91 | 
  92 | Adapt `<Model>ModelArgs` to match the target model's HuggingFace config fields.
  93 | 
  94 | **Key changes from reference**:
  95 | 
  96 | 1. Update the `@dataclass` fields to match the target model's hyperparameters:
  97 | 
  98 |    - Field names should use Archon conventions (`dim`, `n_layers`, `n_heads`,
  99 |      `n_kv_heads`, `vocab_size`, `head_dim`, `hidden_dim`, `norm_eps`, `rope_theta`,
 100 |      etc.)
 101 |    - Default values should match the smallest variant of the target model
 102 |    - Add model-specific fields (e.g., `attention_bias`, `qk_norm`, `sliding_window`)
 103 | 
 104 | 1. Update `from_hf_config()` to correctly map HuggingFace config attributes:
 105 | 
 106 |    - Use `getattr(hf_config, "field_name", default)` for optional fields
 107 |    - Handle variant-specific fields (e.g., MoE fields only present in MoE variants)
 108 |    - The method must return an instance of the model args class
 109 | 
 110 | **Critical**: Verify every field mapping against the HF model's `config.json`. Incorrect
 111 | mappings here cause silent errors downstream.
 112 | 
 113 | **Base class contract** (`BaseModelArgs`):
 114 | 
 115 | ```python
 116 | @dataclass
 117 | class <Model>ModelArgs(BaseModelArgs):
 118 |     # ... model-specific fields ...
 119 | 
 120 |     @classmethod
 121 |     def from_hf_config(
 122 |         cls,
 123 |         hf_config: PretrainedConfig,
 124 |         is_critic: bool = False,
 125 |         **kwargs,
 126 |     ) -> <Model>ModelArgs:
 127 |         # Map HF config fields to Archon model args
 128 |         ...
 129 | ```
 130 | 
 131 | ### Step 4: Implement `model.py`
 132 | 
 133 | Adapt the model architecture to match the target model.
 134 | 
 135 | **Key components to adapt**:
 136 | 
 137 | 1. **Normalization** (`RMSNorm` or similar):
 138 | 
 139 |    - Check if `elementwise_affine` is configurable
 140 |    - Check the epsilon default value
 141 |    - If the model uses `LayerNorm`, implement accordingly
 142 | 
 143 | 1. **Attention** module:
 144 | 
 145 |    - Q/K/V projection: Check bias presence (`nn.Linear(..., bias=True/False)`)
 146 |    - QK norm: Add `q_norm`/`k_norm` if the model has them, remove if it doesn't
 147 |    - GQA: `n_kv_heads` \< `n_heads` for grouped-query attention
 148 |    - Ulysses SP: Keep the `set_cp_group` / `_sp_enabled` pattern from the reference
 149 |    - Output projection: Check bias presence
 150 | 
 151 | 1. **FeedForward** module:
 152 | 
 153 |    - SwiGLU: `w2(silu(w1(x)) * w3(x))` -- most common for modern LLMs
 154 |    - Check bias in linear layers
 155 |    - For MoE models: `MoE` module replaces `FeedForward` on designated layers
 156 | 
 157 | 1. **TransformerBlock**: Pre-norm (most modern LLMs) vs post-norm
 158 | 
 159 |    - MoE layer detection via `_is_moe_layer()` if applicable
 160 | 
 161 | 1. **Top-level Model** (`<Model>Model(BaseArchonModel)`):
 162 | 
 163 |    - `tok_embeddings`, `layers` (as `ModuleDict`), `norm`, `output`/`score`
 164 |    - `init_weights()`: Match initialization scheme from HF
 165 |    - `init_buffers()`: RoPE cache + MoE buffers
 166 |    - `forward()`: Must follow `BaseArchonModel` signature:
 167 |      `(tokens, positions, cu_seqlens, max_seqlen, tree_attn_meta=None) -> Tensor`
 168 | 
 169 | **Base class contract** (`BaseArchonModel`):
 170 | 
 171 | ```python
 172 | class <Model>Model(BaseArchonModel):
 173 |     def forward(self, tokens, positions, cu_seqlens, max_seqlen, tree_attn_meta=None) -> torch.Tensor: ...
 174 |     def init_weights(self) -> None: ...
 175 |     def init_buffers(self, buffer_device) -> None: ...
 176 | ```
 177 | 
 178 | ### Step 5: Implement `rope.py`
 179 | 
 180 | Handle the rotary position embedding variant.
 181 | 
 182 | **Options**:
 183 | 
 184 | 1. **Standard RoPE** (same as qwen2/qwen3): Re-export from qwen2:
 185 | 
 186 |    ```python
 187 |    from areal.experimental.models.archon.qwen2.model.rope import (
 188 |        apply_rotary_emb,
 189 |        precompute_rope_cache,
 190 |        repeat_kv,
 191 |        reshape_for_broadcast,
 192 |        rotate_half,
 193 |    )
 194 |    ```
 195 | 
 196 | 1. **Custom RoPE** (YaRN, NTK-aware, etc.): Implement custom `precompute_rope_cache()`
 197 |    and `apply_rotary_emb()` functions. The key difference is usually in how `inv_freq`
 198 |    is computed (scaling factors, interpolation, etc.).
 199 | 
 200 | ### Step 6: Implement `state_dict_adapter.py`
 201 | 
 202 | Map between HuggingFace and Archon weight key names.
 203 | 
 204 | **This is the most error-prone step.** The adapter must correctly handle:
 205 | 
 206 | 1. **Key name mapping** (`from_hf_map` dict):
 207 | 
 208 |    - Embedding: `model.embed_tokens.weight` -> `tok_embeddings.weight`
 209 |    - Attention: `model.layers.{}.self_attn.q_proj.weight` ->
 210 |      `layers.{}.attention.wq.weight`
 211 |    - FFN: `model.layers.{}.mlp.gate_proj.weight` -> `layers.{}.feed_forward.w1.weight`
 212 |    - Norms: `model.layers.{}.input_layernorm.weight` ->
 213 |      `layers.{}.attention_norm.weight`
 214 |    - Output: `lm_head.weight` -> `output.weight`
 215 |    - Skip keys (set to `None`): `rotary_emb.inv_freq` (computed at runtime)
 216 |    - Model-specific keys: bias terms, QK norm weights, etc.
 217 | 
 218 | 1. **Reverse mapping** (`to_hf_map`): Auto-generated from `from_hf_map`
 219 | 
 220 | 1. **MoE expert weights** (if applicable): 3D\<->2D conversion for expert weights. Copy
 221 |    the MoE handling from qwen3 if the model has MoE.
 222 | 
 223 | 1. **Weight tying**: Skip `output.weight` during `to_hf()` if `tie_word_embeddings=True`
 224 | 
 225 | **Verification approach**: After implementation, the adapter should satisfy:
 226 | 
 227 | ```python
 228 | # Roundtrip: archon -> hf -> archon preserves all keys
 229 | hf_sd = adapter.to_hf(archon_sd)
 230 | roundtrip_sd = adapter.from_hf(hf_sd)
 231 | assert set(roundtrip_sd.keys()) == set(archon_sd.keys())
 232 | ```
 233 | 
 234 | **Base class contract** (`BaseStateDictAdapter`):
 235 | 
 236 | ```python
 237 | class <Model>StateDictAdapter(BaseStateDictAdapter):
 238 |     def from_hf(self, hf_state_dict) -> dict[str, Any]: ...
 239 |     def to_hf(self, archon_state_dict) -> dict[str, Any]: ...
 240 |     def convert_single_to_hf(self, name, tensor) -> list[tuple[str, torch.Tensor]]: ...
 241 | ```
 242 | 
 243 | ### Step 7: Implement `parallelize.py`
 244 | 
 245 | Define the parallelization strategy for the model.
 246 | 
 247 | **The parallelize function** applies parallelism in this order:
 248 | 
 249 | 1. TP (Tensor Parallelism) -- shard attention/FFN across devices
 250 | 1. EP (Expert Parallelism) -- for MoE models only
 251 | 1. CP (Context Parallelism / Ulysses SP) -- sequence parallelism
 252 | 1. AC (Activation Checkpointing) -- memory optimization
 253 | 1. torch.compile -- compilation optimization
 254 | 1. FSDP (Fully Sharded Data Parallelism) -- data parallelism
 255 | 
 256 | **Key adaptations by model architecture**:
 257 | 
 258 | - **Attention with QK norm**: wq/wk use `use_local_output=False` (DTensor output for
 259 |   norm), add `SequenceParallel(sequence_dim=2)` for q_norm/k_norm
 260 | - **Attention without QK norm**: wq/wk/wv all use `use_local_output=True`
 261 | - **Attention with bias**: Bias terms follow the same parallel plan as their weights
 262 | - **MoE layers**: Separate TP plan for MoE input/output, router gate, and expert
 263 |   weights. Copy from qwen3's `apply_moe_ep_tp()` and `apply_non_moe_tp()`
 264 | - **Dense-only models**: Simpler plan without MoE handling. Copy from qwen2
 265 | 
 266 | **Function signature** (must match `ParallelizeFn` protocol):
 267 | 
 268 | ```python
 269 | def parallelize_<model>(
 270 |     model: nn.Module,
 271 |     parallel_dims: ArchonParallelDims,
 272 |     param_dtype: torch.dtype = torch.bfloat16,
 273 |     reduce_dtype: torch.dtype = torch.float32,
 274 |     loss_parallel: bool = True,
 275 |     cpu_offload: bool = False,
 276 |     reshard_after_forward_policy: str = "default",
 277 |     ac_config: ActivationCheckpointConfig | None = None,
 278 |     enable_compile: bool = True,
 279 | ) -> nn.Module:
 280 | ```
 281 | 
 282 | ### Step 8: Create `spec.py` and Register
 283 | 
 284 | Assemble the `ModelSpec` and register it.
 285 | 
 286 | ```python
 287 | from areal.experimental.models.archon.model_spec import ModelSpec, register_model_spec
 288 | from areal.experimental.models.archon.pipeline_parallel import pipeline_llm
 289 | from areal.experimental.models.archon.<model>.infra.parallelize import parallelize_<model>
 290 | from areal.experimental.models.archon.<model>.model.args import <Model>ModelArgs
 291 | from areal.experimental.models.archon.<model>.model.model import <Model>Model
 292 | from areal.experimental.models.archon.<model>.model.state_dict_adapter import (
 293 |     <Model>StateDictAdapter,
 294 | )
 295 | 
 296 | <MODEL>_SPEC = ModelSpec(
 297 |     name="<Model>",
 298 |     model_class=<Model>Model,
 299 |     model_args_class=<Model>ModelArgs,
 300 |     state_dict_adapter_class=<Model>StateDictAdapter,
 301 |     parallelize_fn=parallelize_<model>,
 302 |     supported_model_types=frozenset({"<model_type>"}),  # From HF config.json
 303 |     pipelining_fn=pipeline_llm,
 304 | )
 305 | 
 306 | # Auto-register when module is imported
 307 | register_model_spec(<MODEL>_SPEC)
 308 | 
 309 | __all__ = ["<MODEL>_SPEC"]
 310 | ```
 311 | 
 312 | **Note**: `supported_model_types` should include all HF `model_type` strings that this
 313 | implementation handles (e.g., `{"qwen3", "qwen3_moe"}` for Qwen3).
 314 | 
 315 | ### Step 9: Register in `__init__.py`
 316 | 
 317 | Add the import to `areal/experimental/models/archon/__init__.py`:
 318 | 
 319 | ```python
 320 | from areal.experimental.models.archon.<model> import spec as <model>_spec  # noqa: F401
 321 | ```
 322 | 
 323 | This triggers auto-registration when the module is imported.
 324 | 
 325 | ### Step 10: Verify and Test
 326 | 
 327 | Verification should be done in stages, adapting based on available hardware and the test
 328 | patterns in `tests/experimental/archon/`.
 329 | 
 330 | **Before writing tests**, examine the existing test files to understand current
 331 | patterns:
 332 | 
 333 | ```
 334 | tests/experimental/archon/
 335 |   conftest.py             -- Pytest configuration (version checks)
 336 |   utils.py                -- Shared utilities (model loading, comparison)
 337 |   test_qwen3_args.py      -- Args unit tests (CPU-only)
 338 |   test_state_dict_adapter.py  -- State dict roundtrip tests
 339 |   test_weight_sync.py     -- Weight completeness tests (meta device)
 340 |   test_forward.py         -- Forward precision comparison (single GPU)
 341 |   ...
 342 | ```
 343 | 
 344 | **Test stages** (write tests appropriate for the model's complexity):
 345 | 
 346 | #### Stage 1: Args Tests (CPU-only, always write these)
 347 | 
 348 | Test `from_hf_config()` with mock HuggingFace configs:
 349 | 
 350 | ```python
 351 | # Pattern: Create mock PretrainedConfig, verify args mapping
 352 | from unittest.mock import MagicMock
 353 | 
 354 | def test_args_from_hf_config():
 355 |     hf_config = MagicMock()
 356 |     hf_config.hidden_size = 4096
 357 |     hf_config.num_hidden_layers = 32
 358 |     # ... set all required fields
 359 |     args = <Model>ModelArgs.from_hf_config(hf_config)
 360 |     assert args.dim == 4096
 361 |     assert args.n_layers == 32
 362 | ```
 363 | 
 364 | #### Stage 2: State Dict Adapter Tests (CPU-only)
 365 | 
 366 | Test key mapping roundtrip:
 367 | 
 368 | ```python
 369 | def test_state_dict_roundtrip():
 370 |     # Create adapter with mock config
 371 |     adapter = <Model>StateDictAdapter(mock_config)
 372 |     # Create fake archon state dict with expected keys
 373 |     archon_sd = {"tok_embeddings.weight": torch.randn(vocab, dim), ...}
 374 |     # Roundtrip
 375 |     hf_sd = adapter.to_hf(archon_sd)
 376 |     roundtrip = adapter.from_hf(hf_sd)
 377 |     assert set(roundtrip.keys()) == set(archon_sd.keys())
 378 | ```
 379 | 
 380 | #### Stage 3: Weight Completeness (meta device, CPU-only)
 381 | 
 382 | Verify all model parameters have HF mappings:
 383 | 
 384 | ```python
 385 | def test_weight_completeness():
 386 |     # Create model on meta device
 387 |     with torch.device("meta"):
 388 |         model = <Model>Model(args)
 389 |     adapter = <Model>StateDictAdapter(hf_config)
 390 |     # Check every archon param has a HF mapping
 391 |     for name, _ in model.named_parameters():
 392 |         hf_pairs = adapter.convert_single_to_hf(name, torch.empty(0))
 393 |         assert len(hf_pairs) > 0, f"No HF mapping for {name}"
 394 | ```
 395 | 
 396 | #### Stage 4: Forward Precision (single GPU, if available)
 397 | 
 398 | Compare Archon model output against HuggingFace reference:
 399 | 
 400 | ```python
 401 | @pytest.mark.skipif(not torch.cuda.is_available(), reason="Requires CUDA")
 402 | def test_forward_matches_hf():
 403 |     # Load both HF and Archon models
 404 |     # Run forward on same input
 405 |     # Compare logits within tolerance
 406 | ```
 407 | 
 408 | **Important**: Do NOT hardcode the test categories. Inspect the existing test files in
 409 | `tests/experimental/archon/` and follow the same patterns, fixtures, and markers. Adapt
 410 | test scope to the model's specific features (e.g., add MoE-specific tests only if the
 411 | model has MoE).
 412 | 
 413 | ## Reference Implementations
 414 | 
 415 | | Model | Directory                                 | Features                                                |
 416 | | ----- | ----------------------------------------- | ------------------------------------------------------- |
 417 | | Qwen2 | `areal/experimental/models/archon/qwen2/` | Dense, attention bias, no QK norm                       |
 418 | | Qwen3 | `areal/experimental/models/archon/qwen3/` | Dense + MoE, QK norm, no attention bias, shared experts |
 419 | 
 420 | ## Architecture Decision Map
 421 | 
 422 | | Feature             | qwen2    | qwen3                      | What to check in target model                            |
 423 | | ------------------- | -------- | -------------------------- | -------------------------------------------------------- |
 424 | | Attention bias      | Yes      | No                         | `attention_bias` in HF config                            |
 425 | | QK norm             | No       | Yes                        | `qk_norm` in HF config or QKNorm module in modeling file |
 426 | | MoE                 | No       | Yes                        | `num_experts`/`num_local_experts` in HF config           |
 427 | | Shared experts      | No       | Yes                        | `num_shared_experts` in HF config                        |
 428 | | Decoder sparse step | No       | Yes                        | `decoder_sparse_step` in HF config                       |
 429 | | Weight tying        | Both     | Both                       | `tie_word_embeddings` in HF config                       |
 430 | | RoPE                | Standard | Standard (re-export qwen2) | Check inv_freq formula in HF modeling code               |
 431 | 
 432 | ## Common Mistakes
 433 | 
 434 | - Not mapping all HF keys in `state_dict_adapter.py` (causes silent weight drops)
 435 | - Wrong `from_hf_config()` field mapping (uses wrong HF config attribute name)
 436 | - Forgetting to handle `None` keys in `from_hf_map` (keys to skip like
 437 |   `rotary_emb.inv_freq`)
 438 | - Missing MoE expert weight 3D\<->2D conversion when model has MoE
 439 | - Wrong TP plan for attention with/without QK norm (`use_local_output` must match)
 440 | - Forgetting to add import line in `areal/experimental/models/archon/__init__.py`
 441 | - Not including all `model_type` variants in `supported_model_types` frozenset
 442 | - Using `print` instead of `areal.utils.logging.getLogger()`
 443 | 
 444 | ## File Checklist
 445 | 
 446 | After completion, verify all files exist and are consistent:
 447 | 
 448 | - [ ] `areal/experimental/models/archon/<model>/__init__.py`
 449 | - [ ] `areal/experimental/models/archon/<model>/spec.py` -- ModelSpec + register
 450 | - [ ] `areal/experimental/models/archon/<model>/model/args.py` -- ModelArgs +
 451 |   from_hf_config
 452 | - [ ] `areal/experimental/models/archon/<model>/model/model.py` -- Model + Attention +
 453 |   FFN
 454 | - [ ] `areal/experimental/models/archon/<model>/model/rope.py` -- RoPE (or re-export)
 455 | - [ ] `areal/experimental/models/archon/<model>/model/state_dict_adapter.py` -- Key
 456 |   mapping
 457 | - [ ] `areal/experimental/models/archon/<model>/infra/parallelize.py` -- Parallel
 458 |   strategy
 459 | - [ ] `areal/experimental/models/archon/__init__.py` -- Import line added
 460 | - [ ] `tests/experimental/archon/test_<model>_*.py` -- Tests
 461 | 
 462 | ______________________________________________________________________
 463 | 
 464 | <!--
 465 | ================================================================================
 466 |                             MAINTAINER GUIDE
 467 | ================================================================================
 468 | 
 469 | Location: .opencode/skills/add-archon-model/SKILL.md
 470 | Invocation: /add-archon-model <model_name>
 471 | 
 472 | ## Purpose
 473 | 
 474 | Semi-automated guide for adding new model architectures to the Archon training engine.
 475 | Unlike simpler skills (add-reward, add-dataset), this skill actively guides Claude to:
 476 | 1. Analyze HuggingFace source code to extract architecture details
 477 | 2. Select the closest reference implementation (qwen2 or qwen3)
 478 | 3. Generate code skeletons adapted to the target architecture
 479 | 4. Create appropriate tests based on existing test patterns
 480 | 
 481 | ## How to Update
 482 | 
 483 | ### When New Reference Models Are Added
 484 | 1. Add to "Reference Implementations" table
 485 | 2. Update "Architecture Decision Map" with new feature columns
 486 | 3. Update Step 2 (reference selection) with new options
 487 | 
 488 | ### When Base Classes Change
 489 | 1. Update contract signatures in Steps 3, 4, 6, 7
 490 | 2. Update file checklist if new files are required
 491 | 
 492 | ### When ModelSpec Changes
 493 | 1. Update Step 8 with new ModelSpec fields
 494 | 2. Update spec.py template
 495 | 
 496 | ### When Test Patterns Change
 497 | 1. Update Step 10 with new test patterns
 498 | 2. Do NOT hardcode test categories -- keep it flexible
 499 | 
 500 | ### Important Design Decisions
 501 | - This skill is SEMI-AUTOMATED: Claude should read HF source and generate code,
 502 |   not just provide templates for the user to fill in manually
 503 | - The skill references existing test files rather than hardcoding test categories,
 504 |   ensuring it stays current as the test suite evolves
 505 | - Reference model selection (qwen2 vs qwen3) is based on MoE and QK norm presence
 506 | 
 507 | ================================================================================
 508 | -->
```


---
## .opencode/skills/add-dataset/SKILL.md

```
   1 | ---
   2 | name: add-dataset
   3 | description: Guide for adding a new dataset loader to AReaL. Use when user wants to add a new dataset.
   4 | ---
   5 | 
   6 | # Add Dataset
   7 | 
   8 | Add a new dataset loader to AReaL.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add a dataset?"
  15 | - User wants to integrate a new dataset
  16 | - User mentions creating a dataset loader
  17 | 
  18 | ## Step-by-Step Guide
  19 | 
  20 | ### Step 1: Create Dataset File
  21 | 
  22 | Create `areal/dataset/<name>.py`:
  23 | 
  24 | ```python
  25 | from datasets import Dataset, load_dataset
  26 | 
  27 | 
  28 | def get_<name>_sft_dataset(
  29 |     path: str,
  30 |     split: str,
  31 |     tokenizer,
  32 |     max_length: int | None = None,
  33 | ) -> Dataset:
  34 |     """Load dataset for SFT training.
  35 | 
  36 |     Args:
  37 |         path: Path to dataset (HuggingFace hub or local path)
  38 |         split: Dataset split (train/validation/test)
  39 |         tokenizer: Tokenizer for processing
  40 |         max_length: Maximum sequence length (optional)
  41 | 
  42 |     Returns:
  43 |         HuggingFace Dataset with processed samples
  44 |     """
  45 |     dataset = load_dataset(path=path, split=split)
  46 | 
  47 |     def process(sample):
  48 |         # Tokenize the full sequence (prompt + response)
  49 |         seq_token = tokenizer.encode(
  50 |             sample["question"] + sample["answer"] + tokenizer.eos_token
  51 |         )
  52 |         prompt_token = tokenizer.encode(sample["question"])
  53 |         # Loss mask: 0 for prompt, 1 for response
  54 |         loss_mask = [0] * len(prompt_token) + [1] * (len(seq_token) - len(prompt_token))
  55 |         return {"input_ids": seq_token, "loss_mask": loss_mask}
  56 | 
  57 |     dataset = dataset.map(process).remove_columns(["question", "answer"])
  58 | 
  59 |     if max_length is not None:
  60 |         dataset = dataset.filter(lambda x: len(x["input_ids"]) <= max_length)
  61 | 
  62 |     return dataset
  63 | 
  64 | 
  65 | def get_<name>_rl_dataset(
  66 |     path: str,
  67 |     split: str,
  68 |     tokenizer,
  69 |     max_length: int | None = None,
  70 | ) -> Dataset:
  71 |     """Load dataset for RL training.
  72 | 
  73 |     Args:
  74 |         path: Path to dataset
  75 |         split: Dataset split
  76 |         tokenizer: Tokenizer for length filtering
  77 |         max_length: Maximum sequence length
  78 | 
  79 |     Returns:
  80 |         HuggingFace Dataset with prompts and answers for reward computation
  81 |     """
  82 |     dataset = load_dataset(path=path, split=split)
  83 | 
  84 |     def process(sample):
  85 |         messages = [
  86 |             {
  87 |                 "role": "user",
  88 |                 "content": sample["question"],
  89 |             }
  90 |         ]
  91 |         return {"messages": messages, "answer": sample["answer"]}
  92 | 
  93 |     dataset = dataset.map(process).remove_columns(["question"])
  94 | 
  95 |     if max_length is not None:
  96 | 
  97 |         def filter_length(sample):
  98 |             content = sample["messages"][0]["content"]
  99 |             tokens = tokenizer.encode(content)
 100 |             return len(tokens) <= max_length
 101 | 
 102 |         dataset = dataset.filter(filter_length)
 103 | 
 104 |     return dataset
 105 | ```
 106 | 
 107 | ### Step 2: Register in __init__.py
 108 | 
 109 | Update `areal/dataset/__init__.py`:
 110 | 
 111 | ```python
 112 | # Add to VALID_DATASETS
 113 | VALID_DATASETS = [
 114 |     # ... existing datasets
 115 |     "<name>",
 116 | ]
 117 | 
 118 | # Add to _get_custom_dataset function
 119 | def _get_custom_dataset(name: str, ...):
 120 |     # ... existing code
 121 |     elif name == "<name>":
 122 |         from areal.dataset.<name> import get_<name>_sft_dataset, get_<name>_rl_dataset
 123 |         if dataset_type == "sft":
 124 |             return get_<name>_sft_dataset(path, split, max_length, tokenizer)
 125 |         else:
 126 |             return get_<name>_rl_dataset(path, split, max_length, tokenizer)
 127 | ```
 128 | 
 129 | ### Step 3: Add Config (Optional)
 130 | 
 131 | If the dataset needs special configuration, add to `areal/api/cli_args.py`:
 132 | 
 133 | ```python
 134 | @dataclass
 135 | class TrainDatasetConfig:
 136 |     # ... existing fields
 137 |     <name>_specific_field: Optional[str] = None
 138 | ```
 139 | 
 140 | ### Step 4: Add Tests
 141 | 
 142 | Create `tests/test_<name>_dataset.py`:
 143 | 
 144 | ```python
 145 | import pytest
 146 | from areal.dataset.<name> import get_<name>_sft_dataset, get_<name>_rl_dataset
 147 | 
 148 | def test_sft_dataset_loads(tokenizer):
 149 |     dataset = get_<name>_sft_dataset("path/to/data", split="train", tokenizer=tokenizer)
 150 |     assert len(dataset) > 0
 151 |     assert "input_ids" in dataset.column_names
 152 |     assert "loss_mask" in dataset.column_names
 153 | 
 154 | def test_rl_dataset_loads(tokenizer):
 155 |     dataset = get_<name>_rl_dataset("path/to/data", split="train", tokenizer=tokenizer)
 156 |     assert len(dataset) > 0
 157 |     assert "messages" in dataset.column_names
 158 |     assert "answer" in dataset.column_names
 159 | ```
 160 | 
 161 | ## Reference Implementations
 162 | 
 163 | | Dataset    | File                               | Description              |
 164 | | ---------- | ---------------------------------- | ------------------------ |
 165 | | GSM8K      | `areal/dataset/gsm8k.py`           | Math word problems       |
 166 | | Geometry3K | `areal/dataset/geometry3k.py`      | Geometry problems        |
 167 | | CLEVR      | `areal/dataset/clevr_count_70k.py` | Visual counting          |
 168 | | HH-RLHF    | `areal/dataset/hhrlhf.py`          | Helpfulness/Harmlessness |
 169 | | TORL       | `areal/dataset/torl_data.py`       | Tool-use RL              |
 170 | 
 171 | ## Required Fields
 172 | 
 173 | ### SFT Dataset
 174 | 
 175 | ```python
 176 | {
 177 |     "messages": [
 178 |         {"role": "user", "content": "..."},
 179 |         {"role": "assistant", "content": "..."},
 180 |     ]
 181 | }
 182 | ```
 183 | 
 184 | ### RL Dataset
 185 | 
 186 | ```python
 187 | {
 188 |     "messages": [
 189 |         {"role": "user", "content": "..."},
 190 |     ],
 191 |     "answer": "ground_truth_for_reward",
 192 |     # Optional metadata for reward function
 193 | }
 194 | ```
 195 | 
 196 | ## Common Mistakes
 197 | 
 198 | - Returning `List[Dict]` instead of HuggingFace `Dataset`
 199 | - Using Python loops instead of `dataset.map()`/`filter()`
 200 | - Missing `"messages"` field for RL datasets
 201 | - Wrong message format (should be list of dicts with `role` and `content`)
 202 | - Not registering in `__init__.py`
 203 | 
 204 | ______________________________________________________________________
 205 | 
 206 | <!--
 207 | ================================================================================
 208 |                             MAINTAINER GUIDE
 209 | ================================================================================
 210 | 
 211 | Location: .opencode/skills/add-dataset/SKILL.md
 212 | Invocation: /add-dataset <name>
 213 | 
 214 | ## Purpose
 215 | 
 216 | Step-by-step guide for adding new dataset loaders.
 217 | 
 218 | ## How to Update
 219 | 
 220 | ### When Dataset API Changes
 221 | 1. Update the code templates
 222 | 2. Update required fields section
 223 | 3. Update registration example
 224 | 
 225 | ### When New Dataset Types Added
 226 | 1. Add to "Reference Implementations" table
 227 | 2. Add any new required fields
 228 | 
 229 | ================================================================================
 230 | -->
```


---
## .opencode/skills/add-reward/SKILL.md

```
   1 | ---
   2 | name: add-reward
   3 | description: Guide for adding a new reward function to AReaL. Use when user wants to create a reward function.
   4 | ---
   5 | 
   6 | # Add Reward
   7 | 
   8 | Add a new reward function to AReaL.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add a reward function?"
  15 | - User wants to implement custom rewards
  16 | - User mentions reward computation
  17 | 
  18 | ## Step-by-Step Guide
  19 | 
  20 | ### Step 1: Create Reward File
  21 | 
  22 | Create `areal/reward/<name>.py`:
  23 | 
  24 | ```python
  25 | from typing import Any
  26 | 
  27 | from areal.utils import logging
  28 | 
  29 | logger = logging.getLogger("MyReward")
  30 | 
  31 | 
  32 | def <name>_reward_fn(
  33 |     prompt: str,
  34 |     completions: str,
  35 |     prompt_ids,
  36 |     completion_ids,
  37 |     answer: str | None = None,
  38 |     **kwargs: Any,
  39 | ) -> float:
  40 |     """Compute reward for a single completion.
  41 | 
  42 |     Args:
  43 |         prompt: Prompt string
  44 |         completions: Completion string (model output)
  45 |         prompt_ids: Tokenized prompt IDs
  46 |         completion_ids: Tokenized completion IDs
  47 |         answer: Ground truth answer from dataset (optional)
  48 |         **kwargs: Additional data from dataset
  49 | 
  50 |     Returns:
  51 |         Reward value (float), typically 0.0 or 1.0
  52 |     """
  53 |     try:
  54 |         # Extract answer from completion
  55 |         extracted = _extract_answer(completions)
  56 | 
  57 |         # Compare with ground truth
  58 |         if answer is not None and extracted == str(answer):
  59 |             return 1.0
  60 |         return 0.0
  61 |     except Exception:
  62 |         logger.warning("Exception in reward computation", exc_info=True)
  63 |         return 0.0
  64 | 
  65 | 
  66 | def _extract_answer(completion: str) -> str:
  67 |     """Extract the answer from a completion string.
  68 | 
  69 |     Implement your extraction logic here.
  70 |     """
  71 |     # Example: Extract content from \boxed{}
  72 |     import re
  73 | 
  74 |     match = re.search(r"\\boxed\{([^}]+)\}", completion)
  75 |     if match:
  76 |         return match.group(1).strip()
  77 |     return completion.strip()
  78 | ```
  79 | 
  80 | ### Step 2: Register in __init__.py
  81 | 
  82 | Update `areal/reward/__init__.py`:
  83 | 
  84 | ```python
  85 | # Add to VALID_REWARD_FN
  86 | VALID_REWARD_FN = [
  87 |     # ... existing reward functions
  88 |     "<name>",
  89 | ]
  90 | 
  91 | # Add to get_reward_fn function
  92 | def get_reward_fn(name: str, **kwargs):
  93 |     # ... existing code
  94 |     elif name == "<name>":
  95 |         from areal.reward.<name> import <name>_reward_fn
  96 |         return <name>_reward_fn
  97 | ```
  98 | 
  99 | ### Step 3: Handle Blocking Operations
 100 | 
 101 | If your reward function uses blocking operations (e.g., API calls, model inference), the
 102 | workflow will wrap it with `AsyncRewardWrapper`:
 103 | 
 104 | ```python
 105 | # In your workflow
 106 | from areal.reward import AsyncRewardWrapper
 107 | 
 108 | self.reward_fn = AsyncRewardWrapper(reward_fn)
 109 | 
 110 | # Then call it asynchronously
 111 | rewards = await self.reward_fn(prompt, completions, **data)
 112 | ```
 113 | 
 114 | ### Step 4: Add Tests
 115 | 
 116 | Create `tests/test_<name>_reward.py`:
 117 | 
 118 | ```python
 119 | import pytest
 120 | from areal.reward.<name> import <name>_reward_fn
 121 | 
 122 | def test_reward_correct_answer():
 123 |     reward = <name>_reward_fn(
 124 |         prompt="What is 2+2?",
 125 |         completions="The answer is \\boxed{4}",
 126 |         prompt_ids=None,
 127 |         completion_ids=None,
 128 |         answer="4",
 129 |     )
 130 |     assert reward == 1.0
 131 | 
 132 | def test_reward_wrong_answer():
 133 |     reward = <name>_reward_fn(
 134 |         prompt="What is 2+2?",
 135 |         completions="The answer is \\boxed{5}",
 136 |         prompt_ids=None,
 137 |         completion_ids=None,
 138 |         answer="4",
 139 |     )
 140 |     assert reward == 0.0
 141 | ```
 142 | 
 143 | ## Reference Implementations
 144 | 
 145 | | Reward     | File                              | Description                  |
 146 | | ---------- | --------------------------------- | ---------------------------- |
 147 | | GSM8K      | `areal/reward/gsm8k.py`           | Math answer verification     |
 148 | | Geometry3K | `areal/reward/geometry3k.py`      | Geometry answer verification |
 149 | | CLEVR      | `areal/reward/clevr_count_70k.py` | Counting verification        |
 150 | | MathVerify | `areal/reward/math_verify.py`     | General math verification    |
 151 | 
 152 | ## Function Signature
 153 | 
 154 | All reward functions must follow this signature:
 155 | 
 156 | ```python
 157 | def reward_fn(
 158 |     prompt: str,               # Input prompt string
 159 |     completions: str,          # Model completion string
 160 |     prompt_ids,                # Tokenized prompt
 161 |     completion_ids,            # Tokenized completion
 162 |     **kwargs: Any,             # Additional data from dataset (e.g., answer)
 163 | ) -> float:                    # Reward value (typically 0.0 or 1.0)
 164 | ```
 165 | 
 166 | **Note**: The reward function is called once per sample. Batching is handled by
 167 | `AsyncRewardWrapper` in the workflow.
 168 | 
 169 | ## Key Requirements
 170 | 
 171 | 1. **Deterministic**: Same inputs should produce same outputs
 172 | 1. **Return float**: Output is a single float value per sample
 173 | 1. **No blocking in async context**: Use `AsyncRewardWrapper` if needed
 174 | 1. **Logging**: Use `areal.utils.logging`, not `print`
 175 | 1. **Handle exceptions**: Return 0.0 on error, don't raise
 176 | 
 177 | ## Common Mistakes
 178 | 
 179 | - Returning a tensor instead of a float
 180 | - Expecting batched inputs (reward is called per sample)
 181 | - Non-deterministic behavior
 182 | - Blocking operations without `AsyncRewardWrapper`
 183 | - Raising exceptions instead of returning 0.0
 184 | 
 185 | ______________________________________________________________________
 186 | 
 187 | <!--
 188 | ================================================================================
 189 |                             MAINTAINER GUIDE
 190 | ================================================================================
 191 | 
 192 | Location: .opencode/skills/add-reward/SKILL.md
 193 | Invocation: /add-reward <name>
 194 | 
 195 | ## Purpose
 196 | 
 197 | Step-by-step guide for adding new reward functions.
 198 | 
 199 | ## How to Update
 200 | 
 201 | ### When Reward API Changes
 202 | 1. Update the function signature section
 203 | 2. Update the code template
 204 | 3. Update key requirements
 205 | 
 206 | ### When New Reward Patterns Emerge
 207 | 1. Add to "Reference Implementations" table
 208 | 2. Add examples for new patterns
 209 | 
 210 | ================================================================================
 211 | -->
```


---
## .opencode/skills/add-unit-tests/SKILL.md

```
   1 | ---
   2 | name: add-unit-tests
   3 | description: Guide for adding unit tests to AReaL. Use when user wants to add tests for new functionality or increase test coverage.
   4 | ---
   5 | 
   6 | # Add Unit Tests
   7 | 
   8 | Add unit tests to AReaL following the project's testing conventions.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add tests?"
  15 | - User wants to increase test coverage
  16 | - User needs to write tests for new functionality
  17 | - User wants to understand AReaL testing patterns
  18 | 
  19 | ## Step-by-Step Guide
  20 | 
  21 | ### Step 1: Understand Test Types
  22 | 
  23 | AReaL has two main test categories:
  24 | 
  25 | | Test Type             | Purpose                            | Location Pattern                   | How It Runs                                |
  26 | | --------------------- | ---------------------------------- | ---------------------------------- | ------------------------------------------ |
  27 | | **Unit Tests**        | Test individual functions/modules  | `tests/test_<module>_<feature>.py` | Directly via pytest                        |
  28 | | **Distributed Tests** | Test distributed/parallel behavior | `tests/torchrun/run_*.py`          | Via torchrun (called by pytest subprocess) |
  29 | 
  30 | **Note**: All tests are invoked via pytest. Distributed tests use `torchrun` but are
  31 | still called from pytest test files.
  32 | 
  33 | ### Step 2: Create Test File Structure
  34 | 
  35 | Create test file with naming convention: `test_<module>_<feature>.py`
  36 | 
  37 | ```python
  38 | import pytest
  39 | import torch
  40 | 
  41 | # Import the module to test
  42 | from areal.dataset.gsm8k import get_gsm8k_sft_dataset
  43 | from tests.utils import get_dataset_path  # Optional test utilities
  44 | # For mocking tokenizer: from unittest.mock import MagicMock
  45 | ```
  46 | 
  47 | ### Step 3: Write Test Functions
  48 | 
  49 | Follow Arrange-Act-Assert pattern:
  50 | 
  51 | ```python
  52 | def test_function_under_condition_returns_expected():
  53 |     """Test that function returns expected value under condition."""
  54 |     # Arrange
  55 |     input_data = 5
  56 |     expected_output = 10
  57 | 
  58 |     # Act
  59 |     result = function_under_test(input_data)
  60 | 
  61 |     # Assert
  62 |     assert result == expected_output
  63 | ```
  64 | 
  65 | ### Step 4: Add Pytest Markers and CI Strategy
  66 | 
  67 | Use appropriate pytest markers:
  68 | 
  69 | | Marker                                  | When to Use                                                  |
  70 | | --------------------------------------- | ------------------------------------------------------------ |
  71 | | `@pytest.mark.slow`                     | Test takes > 10 seconds (excluded from CI by default)        |
  72 | | `@pytest.mark.ci`                       | Slow test that must run in CI (use with `@pytest.mark.slow`) |
  73 | | `@pytest.mark.asyncio`                  | Async test functions                                         |
  74 | | `@pytest.mark.skipif(cond, reason=...)` | Conditional skip                                             |
  75 | | `@pytest.mark.parametrize(...)`         | Parameterized tests                                          |
  76 | 
  77 | **CI Test Strategy**:
  78 | 
  79 | - `@pytest.mark.slow`: Excluded from CI by default (CI runs `pytest -m "not slow"`)
  80 | - `@pytest.mark.slow` + `@pytest.mark.ci`: Slow but must run in CI
  81 | - No marker: Runs in CI (fast unit tests)
  82 | 
  83 | ```python
  84 | @pytest.mark.asyncio
  85 | async def test_async_function():
  86 |     result = await async_function()
  87 |     assert result == expected
  88 | 
  89 | @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
  90 | def test_gpu_feature():
  91 |     tensor = torch.tensor([1, 2, 3], device="cuda")
  92 |     # ... assertions
  93 | 
  94 | @pytest.mark.parametrize("batch_size", [1, 4, 16])
  95 | def test_with_parameters(batch_size):
  96 |     # Parameterized test
  97 | 
  98 | @pytest.mark.slow
  99 | def test_slow_function():
 100 |     # Excluded from CI by default
 101 | 
 102 | @pytest.mark.slow
 103 | @pytest.mark.ci
 104 | def test_slow_but_required_in_ci():
 105 |     # Slow but must run in CI
 106 | ```
 107 | 
 108 | ### Step 5: Mock Distributed Environment
 109 | 
 110 | For unit tests that need distributed mocks:
 111 | 
 112 | ```python
 113 | import torch.distributed as dist
 114 | 
 115 | def test_distributed_function(monkeypatch):
 116 |     monkeypatch.setattr(dist, "get_rank", lambda: 0)
 117 |     monkeypatch.setattr(dist, "get_world_size", lambda: 2)
 118 |     result = distributed_function()
 119 |     assert result == expected
 120 | ```
 121 | 
 122 | ### Step 6: Handle GPU Dependencies
 123 | 
 124 | Always skip gracefully when GPU unavailable:
 125 | 
 126 | ```python
 127 | CUDA_AVAILABLE = torch.cuda.is_available()
 128 | 
 129 | @pytest.mark.skipif(not CUDA_AVAILABLE, reason="CUDA not available")
 130 | def test_gpu_function():
 131 |     tensor = torch.tensor([1, 2, 3], device="cuda")
 132 |     # ... assertions
 133 | ```
 134 | 
 135 | ## Key Requirements (Based on testing.md)
 136 | 
 137 | ### Mocking Distributed
 138 | 
 139 | - Use `torch.distributed.fake_pg` for unit tests
 140 | - Mock `dist.get_rank()` and `dist.get_world_size()` explicitly
 141 | - Don't mock internals of FSDP/DTensor
 142 | 
 143 | ### GPU Test Constraints
 144 | 
 145 | - **Always skip gracefully** when GPU unavailable
 146 | - Clean up GPU memory: `torch.cuda.empty_cache()` in fixtures
 147 | - Use smallest possible model/batch for unit tests
 148 | 
 149 | ### Assertions
 150 | 
 151 | - Use `torch.testing.assert_close()` for tensor comparison
 152 | - Specify `rtol`/`atol` explicitly for numerical tests
 153 | - Avoid bare `assert tensor.equal()` - no useful error message
 154 | 
 155 | ## Reference Implementations
 156 | 
 157 | | Test File                        | Description                            | Key Patterns                                      |
 158 | | -------------------------------- | -------------------------------------- | ------------------------------------------------- |
 159 | | `tests/test_utils.py`            | Utility function tests                 | Fixtures, parametrized tests                      |
 160 | | `tests/test_examples.py`         | Integration tests with dataset loading | Dataset path resolution, success pattern matching |
 161 | | `tests/test_fsdp_engine_nccl.py` | Distributed tests                      | Torchrun integration                              |
 162 | 
 163 | ## Common Mistakes
 164 | 
 165 | - **Missing test file registration**: Ensure file follows `test_*.py` naming
 166 | - **GPU dependency without skip**: Always use `@pytest.mark.skipif` for GPU tests
 167 | - **Incorrect tensor comparisons**: Use `torch.testing.assert_close()` not
 168 |   `assert tensor.equal()`
 169 | - **Memory leaks in GPU tests**: Clean up with `torch.cuda.empty_cache()`
 170 | - **Mocking too much**: Don't mock FSDP/DTensor internals
 171 | - **Unclear test names**: Follow `test_<what>_<condition>_<expected>` pattern
 172 | - **No docstrings**: Add descriptive docstrings to test functions
 173 | 
 174 | ## Integration with Other Skills
 175 | 
 176 | This skill complements other AReaL development skills:
 177 | 
 178 | - **After `/add-dataset`**: Add tests for new dataset loaders
 179 | - **After `/add-workflow`**: Add tests for new workflows
 180 | - **After `/add-reward`**: Add tests for new reward functions
 181 | - **With expert agents**: Reference this skill when planning test implementation
 182 | 
 183 | ## Running Tests
 184 | 
 185 | ```bash
 186 | # First check GPU availability (many tests require GPU)
 187 | python -c "import torch; print('GPU available:', torch.cuda.is_available())"
 188 | 
 189 | # Run specific test file
 190 | uv run pytest tests/test_<name>.py
 191 | 
 192 | # Skip slow tests (CI default)
 193 | uv run pytest -m "not slow"
 194 | 
 195 | # Run with verbose output
 196 | uv run pytest -v
 197 | 
 198 | # Run distributed tests (requires torchrun and multi-GPU)
 199 | # Note: Usually invoked via pytest test files
 200 | torchrun --nproc_per_node=2 tests/torchrun/run_<test>.py
 201 | ```
 202 | 
 203 | <!--
 204 | ================================================================================
 205 |                             MAINTAINER GUIDE
 206 | ================================================================================
 207 | 
 208 | Location: .opencode/skills/add-unit-tests/SKILL.md
 209 | Invocation: /add-unit-tests
 210 | 
 211 | ## Purpose
 212 | 
 213 | Step-by-step guide for adding unit tests to AReaL.
 214 | 
 215 | ## How to Update
 216 | 
 217 | ### When Testing Conventions Change
 218 | 1. Update "Key Requirements" section based on `testing.md`
 219 | 2. Update test examples to match new patterns
 220 | 3. Update reference implementations
 221 | 
 222 | ### When Test Types Need Update
 223 | 1. Update "Understand Test Types" table (currently two main types)
 224 | 2. Add new examples if needed
 225 | 3. Update common mistakes
 226 | 
 227 | ### Integration with Other Skills
 228 | Ensure references to other skills (`/add-dataset`, `/add-workflow`, `/add-reward`) remain accurate.
 229 | 
 230 | ================================================================================
 231 | -->
```


---
## .opencode/skills/add-workflow/SKILL.md

```
   1 | ---
   2 | name: add-workflow
   3 | description: Guide for adding a new RolloutWorkflow to AReaL. Use when user wants to create a new workflow.
   4 | ---
   5 | 
   6 | # Add Workflow
   7 | 
   8 | Add a new RolloutWorkflow implementation to AReaL.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add a workflow?"
  15 | - User wants to create a new RolloutWorkflow
  16 | - User mentions implementing a custom rollout
  17 | 
  18 | ## Prerequisites
  19 | 
  20 | Before starting, ensure you understand:
  21 | 
  22 | - The workflow's purpose and requirements
  23 | - Input/output data format
  24 | - Reward function to use
  25 | 
  26 | ## Step-by-Step Guide
  27 | 
  28 | ### Step 1: Create Workflow File
  29 | 
  30 | Create `areal/workflow/<name>.py`:
  31 | 
  32 | ```python
  33 | import uuid
  34 | from typing import Any, Callable
  35 | 
  36 | import torch
  37 | 
  38 | from areal.api.cli_args import GenerationHyperparameters
  39 | from areal.api.engine_api import InferenceEngine
  40 | from areal.api.io_struct import ModelRequest, ModelResponse
  41 | from areal.api.reward_api import AsyncRewardWrapper
  42 | from areal.api.workflow_api import RolloutWorkflow
  43 | from areal.utils import logging
  44 | 
  45 | logger = logging.getLogger("MyWorkflow")
  46 | 
  47 | 
  48 | class MyWorkflow(RolloutWorkflow):
  49 |     """Description of your workflow."""
  50 | 
  51 |     def __init__(
  52 |         self,
  53 |         gconfig: GenerationHyperparameters,
  54 |         tokenizer,
  55 |         reward_fn: Callable,
  56 |     ):
  57 |         self.gconfig = gconfig.new_with_stop_and_pad_token_ids(tokenizer)
  58 |         self.tokenizer = tokenizer
  59 |         self.async_reward_fn = AsyncRewardWrapper(reward_fn)
  60 | 
  61 |     async def arun_episode(
  62 |         self,
  63 |         engine: InferenceEngine,
  64 |         data: dict[str, Any],
  65 |     ) -> dict[str, Any] | None | dict[str, InteractionWithTokenLogpReward]:
  66 |         """Run a single episode. MUST be async and non-blocking."""
  67 | 
  68 |         # 1. Prepare input_ids from data
  69 |         input_ids = self.tokenizer.apply_chat_template(
  70 |             data["messages"],
  71 |             tokenize=True,
  72 |             add_generation_prompt=True,
  73 |         )
  74 | 
  75 |         # 2. Build ModelRequest
  76 |         req = ModelRequest(
  77 |             rid=uuid.uuid4().hex,
  78 |             input_ids=list(input_ids),
  79 |             gconfig=self.gconfig.new(n_samples=1),
  80 |             tokenizer=self.tokenizer,
  81 |         )
  82 | 
  83 |         # 3. Generate completion (async)
  84 |         resp: ModelResponse = await engine.agenerate(req)
  85 | 
  86 |         # 4. Compute reward (async)
  87 |         prompt_str = self.tokenizer.decode(input_ids)
  88 |         completion_str = self.tokenizer.decode(resp.output_tokens)
  89 |         reward = await self.async_reward_fn(
  90 |             prompt_str,
  91 |             completion_str,
  92 |             resp.input_tokens,
  93 |             resp.output_tokens,
  94 |             **data,
  95 |         )
  96 | 
  97 |         # 5. Return results in expected format
  98 |         return {
  99 |             "input_ids": torch.tensor(resp.input_tokens),
 100 |             "output_ids": torch.tensor(resp.output_tokens),
 101 |             "reward": torch.tensor(reward),
 102 |         }
 103 | ```
 104 | 
 105 | ### Step 2: Register in __init__.py
 106 | 
 107 | Add to `areal/workflow/__init__.py`:
 108 | 
 109 | ```python
 110 | from areal.workflow.<name> import MyWorkflow
 111 | 
 112 | __all__ = [
 113 |     # ... existing exports
 114 |     "MyWorkflow",
 115 | ]
 116 | ```
 117 | 
 118 | ### Step 3: Update Entry Script
 119 | 
 120 | Update your training script to use the new workflow:
 121 | 
 122 | ```python
 123 | trainer.train(
 124 |     workflow="areal.workflow.<name>.MyWorkflow",
 125 |     # ... other args
 126 | )
 127 | ```
 128 | 
 129 | ### Step 4: Add Tests
 130 | 
 131 | Create `tests/test_<name>_workflow.py`:
 132 | 
 133 | ```python
 134 | import pytest
 135 | from areal.workflow.<name> import MyWorkflow
 136 | 
 137 | @pytest.mark.asyncio
 138 | async def test_workflow_basic():
 139 |     # Test basic functionality
 140 |     pass
 141 | ```
 142 | 
 143 | ## Reference Implementations
 144 | 
 145 | | Workflow           | File                            | Description                |
 146 | | ------------------ | ------------------------------- | -------------------------- |
 147 | | MultiTurnWorkflow  | `areal/workflow/multi_turn.py`  | Multi-turn conversation    |
 148 | | RLVRWorkflow       | `areal/workflow/rlvr.py`        | RL with verifiable rewards |
 149 | | VisionRLVRWorkflow | `areal/workflow/vision_rlvr.py` | Vision + RLVR              |
 150 | 
 151 | ## Key Requirements
 152 | 
 153 | 1. **Async**: `arun_episode` must be `async def` and non-blocking
 154 | 1. **No sync I/O**: Use `aiofiles` for file operations
 155 | 1. **Wrap rewards**: Use `AsyncRewardWrapper` for reward functions
 156 | 1. **Tensor format**: Output tensors should be `[batch, seq_len, ...]`
 157 | 1. **Use helpers**: `concat_padded_tensors` for combining outputs
 158 | 
 159 | ## Common Mistakes
 160 | 
 161 | - Using `open()` instead of `aiofiles.open()`
 162 | - Forgetting to `await` async calls
 163 | - Not wrapping reward function with `AsyncRewardWrapper`
 164 | - Wrong tensor shape conventions
 165 | 
 166 | ______________________________________________________________________
 167 | 
 168 | <!--
 169 | ================================================================================
 170 |                             MAINTAINER GUIDE
 171 | ================================================================================
 172 | 
 173 | Location: .opencode/skills/add-workflow/SKILL.md
 174 | Invocation: /add-workflow <name>
 175 | 
 176 | ## Purpose
 177 | 
 178 | Step-by-step guide for adding new RolloutWorkflow implementations.
 179 | 
 180 | ## How to Update
 181 | 
 182 | ### When Workflow API Changes
 183 | 1. Update the code template in Step 1
 184 | 2. Update the required imports
 185 | 3. Update the method signature if changed
 186 | 
 187 | ### When New Patterns Emerge
 188 | 1. Add to "Reference Implementations" table
 189 | 2. Update "Key Requirements" if new requirements added
 190 | 
 191 | ================================================================================
 192 | -->
```


---
## .opencode/skills/commit-conventions/SKILL.md

```
   1 | ---
   2 | name: commit-conventions
   3 | description: AReaL commit message conventions. MUST load on every git commit -- provides Conventional Commits format with scope inference from file paths.
   4 | ---
   5 | 
   6 | # Commit Conventions
   7 | 
   8 | Commit message conventions and scope inference rules for the AReaL repository.
   9 | 
  10 | ## When to Use
  11 | 
  12 | **ALWAYS load this skill when making any git commit in AReaL.** This includes:
  13 | 
  14 | - Direct commits (`git commit`)
  15 | - Commits during PR creation (`/create-pr`)
  16 | - Commits delegated via `task(load_skills=["commit-conventions"], ...)`
  17 | - Any agent workflow that produces a commit
  18 | 
  19 | ## Commit Message Format
  20 | 
  21 | ```
  22 | <type>(<scope>): <subject>
  23 | 
  24 | <body>
  25 | 
  26 | [Optional sections:]
  27 | Key changes:
  28 | - change 1
  29 | - change 2
  30 | 
  31 | Refs: #123, #456
  32 | ```
  33 | 
  34 | ## Type Selection
  35 | 
  36 | | Type       | When to Use                     |
  37 | | ---------- | ------------------------------- |
  38 | | `feat`     | New feature or capability       |
  39 | | `fix`      | Bug fix                         |
  40 | | `docs`     | Documentation only              |
  41 | | `refactor` | Code change without feature/fix |
  42 | | `test`     | Adding or fixing tests          |
  43 | | `chore`    | Build, deps, config changes     |
  44 | | `perf`     | Performance improvement         |
  45 | 
  46 | ## Scope Inference
  47 | 
  48 | Infer scope from the **primary** changed file paths:
  49 | 
  50 | | File Path Pattern        | Scope                          |
  51 | | ------------------------ | ------------------------------ |
  52 | | `areal/workflow/`        | `workflow`                     |
  53 | | `areal/engine/`          | `engine`                       |
  54 | | `areal/reward/`          | `reward`                       |
  55 | | `areal/dataset/`         | `dataset`                      |
  56 | | `areal/api/`             | `api`                          |
  57 | | `areal/utils/`           | `utils`                        |
  58 | | `areal/infra/`           | `infra`                        |
  59 | | `areal/trainer/`         | `trainer`                      |
  60 | | `areal/models/`          | `models`                       |
  61 | | `areal/experimental/`    | `archon`                       |
  62 | | `docs/`                  | `docs`                         |
  63 | | `examples/`              | `examples`                     |
  64 | | `.claude/`, `.opencode/` | `agents`                       |
  65 | | Multiple areas           | Omit scope or use broader term |
  66 | 
  67 | ## Rules
  68 | 
  69 | - **Subject**: imperative mood, ~50-72 chars, no trailing period
  70 | - **Body**: explain "why" not "what", wrap at 72 chars
  71 | - **Key changes**: bullet list of main modifications (for complex commits with 3+ files)
  72 | - **Refs**: reference issues/PRs if applicable
  73 | 
  74 | ## Examples
  75 | 
  76 | **Single file fix:**
  77 | 
  78 | ```
  79 | fix(reward): handle empty completion in gsm8k
  80 | 
  81 | Return 0 reward instead of raising exception when
  82 | completion string is empty after extraction.
  83 | ```
  84 | 
  85 | **Multi-file feature:**
  86 | 
  87 | ```
  88 | feat(engine): add CPU offload support to ArchonEngine
  89 | 
  90 | Enable torch_memory_saver for model offloading during
  91 | rollout phase to reduce GPU memory pressure.
  92 | 
  93 | Key changes:
  94 | - Add offload/onload methods to ArchonEngine
  95 | - Integrate with weight update flow
  96 | - Handle ROCm compatibility
  97 | ```
  98 | 
  99 | **Docs only:**
 100 | 
 101 | ```
 102 | docs: update algorithm comparison table
 103 | 
 104 | Add SAPO and GSPO to the algorithm family documentation
 105 | with configuration examples.
 106 | ```
 107 | 
 108 | **Agent/tooling changes:**
 109 | 
 110 | ```
 111 | chore(agents): port review-pr command to OpenCode
 112 | 
 113 | Add OpenCode-native commands with task() category
 114 | delegation instead of hardcoded model names.
 115 | 
 116 | Key changes:
 117 | - Create .opencode/command/ with review-pr, create-pr
 118 | - Replace Opus/Sonnet/Haiku with deep/unspecified-high/quick
 119 | - Add expert subagent consultation patterns
 120 | ```
 121 | 
 122 | ______________________________________________________________________
 123 | 
 124 | <!--
 125 | ================================================================================
 126 |                             MAINTAINER GUIDE
 127 | ================================================================================
 128 | 
 129 | Location: .opencode/skills/commit-conventions/SKILL.md
 130 | Invocation: Automatically loaded on every git commit via load_skills
 131 | 
 132 | ## Purpose
 133 | 
 134 | Provides Conventional Commits format with AReaL-specific scope inference
 135 | from file paths. Unlike other skills, this one is NOT user-triggered --
 136 | it is loaded by the system/agent on every commit operation.
 137 | 
 138 | ## How to Update
 139 | 
 140 | ### When New Modules Are Added
 141 | 1. Add the file path pattern and scope to the "Scope Inference" table
 142 | 2. Keep table sorted by areal/ subpackages first, then top-level dirs
 143 | 
 144 | ### When Commit Types Change
 145 | 1. Update the "Type Selection" table
 146 | 2. Add/update examples to illustrate the new type
 147 | 
 148 | ### When Adding Examples
 149 | 1. Each example should demonstrate a distinct commit pattern
 150 | 2. Keep examples realistic -- use actual AReaL module names
 151 | 3. Show both subject-only and subject+body+key-changes variants
 152 | 
 153 | ### Important Design Decisions
 154 | - This skill is ALWAYS loaded (not optional) -- keep it concise to
 155 |   minimize token overhead on every commit
 156 | - Scope inference is path-based, not content-based -- simpler and
 157 |   more deterministic
 158 | - "Multiple areas" -> omit scope rather than invent a new one
 159 | 
 160 | ================================================================================
 161 | -->
```


---
## .opencode/skills/debug-distributed/SKILL.md

```
   1 | ---
   2 | name: debug-distributed
   3 | description: Guide for debugging distributed training issues in AReaL. Use when user encounters hangs, wrong results, OOM, or communication errors.
   4 | ---
   5 | 
   6 | # Debug Distributed Training
   7 | 
   8 | Debugging guide for distributed training issues in AReaL (FSDP2, TP, CP, EP).
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - Training hangs or deadlocks
  15 | - Results differ across ranks or are numerically wrong
  16 | - OOM errors in distributed settings
  17 | - NCCL/communication errors or device mesh issues
  18 | 
  19 | ## Debugging Principles
  20 | 
  21 | ### Minimal Reproduction
  22 | 
  23 | **Always follow the minimal demo principle**: Reproduce with the least amount of code to
  24 | narrow down the issue faster.
  25 | 
  26 | ```python
  27 | # Bad: Debug in full training loop
  28 | # Good: Create minimal script
  29 | import torch
  30 | import torch.distributed as dist
  31 | 
  32 | dist.init_process_group("nccl")
  33 | rank = dist.get_rank()
  34 | 
  35 | # Reproduce the exact operation that fails
  36 | tensor = torch.ones(10).cuda()
  37 | dist.all_reduce(tensor)  # <-- Isolate the failing op
  38 | print(f"Rank {rank}: {tensor}")
  39 | ```
  40 | 
  41 | **Reduction strategy:**
  42 | 
  43 | 1. Remove unrelated model components
  44 | 1. Use small tensor sizes
  45 | 1. Reduce world_size to minimum (e.g., 2 GPUs)
  46 | 1. Remove torch.compile if possible
  47 | 1. Disable activation checkpointing
  48 | 
  49 | ## Step-by-Step Debugging Guide
  50 | 
  51 | ### 1. Hang Debugging (Deadlocks, Synchronization)
  52 | 
  53 | **Environment Variables for Debugging**:
  54 | 
  55 | ```bash
  56 | # Full debug logging
  57 | export TORCH_DISTRIBUTED_DEBUG=DETAIL
  58 | export NCCL_DEBUG=INFO
  59 | export NCCL_DEBUG_SUBSYS=ALL
  60 | 
  61 | # torch.compile debugging
  62 | export TORCH_LOGS="+dynamo,recompiles"
  63 | export TORCHDYNAMO_VERBOSE=1
  64 | ```
  65 | 
  66 | **Dump Call Stack with py-spy** (for hung processes):
  67 | 
  68 | ```bash
  69 | # Find process IDs
  70 | ps aux | grep python
  71 | 
  72 | # Dump call stack of specific rank
  73 | py-spy dump --pid <PID>
  74 | 
  75 | # Record flame graph for performance analysis
  76 | py-spy record -o profile.svg --pid <PID> --duration 30
  77 | ```
  78 | 
  79 | **Common Causes**:
  80 | 
  81 | 1. **Mismatched Collectives**: One rank calls `all_reduce`, another doesn't.
  82 | 1. **Wrong Process Group**: Using wrong group for collective.
  83 | 1. **Tensor Shape Mismatch**: Different shapes across ranks.
  84 | 
  85 | **Debug Steps**:
  86 | 
  87 | ```python
  88 | # Verify group membership
  89 | mesh = parallel_dims.get_mesh("dp_shard_cp")
  90 | group = mesh.get_group()
  91 | print(f"Rank {dist.get_rank()}: group size = {dist.get_world_size(group)}")
  92 | 
  93 | # Print shapes on all ranks
  94 | print(f"Rank {dist.get_rank()}: tensor.shape = {tensor.shape}")
  95 | dist.barrier()
  96 | ```
  97 | 
  98 | **Timeout Adjustment** (for debugging only):
  99 | 
 100 | ```python
 101 | from areal.engine.core.distributed import patch_dist_group_timeout
 102 | from datetime import timedelta
 103 | patch_dist_group_timeout(timedelta(minutes=30))
 104 | ```
 105 | 
 106 | ### 2. Wrong Results (Gradient, Reduction Issues)
 107 | 
 108 | **Check DTensor Placements**:
 109 | 
 110 | ```python
 111 | from torch.distributed.tensor import DTensor
 112 | if isinstance(param, DTensor):
 113 |     print(f"Param {name}: placements={param.placements}, mesh={param.device_mesh}")
 114 | ```
 115 | 
 116 | **Verify Gradient Reduction**:
 117 | 
 118 | ```python
 119 | for name, param in model.named_parameters():
 120 |     if param.grad is not None:
 121 |         print(f"Rank {dist.get_rank()}: {name} grad_sum = {param.grad.sum().item()}")
 122 | ```
 123 | 
 124 | ### 3. OOM Issues (Memory, Sharding)
 125 | 
 126 | **Check Memory Usage**:
 127 | 
 128 | ```python
 129 | print(f"Rank {dist.get_rank()}: "
 130 |       f"allocated={torch.cuda.memory_allocated()/1e9:.2f}GB, "
 131 |       f"reserved={torch.cuda.memory_reserved()/1e9:.2f}GB")
 132 | ```
 133 | 
 134 | **Check FSDP Coverage**:
 135 | 
 136 | ```python
 137 | for name, param in model.named_parameters():
 138 |     is_dtensor = isinstance(param, DTensor)
 139 |     print(f"{name}: is_dtensor={is_dtensor}, shape={param.shape}")
 140 | ```
 141 | 
 142 | ### 4. Communication Errors
 143 | 
 144 | | Error                     | Cause                | Solution                           |
 145 | | ------------------------- | -------------------- | ---------------------------------- |
 146 | | `NCCL WARN Cuda failure`  | GPU communication    | Check NCCL version, GPU topology   |
 147 | | `RuntimeError: Timed out` | Rank synchronization | Increase timeout, check code paths |
 148 | | `Invalid device mesh`     | Mesh configuration   | Verify world_size = dp * tp * cp   |
 149 | 
 150 | ## Debugging Tools
 151 | 
 152 | ### Environment Variables Reference
 153 | 
 154 | | Variable                          | Purpose                                |
 155 | | --------------------------------- | -------------------------------------- |
 156 | | `TORCH_DISTRIBUTED_DEBUG=DETAIL`  | Detailed distributed logging           |
 157 | | `NCCL_DEBUG=INFO`                 | NCCL communication logging             |
 158 | | `NCCL_DEBUG_SUBSYS=ALL`           | All NCCL subsystems                    |
 159 | | `TORCH_LOGS="+dynamo,recompiles"` | torch.compile logging                  |
 160 | | `TORCHDYNAMO_VERBOSE=1`           | Dynamo verbose output                  |
 161 | | `CUDA_LAUNCH_BLOCKING=1`          | Synchronous CUDA (slow, for debugging) |
 162 | 
 163 | ### py-spy for Call Stack Analysis
 164 | 
 165 | ```bash
 166 | # Install
 167 | pip install py-spy
 168 | 
 169 | # Dump call stack of hung process
 170 | py-spy dump --pid <PID>
 171 | 
 172 | # Dump all Python processes
 173 | pgrep -f python | xargs -I {} py-spy dump --pid {}
 174 | 
 175 | # Record flame graph
 176 | py-spy record -o profile.svg --pid <PID> --duration 30
 177 | ```
 178 | 
 179 | ### Rank-Conditional Printing
 180 | 
 181 | ```python
 182 | def print_all_ranks(msg):
 183 |     for r in range(dist.get_world_size()):
 184 |         if dist.get_rank() == r:
 185 |             print(f"[Rank {r}] {msg}")
 186 |         dist.barrier()
 187 | ```
 188 | 
 189 | ### Check Device Mesh
 190 | 
 191 | ```python
 192 | def debug_mesh(parallel_dims):
 193 |     mesh = parallel_dims.world_mesh
 194 |     for dim_name in mesh.mesh_dim_names:
 195 |         submesh = parallel_dims.get_mesh(dim_name)
 196 |         if submesh:
 197 |             print(f"Rank {dist.get_rank()}: {dim_name} size={submesh.size()}")
 198 | ```
 199 | 
 200 | ### Validate Tensor Consistency
 201 | 
 202 | ```python
 203 | def check_tensor_consistency(tensor, name, group=None):
 204 |     local_sum = tensor.sum().item()
 205 |     tensor_sums = [None] * dist.get_world_size(group)
 206 |     dist.all_gather_object(tensor_sums, local_sum, group=group)
 207 |     if dist.get_rank() == 0 and len(set(tensor_sums)) > 1:
 208 |         print(f"WARNING: {name} inconsistent: {tensor_sums}")
 209 | ```
 210 | 
 211 | ## Key Files Reference
 212 | 
 213 | | Component       | File                                                          |
 214 | | --------------- | ------------------------------------------------------------- |
 215 | | Parallel Dims   | `areal/experimental/models/archon/parallel_dims.py`           |
 216 | | Expert Parallel | `areal/experimental/models/archon/expert_parallel.py`         |
 217 | | Ulysses (CP)    | `areal/experimental/models/archon/ulysses.py`                 |
 218 | | FSDP/TP Apply   | `areal/experimental/models/archon/qwen2/infra/parallelize.py` |
 219 | 
 220 | ______________________________________________________________________
 221 | 
 222 | <!--
 223 | ================================================================================
 224 |                             MAINTAINER GUIDE
 225 | ================================================================================
 226 | 
 227 | Location: .opencode/skills/debug-distributed/SKILL.md
 228 | Invocation: /debug-distributed
 229 | 
 230 | ## Purpose
 231 | 
 232 | Debugging guide for distributed training issues.
 233 | Covers FSDP2, Tensor Parallelism, Context Parallelism, and Expert Parallelism.
 234 | 
 235 | ## How to Update
 236 | 
 237 | ### When Adding New Parallelism Features
 238 | 1. Add section for the parallelism type
 239 | 2. Document common error patterns and debugging snippets
 240 | 
 241 | ### When PyTorch Distributed APIs Change
 242 | 1. Update DTensor/DeviceMesh examples
 243 | 2. Update environment variable references
 244 | 
 245 | ### When New Error Patterns Emerge
 246 | 1. Add to "Common Errors and Solutions" table
 247 | 2. Reference relevant source files
 248 | 
 249 | ================================================================================
 250 | -->
```


---
## AGENTS.md

```
   1 | <!-- Go-to brief for AI coding agents working on AReaL. -->
   2 | 
   3 | # AGENTS.md -- AReaL Agent Operations Guide
   4 | 
   5 | ## Quick reference
   6 | 
   7 | **Tech stack**: Python 3.12+ | PyTorch | FSDP2 / Megatron / Archon | SGLang / vLLM
   8 | 
   9 | ```bash
  10 | # Environment
  11 | uv sync --extra cuda            # CUDA + SGLang inference (default); for vLLM: --extra cuda-train --extra vllm
  12 | source .venv/bin/activate        # activate venv BEFORE pre-commit or git commit if venv exists
  13 | pre-commit install --install-hooks  # hooks: Ruff, clang-format, mdformat, nbstripout, conventional-commits
  14 | pre-commit run --all-files       # lint + format everything
  15 | 
  16 | # Tests
  17 | uv run pytest tests/test_<topic>.py
  18 | 
  19 | # CLI docs
  20 | uv run python docs/generate_cli_docs.py
  21 | 
  22 | # Docs build (canonical, release-aligned)
  23 | ./docs/build_all.sh
  24 | # Do NOT use `jupyter-book build docs/en|docs/zh` directly for final preview/release,
  25 | # because it skips AReaL-specific static setup and output packaging.
  26 | ```
  27 | 
  28 | **Hard rules** -- never violate:
  29 | 
  30 | - No wildcard imports (`from x import *`).
  31 | - No hardcoded secrets, paths, or endpoints.
  32 | - No skipping pre-commit hooks.
  33 | - No guessing cluster configs or rebuilding CUDA/driver stacks.
  34 | - Integration tests require multi-node hardware -- explain skips explicitly.
  35 | 
  36 | **Always do**:
  37 | 
  38 | - Read relevant files before modifying code.
  39 | - Run `pre-commit run --all-files` before committing.
  40 | - Follow existing code patterns in the same module.
  41 | - Add tests for new functionality.
  42 | - Use the `question` tool (structured options) when asking the user for decisions or
  43 |   clarifications.
  44 | 
  45 | **Ask first** before:
  46 | 
  47 | - Modifying config structures in `areal/api/cli_args.py`.
  48 | - Adding new dependencies.
  49 | - Changing launcher or scheduler logic.
  50 | - Deleting or renaming public APIs.
  51 | 
  52 | When unsure, leave a `TODO(agent)` comment and note the constraint in your response.
  53 | 
  54 | ______________________________________________________________________
  55 | 
  56 | ## Repository map
  57 | 
  58 | ```
  59 | areal/                     Core Python package
  60 | |-- api/                   Config dataclasses, contracts, IO structs
  61 | |-- dataset/               Stateful dataset loaders (GSM8K, Geometry3K, CLEVR, ...)
  62 | |-- engine/                Training backends (FSDP2, Megatron) + inference adapters
  63 | |-- experimental/          Prototype engines/workflows (Archon MoE engine)
  64 | |-- infra/                 Launchers (Local/Ray/Slurm), schedulers, utilities
  65 | |-- models/                Model adapters (Megatron-Core, Transformers, custom heads)
  66 | |-- reward/                Built-in reward functions + math parsers
  67 | |-- tests/                 Unit/integration test suites
  68 | |-- trainer/               High-level orchestrators (PPOTrainer, SFTTrainer)
  69 | |-- utils/                 Cross-cutting helpers (logging, data, checkpoints, RL ops)
  70 | +-- workflow/              RolloutWorkflow implementations (RLVR, multi-turn, vision)
  71 | 
  72 | docs/                      Jupyter Book docs (https://inclusionai.github.io/AReaL/)
  73 | examples/                  Training scripts and launcher recipes
  74 | ```
  75 | 
  76 | ______________________________________________________________________
  77 | 
  78 | ## Code style & patterns
  79 | 
  80 | - **Composition over inheritance** -- keep hierarchies \<= 2 levels; prefer delegation.
  81 | 
  82 | | Type             | Pattern         | Example                                   |
  83 | | ---------------- | --------------- | ----------------------------------------- |
  84 | | Config dataclass | `XxxConfig`     | `GRPOConfig`, `FSDPEngineConfig`          |
  85 | | Engine class     | `XxxEngine`     | `FSDPEngine`, `ArchonEngine`              |
  86 | | Workflow class   | `XxxWorkflow`   | `RLVRWorkflow`, `MultiTurnWorkflow`       |
  87 | | Reward function  | `xxx_reward_fn` | `gsm8k_reward_fn`, `geometry3k_reward_fn` |
  88 | 
  89 | **Logging**: `areal.utils.logging.getLogger(name)` with **PascalCase** names -- never
  90 | `print` or `logging.__name__`. Per-rank format: `[{Component} Rank {N}]`. Register new
  91 | loggers with color in `areal/utils/logging.py`.
  92 | 
  93 | **Performance**:
  94 | 
  95 | - No GPU-CPU sync in hot paths (`.item()`, `.tolist()`, `print(tensor)`).
  96 | - Batch ops over Python loops on tensor elements.
  97 | - Explicit `dtype`/`device`; `torch.Size` assertions for shape validation.
  98 | 
  99 | **Typing & imports**: explicit type hints; reuse `areal/api/cli_args.py` dataclasses; no
 100 | wildcard imports; heavy optional deps inside functions.
 101 | 
 102 | **Async**: rollout workflows must stay non-blocking (`await` + `aiofiles`); no sync I/O
 103 | in `arun_episode`.
 104 | 
 105 | ______________________________________________________________________
 106 | 
 107 | ## Domain experts & skills
 108 | 
 109 | Fire the appropriate **expert subagent** or **load a skill** based on what you're
 110 | working on. Experts are read-only consultants with deep domain knowledge; skills are
 111 | step-by-step implementation guides.
 112 | 
 113 | | Working on...                | Fire subagent      | Load skill          |
 114 | | ---------------------------- | ------------------ | ------------------- |
 115 | | FSDP engine code             | `fsdp-expert`      | --                  |
 116 | | Archon engine / new model    | `archon-expert`    | `add-archon-model`  |
 117 | | Megatron engine code         | `megatron-expert`  | --                  |
 118 | | RL algorithms / PPO / GRPO   | `algorithm-expert` | --                  |
 119 | | Launcher / scheduler / infra | `launcher-expert`  | `debug-distributed` |
 120 | | New reward function          | --                 | `add-reward`        |
 121 | | New dataset loader           | --                 | `add-dataset`       |
 122 | | New rollout workflow         | --                 | `add-workflow`      |
 123 | | Unit tests                   | --                 | `add-unit-tests`    |
 124 | | Distributed debugging        | --                 | `debug-distributed` |
 125 | 
 126 | **How to fire an expert**:
 127 | `task(subagent_type="fsdp-expert", load_skills=[], run_in_background=true, prompt="...")`
 128 | 
 129 | ______________________________________________________________________
 130 | 
 131 | ## Core concepts
 132 | 
 133 | **Trainer** orchestrator (`areal/trainer/`, `PPOTrainer`, `SFTTrainer`): manages the
 134 | training loop, dataset loading, and workflow execution. Entry point:
 135 | `examples/math/gsm8k_rl.py`.
 136 | 
 137 | **Rollout workflows** (`areal/workflow/`, `RolloutWorkflow.arun_episode`): define how
 138 | episodes are generated. Use `add-workflow` skill for step-by-step guide.
 139 | 
 140 | **Engines**: *Inference engines* handle async generation via `engine.agenerate()` and
 141 | manage weight updates. *Training engines* consume rollout tensors, compute PPO/GRPO
 142 | updates, and broadcast weight versions (FSDP2, Megatron, or Archon).
 143 | 
 144 | **Weight versioning**: async workflows require version alignment via `WeightUpdateMeta`
 145 | (`areal/api/engine_api.py`). Critical for correctness across distributed training.
 146 | 
 147 | **Observability**: emit metrics via `stats_tracker.get()`, persist artifacts under
 148 | `dump_dir`, checkpoint via `areal/utils/saver.py` / `recover.py`.
 149 | 
 150 | **Launcher / scheduler**: training requires cluster setup (local / Ray / Slurm) via
 151 | configs in `areal/infra/launcher/`. See `launcher-expert` for deployment guidance.
 152 | 
 153 | ______________________________________________________________________
 154 | 
 155 | ## API & config rules
 156 | 
 157 | *Applies to: `areal/api/**`*
 158 | 
 159 | - **Field ordering**: required -> common optional -> rare optional -> internal (`_`
 160 |   prefix).
 161 | - **Validation**: `__post_init__` with `ValueError` and clear message.
 162 | - **Backward compat**: add fields with defaults; deprecate before removing; avoid type
 163 |   changes.
 164 | - **CLI**: use `Literal` for enum choices; all public configs need docstrings with
 165 |   constraints.
 166 | 
 167 | ______________________________________________________________________
 168 | 
 169 | ## Distributed code rules
 170 | 
 171 | *Applies to: `areal/engine/**`, `areal/experimental/**`*
 172 | 
 173 | - Never create global process groups at module level; always pass `process_group`
 174 |   explicitly.
 175 | - `dist.get_rank(group)` not `dist.get_rank()` when group matters.
 176 | - DeviceMesh dimensions must match `ArchonParallelDims`: `dp_shard`, `tp`, `cp`, `ep`,
 177 |   `etp`.
 178 | - All-reduce: all ranks must call. Broadcast: explicit `src`. Barrier: debugging only.
 179 | 
 180 | | Issue         | Cause                            | Fix                       |
 181 | | ------------- | -------------------------------- | ------------------------- |
 182 | | Hang          | Mismatched collective calls      | All ranks call same op    |
 183 | | Wrong results | Incorrect `ReduceOp`             | Check SUM vs MEAN         |
 184 | | OOM           | Unsharded tensor on wrong device | Verify DTensor placements |
 185 | 
 186 | Debug env vars: `TORCH_DISTRIBUTED_DEBUG=DETAIL`, `NCCL_DEBUG=INFO`,
 187 | `CUDA_LAUNCH_BLOCKING=1`. See `/debug-distributed` skill for comprehensive guide.
 188 | 
 189 | ______________________________________________________________________
 190 | 
 191 | ## Testing rules
 192 | 
 193 | *Applies to: `**/tests/**`, `test_*.py`*
 194 | 
 195 | | Marker                                  | When                             |
 196 | | --------------------------------------- | -------------------------------- |
 197 | | `@pytest.mark.slow`                     | > 10s (excluded from default CI) |
 198 | | `@pytest.mark.slow` + `@pytest.mark.ci` | Slow but must run in CI          |
 199 | | `@pytest.mark.asyncio`                  | Async tests                      |
 200 | 
 201 | - Naming: `test_<what>_<condition>_<expected>()` with Arrange/Act/Assert.
 202 | - GPU: skip gracefully (`@pytest.mark.skipif(not CUDA_AVAILABLE, reason="...")`).
 203 | - Distributed mocking: `torch.distributed.fake_pg`; don't mock FSDP/DTensor internals.
 204 | - Assertions: `torch.testing.assert_close()` with explicit `rtol`/`atol`; prefer
 205 |   `tmp_path`, `monkeypatch`.
 206 | 
 207 | | Suite       | Command                       | GPU       |
 208 | | ----------- | ----------------------------- | --------- |
 209 | | Unit        | `pytest tests/test_*.py`      | No        |
 210 | | GRPO        | `pytest tests/grpo/`          | Yes       |
 211 | | FSDP        | `pytest tests/test_fsdp_*.py` | Yes       |
 212 | | Distributed | `pytest tests/torchrun/`      | Multi-GPU |
 213 | 
 214 | ______________________________________________________________________
 215 | 
 216 | ## Collaboration & review
 217 | 
 218 | - **Branches**: kebab-case (`feature/multi-turn-metrics`, `bugfix/fsdp-weight-sync`).
 219 | - **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`), ~72 char subject,
 220 |   imperative voice. Squash WIP before PR.
 221 | - **Pre-merge**: full pre-commit stack; doc-only edits need at least `mdformat --check`.
 222 | - **PRs**: tie to issue, highlight risk areas, list test commands executed, note skipped
 223 |   suites with reasons.
 224 | 
 225 | | Command / Skill      | Purpose                                              |
 226 | | -------------------- | ---------------------------------------------------- |
 227 | | `/create-pr`         | Rebase, squash, create PR                            |
 228 | | `commit-conventions` | Commit message conventions (auto-triggers on commit) |
 229 | | `/review-pr`         | Dynamic agent-allocated PR review                    |
 230 | | `/translate-doc-zh`  | Translate English docs to Chinese                    |
 231 | 
 232 | ______________________________________________________________________
 233 | 
 234 | ## Reference material
 235 | 
 236 | - **Docs portal**: <https://inclusionai.github.io/AReaL/>
 237 | - **Quickstart**: `docs/tutorial/quickstart.md`
 238 | - **Architecture**: `docs/tutorial/gsm8k_grpo.md`
 239 | - **Customization**: `docs/customization/*.md`
 240 | - **Algorithms**: `docs/algorithms/*.md`
 241 | - **Best practices**: `docs/best_practices/*.md`
 242 | - **CLI reference**: `docs/cli_reference.md`
 243 | - **Agent workflow**: `docs/customization/agent.md`
```


---
## CLAUDE.md

```
   1 | # CLAUDE.md - AReaL
   2 | 
   3 | ## WHAT: Project Overview
   4 | 
   5 | AReaL is a distributed RL training framework for LLM alignment via reinforcement
   6 | learning.
   7 | 
   8 | **Tech Stack**: Python 3.12+ | PyTorch | FSDP2/Megatron | SGLang/vLLM
   9 | 
  10 | **Core Directories**:
  11 | 
  12 | - `areal/` - Core package
  13 |   - `api/` - Config dataclasses, workflow/engine contracts
  14 |   - `engine/` - FSDP2, Megatron, SGLang/vLLM adapters
  15 |     - `fsdp_utils/` - FSDP2-specific utilities (checkpoint, grad, optimizer, parallel)
  16 |     - `megatron_utils/` - Megatron/FP8 utilities (checkpoint, pipeline, quantization)
  17 |     - `core/` - Engine-shared utilities (distributed, lock, model, offload)
  18 |   - `infra/` - Infrastructure (launcher, scheduler, RPC)
  19 |     - `utils/` - Infrastructure utilities (launcher, proc, http, concurrent, slurm, ray)
  20 |   - `workflow/` - RolloutWorkflow implementations
  21 |   - `reward/` - Reward functions
  22 |   - `dataset/` - Dataset loaders
  23 |   - `utils/` - Cross-cutting utilities (logging, data, checkpoints, network, RL
  24 |     functional)
  25 | - `examples/` - Training scripts and configs
  26 | - `docs/` - Jupyter Book source
  27 | 
  28 | ## WHY: Purpose
  29 | 
  30 | - Enable efficient RL training for LLM alignment at scale
  31 | - Async rollout + distributed training for high throughput
  32 | - Modular design: workflows, engines, rewards, and datasets are independently extensible
  33 | 
  34 | ## HOW: Core Commands
  35 | 
  36 | ```bash
  37 | # Check environment
  38 | python --version              # Requires 3.12+
  39 | uv --version                  # Install: https://docs.astral.sh/uv/
  40 | 
  41 | # Sync dependencies
  42 | uv sync --extra cuda          # CUDA + SGLang inference (default)
  43 | uv sync --group dev           # Include dev/test packages
  44 | uv run python3 areal/tools/validate_installation.py  # Validate installation
  45 | 
  46 | # Pre-commit hooks
  47 | pre-commit install --install-hooks  # Set up hooks (run once)
  48 | pre-commit run --all-files    # Format and lint
  49 | 
  50 | # Run tests
  51 | # First check GPU availability (many tests require GPU)
  52 | python -c "import torch; print('GPU available:', torch.cuda.is_available())"
  53 | uv run pytest tests/test_<topic>.py
  54 | 
  55 | # Generate CLI docs
  56 | uv run python docs/generate_cli_docs.py
  57 | 
  58 | # Build docs (canonical, release-aligned)
  59 | ./docs/build_all.sh
  60 | # Do NOT use `jupyter-book build docs/en|docs/zh` directly for final preview/release,
  61 | # because it skips AReaL-specific static setup and output packaging.
  62 | ```
  63 | 
  64 | ## Boundaries
  65 | 
  66 | ### Constraints
  67 | 
  68 | - Designed for distributed GPU clusters; assume containerized execution
  69 | - Integration tests require multi-node hardware; explain skips when unavailable
  70 | - Secrets and endpoints are managed outside the repo
  71 | 
  72 | ### Always Do
  73 | 
  74 | - Read relevant files before modifying code
  75 | - Run `pre-commit run --all-files` before committing
  76 | - Follow existing code patterns in the same module
  77 | - Add tests for new functionality
  78 | 
  79 | ### Ask First
  80 | 
  81 | - Modifying config structures in `areal/api/cli_args.py`
  82 | - Adding new dependencies
  83 | - Changing launcher or scheduler logic
  84 | - Deleting or renaming public APIs
  85 | - Running GPU/distributed tests (check GPU first:
  86 |   `python -c "import torch; print('GPU available:', torch.cuda.is_available())"`)
  87 | 
  88 | ### Never Do
  89 | 
  90 | - Hardcode secrets, paths, or endpoints
  91 | - Skip pre-commit hooks
  92 | - Guess cluster configs or rebuild CUDA/driver stacks
  93 | - Use wildcard imports (`from x import *`)
  94 | 
  95 | ## Progressive Disclosure: Detailed Guides
  96 | 
  97 | | Task                   | Reference                                                     |
  98 | | ---------------------- | ------------------------------------------------------------- |
  99 | | Add Workflow           | `docs/customization/agent.md`, `areal/workflow/multi_turn.py` |
 100 | | Add Dataset            | `docs/customization/`, `areal/dataset/gsm8k.py`               |
 101 | | Add Reward             | `areal/api/reward_api.py`, `areal/reward/geometry3k.py`       |
 102 | | Add Archon Model       | `areal/experimental/models/archon/qwen2/`, `qwen3/`           |
 103 | | Algorithm Details      | `docs/algorithms/*.md`                                        |
 104 | | Quickstart             | `docs/tutorial/quickstart.md`                                 |
 105 | | Architecture Deep Dive | `docs/tutorial/gsm8k_grpo.md`                                 |
 106 | | CLI Reference          | `docs/cli_reference.md`                                       |
 107 | 
 108 | ## Git Workflow
 109 | 
 110 | - **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`), ~72 chars subject,
 111 |   imperative voice, reasoning in body
 112 | - **Squash**: Squash WIP commits before opening PR
 113 | - **PR requirements**: Run pre-commit, document test coverage, note hardware limitations
 114 | 
 115 | ## Extended Configuration
 116 | 
 117 | See `.claude/agents/`, `.claude/skills/`, `.claude/commands/`, and `.claude/rules/` for
 118 | specialized instructions.
 119 | 
 120 | ### Agents
 121 | 
 122 | | Agent                       | Purpose                                   | Activation Trigger                                                  |
 123 | | --------------------------- | ----------------------------------------- | ------------------------------------------------------------------- |
 124 | | `planner`                   | Implementation planning                   | Before multi-file changes, new features, or architectural decisions |
 125 | | `simple-code-reviewer`      | Quick code quality checks                 | After code changes, before committing                               |
 126 | | `code-verifier`             | Formatting/linting/tests                  | After code changes, before committing                               |
 127 | | `fsdp-engine-expert`        | FSDPEngine implementation                 | FSDPEngine code changes or questions                                |
 128 | | `archon-engine-expert`      | ArchonEngine implementation               | ArchonEngine code changes or questions                              |
 129 | | `megatron-engine-expert`    | MegatronEngine implementation             | MegatronEngine code changes or questions                            |
 130 | | `algorithm-expert`          | RL algorithms                             | GRPO/PPO/DAPO questions                                             |
 131 | | `launcher-scheduler-expert` | Cluster launching and resource scheduling | Launcher/scheduler code changes or configuration questions          |
 132 | 
 133 | **Stage-by-Stage Agent Guidance**:
 134 | 
 135 | 1. **Planning Stage** (Before coding): Use `planner` for architecture design and
 136 |    implementation planning
 137 | 1. **Code Formatting & Linting** (After coding): Use `code-verifier` to automatically
 138 |    run formatting, linting, and tests, catching syntax errors and style issues quickly
 139 | 1. **Code Quality Check** (After formatting): Use `simple-code-reviewer` for quick code
 140 |    quality checks, focusing on logic issues and code smells
 141 | 
 142 | ### Skills (Guided Development Workflows)
 143 | 
 144 | Skills provide step-by-step guides for common development tasks:
 145 | 
 146 | - `/add-dataset` - Dataset loader creation guide
 147 | - `/add-workflow` - Workflow implementation guide
 148 | - `/add-reward` - Reward function guide
 149 | - `/add-archon-model` - Archon engine model architecture guide
 150 | - `/debug-distributed` - Distributed debugging guide
 151 | - `/add-unit-tests` - Test development guide (NEW)
 152 | 
 153 | ### Commands (User-invoked Actions)
 154 | 
 155 | Commands perform specific actions when invoked:
 156 | 
 157 | - `/create-pr` - Rebase, squash commits, and create/update PR with intelligent messages
 158 | - `/gen-commit-msg` - Generate commit messages from staged changes
 159 | - `/review-pr` - Intelligent PR code review with dynamic agent allocation
 160 | - `/translate-doc-zh` - Translate English documentation to Chinese
 161 | 
 162 | ### Rules (Code Quality Standards)
 163 | 
 164 | Project-wide standards enforced across all code changes:
 165 | 
 166 | - `api-config.md` - Configuration dataclass design patterns
 167 | - `code-style.md` - Coding conventions beyond pre-commit hooks
 168 | - `distributed.md` - Distributed training patterns and constraints
 169 | - `testing.md` - Testing strategy and coverage requirements
```


---
## README.md

```
   1 | <h1 align="center">
   2 | <em>AReaL</em>: A Large-Scale Asynchronous Reinforcement Learning System
   3 | </h1>
   4 | 
   5 | <p align="center">
   6 | | <a href="https://arxiv.org/pdf/2505.24298"><b>Paper</b></a> | <a href="https://inclusionai.github.io/AReaL/"><b>Documentation</b></a> | <a href="https://inclusionai.github.io/AReaL/zh/"><b>中文文档</b></a> | <a href="https://deepwiki.com/inclusionAI/AReaL"><b>Ask DeepWiki</b></a> | <a href="https://huggingface.co/collections/inclusionAI/"><b>🤗 Models & Data</b></a> |
   7 | <a href="./assets/wechat_qrcode.png" target="_blank"><img src="./assets/wechat_icon.png" width="20" style="vertical-align: middle;"> <b>WeChat (微信) Group</b></a> |
   8 | </p>
   9 | 
  10 | <img align="right" alt="ReaL" src="/assets/logo.png" width="20%">
  11 | 
  12 | AReaL is an open-source **fully asynchronous** reinforcement learning training system
  13 | for large **reasoning and agentic models**, developed by members from Tsinghua IIIS and
  14 | the AReaL Team at Ant Group. Built upon the open-source project
  15 | [ReaLHF](https://github.com/openpsi-project/ReaLHF), we are fully committed to
  16 | open-source principles by providing the training details, data, and infrastructure
  17 | required to reproduce our results, along with the models themselves. AReaL aims to help
  18 | everyone build their own AI agents easily and affordably. Our team loves milk tea
  19 | because it's delicious, customizable, and affordable—we hope you enjoy our project just
  20 | as much as you'd enjoy real milk tea. Cheers!
  21 | 
  22 | **AReaL Highlights**
  23 | 
  24 | - ⚡ **Flexibility**: Seamless customization for
  25 |   [agentic RL](https://inclusionai.github.io/AReaL/en/tutorial/agentic_rl.html) and
  26 |   [online RL training](./examples/openclaw/) by simply replacing the `base_url`.
  27 | - 📈 **Scalability**: **Stable** fully asynchronous RL training with **industry-leading
  28 |   speed**.
  29 | - ✨ **Cutting-Edge Performance**: State-of-the-art [math](/blog/AReaL_v0_2.md),
  30 |   [coding](/blog/AReaL_v0_3.md), [search](https://github.com/inclusionAI/ASearcher), and
  31 |   [customer service](https://arxiv.org/abs/2601.22607) agents.
  32 | 
  33 | ## 📰 News
  34 | 
  35 | **\[2026/03/02\]** We provide [a complete example](./examples/openclaw/) to train your
  36 | own 🦞 OpenClaw agent by simply replacing the `base_url` and `api_key` with AReaL's RL
  37 | service - no complicated dependencies, no code changes, works with any agentic runtime!
  38 | 
  39 | **\[2026/02/06\]** We are delighted to introduce **AReaL-SEA**, a self-evolving data
  40 | synthesis engine. Combined with RL training on AReaL, the 235B MoE model surpasses GPT 5
  41 | and achieves comparable performance with Gemini 3.0 Pro on $\\tau^2$-bench! Check out
  42 | the [paper](https://arxiv.org/pdf/2601.22607),
  43 | [model](https://huggingface.co/inclusionAI/AReaL-SEA-235B-A22B),
  44 | [data](https://huggingface.co/datasets/inclusionAI/AReaL-tau2-data), and
  45 | [code](https://github.com/inclusionAI/AReaL/tree/main/examples/tau2).
  46 | 
  47 | **\[2026/01/15\]** Congrats to our friends at [CAMEL-AI](https://www.camel-ai.org/) for
  48 | open-sourcing [SETA](https://github.com/camel-ai/seta), their terminal agent RL project
  49 | trained with AReaL! Check out
  50 | [their training workflow](https://github.com/camel-ai/seta/tree/main/training/tbench_areal_workflow)
  51 | and the [announcement on X](https://x.com/guohao_li/status/2009678513574408636).
  52 | 
  53 | <details>
  54 | <summary><b>📋 Previous Releases</b></summary>
  55 | 
  56 | **\[2026/01/01\]** Happy New Year! Thanks to the outstanding contribution from
  57 | @HwVanICI, we are excited to officially announce stable support for AReaL training on
  58 | **Ascend NPU devices**! The code is actively maintained and continuously updated in the
  59 | [`ascend` branch](https://github.com/inclusionAI/AReaL/tree/ascend). Check out
  60 | [our documentation](https://inclusionai.github.io/AReaL/en/tutorial/installation_npu.html)
  61 | to get started, and feel free to report any issues!
  62 | 
  63 | **\[2025/08/30\]** Introducing ASearcher, a state-of-the-art search agent built with
  64 | AReaL's end-to-end asynchronous RL training. Check out the [paper](assets/paper.pdf) and
  65 | the [open-source repository](https://github.com/inclusionAI/ASearcher)!
  66 | 
  67 | **\[2025/07/31\] (AReaL-lite)** We introduce AReaL-lite, a **lightweight** version of
  68 | AReaL designed specifically for AI researchers and rapid prototyping. AReaL-lite
  69 | features an **algorithm-first** API design that prioritizes ease of use and algorithm
  70 | development, while natively supporting **fully asynchronous agentic RL**. With 80% fewer
  71 | lines of code, AReaL-lite maintains 90% of AReaL's performance and core functionality.
  72 | Check out [our AReaL-lite design documentation](/areal/README.md) and
  73 | [the quickstart guide](https://inclusionai.github.io/AReaL/en/tutorial/quickstart.html)
  74 | to begin your journey with **AReaL-lite**!
  75 | 
  76 | **\[2025/06/03\] (v0.3, boba²)** We release **boba²** (double-boba) for fully
  77 | asynchronous RL training, which achieves **2.77× speedup while delivering comparable or
  78 | superior training performance** compared to synchronous systems. Furthermore,
  79 | asynchronous RL significantly simplifies multi-turn agentic RL training setup! Check out
  80 | [our v0.3 overview blog](/blog/AReaL_v0_3.md) and the
  81 | [research paper](assets/paper.pdf).
  82 | 
  83 | **\[2025/03/31\] (v0.2, boba)** Introducing our milestone release—boba! Please call it
  84 | A-ReaL-boba! This release features significantly faster training with SGLang support and
  85 | state-of-the-art 7B and 32B models for mathematical reasoning. Check out our
  86 | [v0.2 technical blog](/blog/AReaL_v0_2.md).
  87 | 
  88 | **\[2025/02/24\] (v0.1)** Our initial release includes reproducible results for 1.5B and
  89 | 7B Large Reasoning Models (LRMs). Check out our
  90 | [v0.1 technical blog](/blog/AReaL_v0_1.md).
  91 | 
  92 | </details>
  93 | 
  94 | ## 🚀 Getting Started
  95 | 
  96 | First, install the package:
  97 | 
  98 | ```bash
  99 | git clone https://github.com/inclusionAI/AReaL
 100 | cd AReaL
 101 | pip install uv
 102 | uv sync --extra cuda  # installs training packages + SGLang (default inference backend)
 103 | ```
 104 | 
 105 | Our training scripts automatically download the required dataset (openai/gsm8k) and
 106 | model (Qwen/Qwen2-1.5B-Instruct). To run on a single node:
 107 | 
 108 | ```bash
 109 | python3 examples/math/gsm8k_rl.py --config examples/math/gsm8k_grpo.yaml scheduler.type=local
 110 | ```
 111 | 
 112 | To run on a Ray cluster with 2 nodes and 8 GPUs per node (remember to update paths in
 113 | the YAML file to point to your shared storage):
 114 | 
 115 | ```bash
 116 | python3 examples/math/gsm8k_rl.py --config examples/math/gsm8k_grpo.yaml \
 117 |   cluster.n_nodes=2 cluster.n_gpus_per_node=8 \
 118 |   scheduler.type=ray
 119 | ```
 120 | 
 121 | For comprehensive setup instructions, see
 122 | [our quickstart guide](https://inclusionai.github.io/AReaL/en/tutorial/quickstart.html).
 123 | 
 124 | ## 📚 Examples
 125 | 
 126 | ### Math & Reasoning
 127 | 
 128 | | Task                                                | Description                                                                                  | Performance                                                       |
 129 | | --------------------------------------------------- | -------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
 130 | | **[Math](examples/math/)**                          | GSM8K math reasoning with GRPO, PPO, DAPO, REINFORCE, RLOO, LitePPO, DR-GRPO, GSPO, and more | -                                                                 |
 131 | | **[Multi-Turn Math](examples/multi_turn_math/)**    | Multi-turn math agent with reward discounting across turns                                   | [Training Curve](examples/multi_turn_math/reward_curve.png)       |
 132 | | **[LoRA Math](examples/math/gsm8k_grpo_lora.yaml)** | Parameter-efficient math training with LoRA (SGLang/vLLM backends)                           | -                                                                 |
 133 | | **[Countdown](examples/countdown/)**                | Countdown numbers game with custom rewards                                                   | [Training Curve](examples/countdown/countdown_training_curve.png) |
 134 | 
 135 | ### Agentic RL
 136 | 
 137 | | Task                                                     | Description                                                            | Performance                                                                  |
 138 | | -------------------------------------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
 139 | | **[General Agent](examples/agent_workflow/)**            | General agentic training with any agentic frameworks                   | [Guide](docs/tutorial/agentic_rl.md)                                         |
 140 | | **[Tau2 Customer Service](examples/tau2/)**              | Customer service agent on Tau2-Bench (retail, airline, telecom)        | [Paper](https://arxiv.org/abs/2601.22607)                                    |
 141 | | **[Search Agent](examples/search_agent/)**               | End-to-end search agent with Tongyi-DeepResearch workflow              | [Training Curve](examples/search_agent/tongyi_deepresearch/reward_curve.png) |
 142 | | **[Tool-Integrated Reasoning](examples/tir/)**           | Multi-turn tool calling during reasoning (Python executor, calculator) | [Training Curve](examples/tir/figures/task_reward.png)                       |
 143 | | **[OpenAI Agents Integration](examples/openai_agents/)** | Integration with OpenAI Agents SDK for agentic workflows               | -                                                                            |
 144 | | **[CAMEL-AI Integration](examples/camel/)**              | Integration with CAMEL-AI framework for agentic RL                     | -                                                                            |
 145 | 
 146 | ### Vision-Language Models
 147 | 
 148 | | Task                                | Description                                               | Performance                                     |
 149 | | ----------------------------------- | --------------------------------------------------------- | ----------------------------------------------- |
 150 | | **[VLM](examples/vlm/)**            | Geometry3K and CLEVR Count 70K visual reasoning with GRPO | -                                               |
 151 | | **[VLM on NPU](examples/vlm_npu/)** | VLM training on Huawei NPU hardware                       | [Benchmark Results](examples/vlm_npu/README.md) |
 152 | 
 153 | ### Alignment & Infrastructure
 154 | 
 155 | | Task                                            | Description                                           | Performance                                       |
 156 | | ----------------------------------------------- | ----------------------------------------------------- | ------------------------------------------------- |
 157 | | **[RLHF Reward Modeling](examples/alignment/)** | Bradley-Terry reward modeling on Anthropic HH-RLHF    | [Training Curve](examples/alignment/rw_curve.png) |
 158 | | **[SkyPilot Deployment](examples/skypilot/)**   | Cloud deployment with SkyPilot (GCP, AWS, Kubernetes) | [Screenshots](examples/skypilot/README.md)        |
 159 | 
 160 | ## 🔧 Support Matrix
 161 | 
 162 | ### 🧠 Algorithms
 163 | 
 164 | All RL algorithms support both asynchronous and synchronous versions by setting
 165 | `max_head_offpolicyness=0`. See [Asynchronous RL Guide](docs/algorithms/async.md).
 166 | 
 167 | | Algorithm                | Documentation                                 | Paper                                          | Configuration                                                     |
 168 | | ------------------------ | --------------------------------------------- | ---------------------------------------------- | ----------------------------------------------------------------- |
 169 | | **GRPO**                 | [📖 Docs](docs/en/algorithms/grpo_series.md)  | [📄 Paper](https://arxiv.org/pdf/2402.03300)   | [🔗 GSM8K Example](examples/math/gsm8k_grpo.yaml)                 |
 170 | | **GSPO**                 | [📖 Docs](docs/en/algorithms/grpo_series.md)  | [📄 Paper](https://arxiv.org/abs/2507.18071)   | [🔗 GSM8K Example](examples/math/gsm8k_gspo.yaml)                 |
 171 | | **PPO**                  | [📖 Docs](docs/en/algorithms/grpo_series.md)  | [📄 Paper](https://arxiv.org/pdf/2203.02155)   | [🔗 GSM8K Example](examples/math/gsm8k_ppo.yaml)                  |
 172 | | **DAPO**                 | [📖 Docs](docs/en/algorithms/grpo_series.md)  | [📄 Paper](https://arxiv.org/abs/2503.14476)   | [🔗 GSM8K Example](examples/math/gsm8k_dapo_dynamic_bs.yaml)      |
 173 | | **LitePPO**              | [📖 Docs](docs/en/algorithms/grpo_series.md)  | [📄 Paper](https://arxiv.org/abs/2508.08221)   | [🔗 GSM8K Example](examples/math/gsm8k_liteppo.yaml)              |
 174 | | **Dr.GRPO**              | [📖 Docs](docs/en/algorithms/grpo_series.md)  | [📄 Paper](https://arxiv.org/abs/2503.20783)   | [🔗 GSM8K Example](examples/math/gsm8k_drgrpo.yaml)               |
 175 | | **REINFORCE++**          | -                                             | [📄 Paper](https://arxiv.org/pdf/2501.03262)   | [🔗 GSM8K Example](examples/math/gsm8k_reinforce.yaml)            |
 176 | | **RLOO**                 | [📖 Docs](docs/en/algorithms/grpo_series.md)  | [📄 Paper](https://arxiv.org/pdf/2402.14740v1) | [🔗 GSM8K Example](examples/math/gsm8k_rloo.yaml)                 |
 177 | | **SAPO**                 | [📖 Docs](docs/en/algorithms/grpo_series.md)  | [📄 Paper](https://arxiv.org/abs/2511.20347)   | [🔗 GSM8K Example](examples/math/gsm8k_sapo.yaml)                 |
 178 | | **M2PO**                 | [📖 Docs](docs/algorithms/m2po.md)            | [📄 Paper](https://arxiv.org/abs/2510.01161)   | [🔗 GSM8K Example](examples/math/gsm8k_m2po.yaml)                 |
 179 | | **RLHF Reward Modeling** | -                                             | -                                              | [🔗 RLHF Example](examples/alignment/)                            |
 180 | | **SFT**                  | -                                             | -                                              | [🔗 GSM8K Example](examples/math/gsm8k_sft.py)                    |
 181 | | **Distillation**         | [📖 Docs](docs/en/algorithms/distillation.md) | [📄 Paper](https://arxiv.org/pdf/2506.02208)   | [🔗 GSM8K Example](examples/distillation/gsm8k_grpo_distill.yaml) |
 182 | 
 183 | ### Models
 184 | 
 185 | | Model Family               | Megatron | PyTorch FSDP | PyTorch Archon | Notes                                                    |
 186 | | -------------------------- | -------- | ------------ | -------------- | -------------------------------------------------------- |
 187 | | **Qwen2/3**                | ✅       | ✅           | ✅             | -                                                        |
 188 | | **Qwen3-MoE**              | ✅       | ✅           | ✅             | -                                                        |
 189 | | **Qwen2.5-VL**             | ❌       | ✅           | ❌             | Vision-language model                                    |
 190 | | **Qwen3-VL**               | ❌       | ✅           | ❌             | Vision-language model                                    |
 191 | | **Gemma 3**                | ❌       | ✅           | ❌             | Vision-language model                                    |
 192 | | **Other Hugging Face LLM** | ❌       | ✅           | ❌             | Compatibility depending on the version of `transformers` |
 193 | 
 194 | Check the [AI Coding Assistant Guide](docs/reference/ai_assisted_dev.md) and
 195 | [Archon Reference](docs/tutorial/archon.md) for how to integrate new models into AReaL.
 196 | 
 197 | ### Training Backends
 198 | 
 199 | | Backend            | DP          | Tensor Parallel | Sequence Parallel within TP | Context Parallel | Pipeline Parallel | Expert Parallel | 1D Sequence Packing | LoRA |
 200 | | ------------------ | ----------- | --------------- | --------------------------- | ---------------- | ----------------- | --------------- | ------------------- | ---- |
 201 | | **Megatron**       | ✅ (ZeRO-1) | ✅              | ✅                          | ✅               | ✅                | ✅              | ✅                  | ❌   |
 202 | | **PyTorch FSDP**   | ✅ (FSDP2)  | ✅              | ✅                          | ✅               | ❌                | ❌              | ✅                  | ✅   |
 203 | | **PyTorch Archon** | ✅ (FSDP2)  | ✅              | ✅                          | ✅               | ✅                | ✅              | ✅                  | ❌   |
 204 | 
 205 | ### Inference Backends
 206 | 
 207 | | Backend    | Tensor Parallel | Context Parallel | Pipeline Parallel | Data Parallel Attention | Expert Parallel |
 208 | | ---------- | --------------- | ---------------- | ----------------- | ----------------------- | --------------- |
 209 | | **vLLM**   | ✅              | ❓               | ✅                | ❓                      | ❓              |
 210 | | **SGLang** | ✅              | ❌               | ❌                | ✅                      | ✅              |
 211 | 
 212 | ## 📖 Resources
 213 | 
 214 | ### Tutorial
 215 | 
 216 | - [Installation](docs/en/tutorial/installation.md)
 217 | - [Quickstart](docs/en/tutorial/quickstart.md)
 218 | - [Agentic RL](docs/en/tutorial/agentic_rl.md)
 219 | - [Evaluation](docs/en/tutorial/eval.md)
 220 | - [Large MoE with Megatron](docs/en/tutorial/megatron.md)
 221 | - [Large MoE with PyTorch Archon](docs/en/tutorial/archon.md)
 222 | 
 223 | ### Code Walkthrough
 224 | 
 225 | - [Running GRPO on GSM8K dataset](docs/en/tutorial/gsm8k_grpo.md)
 226 | 
 227 | ### Best Practices
 228 | 
 229 | - [Improving Algorithm Performance](docs/en/best_practices/algo_perf.md)
 230 | - [Agent Workflow Best Practices](docs/en/best_practices/workflow.md)
 231 | - [Debugging](docs/en/best_practices/debugging.md)
 232 | - [Handling OOM Issues](docs/en/best_practices/handling_oom.md)
 233 | - [Performance Profiling](docs/en/best_practices/perf_profiling.md)
 234 | 
 235 | ### Customization
 236 | 
 237 | - [Customize Dataset](docs/en/customization/dataset.md)
 238 | - [Customize Agentic/RVLR Rollout Workflows](docs/en/customization/agent.md)
 239 | 
 240 | ### Algorithms
 241 | 
 242 | - [Asynchronous RL Explained](docs/en/algorithms/async.md)
 243 | - [PPO, GRPO, and Related Algorithms](docs/en/algorithms/grpo_series.md)
 244 | - [M2PO](docs/en/algorithms/m2po.md)
 245 | 
 246 | ### Reference
 247 | 
 248 | - [CLI Configurations](docs/en/cli_reference.md)
 249 | - [Checkpointing](docs/en/reference/checkpointing.md)
 250 | - [Metrics Tracking](docs/en/reference/metrics_tracking.md)
 251 | - [Allocation Mode](docs/en/reference/alloc_mode.md)
 252 | - [Rollout Workflow](docs/en/reference/rollout_workflow.md)
 253 | - [Agent Workflow](docs/en/reference/agent_workflow.md)
 254 | - [AI-Assisted Development](docs/en/reference/ai_assisted_dev.md)
 255 | 
 256 | ## 🤝 Contributing
 257 | 
 258 | We warmly welcome contributions from the community! Whether you're fixing bugs, adding
 259 | features, improving documentation, or helping others, your contribution is valued.
 260 | Please check our **[Contributing Guide](CONTRIBUTING.md)** for detailed information.
 261 | 
 262 | ```bash
 263 | # Fork and clone the repository
 264 | git clone https://github.com/YOUR-USERNAME/AReaL
 265 | cd AReaL
 266 | 
 267 | # Install uv and sync dependencies
 268 | pip install uv
 269 | # Use `--extra cuda` on Linux with CUDA (installs training packages + SGLang)
 270 | uv sync --extra cuda --group dev
 271 | # For vLLM instead: uv sync --extra cuda-train --extra vllm --group dev
 272 | # Or without CUDA support
 273 | # uv sync --group dev
 274 | 
 275 | # Set up pre-commit hooks (formatting, linting, commit message checks)
 276 | pre-commit install --install-hooks
 277 | 
 278 | # Make changes
 279 | git checkout -b feat/gpt-o5
 280 | git add .
 281 | # `git commit` will automatically check your files and commit messages
 282 | git commit -m "feat: implement gpt-o5 training loop"
 283 | git push
 284 | ```
 285 | 
 286 | ## 🗺️ Future Roadmap
 287 | 
 288 | - **[Full Roadmap](ROADMAP.md)**
 289 | - **[2025 Q4 Roadmap](https://github.com/inclusionAI/AReaL/issues/542)**
 290 | 
 291 | AReaL is under active development with planned minor releases weekly and major releases
 292 | monthly. We warmly welcome community engagement and contributions. We are also
 293 | **actively hiring interns and full-time employees** with open positions in both the US
 294 | and China.
 295 | 
 296 | ## 🙏 Acknowledgments
 297 | 
 298 | We gratefully acknowledge that major contributors are from the AReaL Team at the
 299 | Institute for Interdisciplinary Information Sciences (IIIS), Tsinghua University and Ant
 300 | Group.
 301 | 
 302 | We have also received invaluable assistance from the following groups (listed
 303 | alphabetically):
 304 | 
 305 | - The Data Intelligence Lab at Ant Research for their data support
 306 | 
 307 | - @HwVanICI for support on vLLM, LoRA, NPU integration, and more
 308 | 
 309 | - The [Relaxed System Lab](https://github.com/Relaxed-System-Lab) at HKUST for seamless
 310 |   collaboration on numerous system-related aspects
 311 | 
 312 | - The [SGLang team](https://github.com/sgl-project/sglang) for supporting custom weight
 313 |   update features and their contributions during AReaL-lite development
 314 | 
 315 | - The Super Computing Technology (SCT) team at Ant Group for their expertise in
 316 |   large-scale cluster operations and maintenance
 317 | 
 318 | - Special thanks to @Lyken17 for providing valuable suggestions throughout the API
 319 |   design process
 320 | 
 321 | We also deeply appreciate all pioneering work from the community, particularly the
 322 | [ReaLHF](https://github.com/openpsi-project/ReaLHF) project from OpenPsi Inc. and other
 323 | outstanding projects, including but not limited to
 324 | [DeepScaleR](https://github.com/agentica-project/deepscaler),
 325 | [Open-Reasoner-Zero](https://github.com/Open-Reasoner-Zero/Open-Reasoner-Zero/tree/main),
 326 | [OpenRLHF](https://github.com/OpenRLHF/OpenRLHF),
 327 | [VeRL](https://github.com/volcengine/verl),
 328 | [SGLang](https://github.com/sgl-project/sglang), [QwQ](https://github.com/QwenLM/QwQ),
 329 | [Light-R1](https://github.com/Qihoo360/Light-R1), and
 330 | [DAPO](https://github.com/BytedTsinghua-SIA/DAPO).
 331 | 
 332 | ## 📄 Citation
 333 | 
 334 | ```bibtex
 335 | @inproceedings{mei2025real,
 336 |   author       = {Mei, Zhiyu and Fu, Wei and Li, Kaiwei and Wang, Guangju and Zhang, Huanchen and Wu, Yi},
 337 |   title        = {ReaL: Efficient RLHF Training of Large Language Models with Parameter Reallocation},
 338 |   booktitle    = {Proceedings of the Eighth Conference on Machine Learning and Systems,
 339 |                   MLSys 2025, Santa Clara, CA, USA, May 12-15, 2025},
 340 |   publisher    = {mlsys.org},
 341 |   year         = {2025},
 342 | }
 343 | ```
 344 | 
 345 | ```bibtex
 346 | @misc{fu2025areal,
 347 |       title={AReaL: A Large-Scale Asynchronous Reinforcement Learning System for Language Reasoning},
 348 |       author={Wei Fu and Jiaxuan Gao and Xujie Shen and Chen Zhu and Zhiyu Mei and Chuyi He and Shusheng Xu and Guo Wei and Jun Mei and Jiashu Wang and Tongkai Yang and Binhang Yuan and Yi Wu},
 349 |       year={2025},
 350 |       eprint={2505.24298},
 351 |       archivePrefix={arXiv},
 352 |       primaryClass={cs.LG},
 353 |       url={https://arxiv.org/abs/2505.24298},
 354 | }
 355 | ```
```
