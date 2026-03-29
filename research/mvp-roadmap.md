# Agent-Native SWE Benchmark: Research Findings & MVP Roadmap

You have uncovered a structural blind spot in the current multi-million-dollar race to build Software Engineering (SWE) environments. While major labs are optimizing for sheer volume and unit-test execution, they are entirely missing **Contextual Instruction Adherence**—how AI agents interact with modern, human-written rule files (`.cursorrules`, `CLAUDE.md`, `AGENTS.md`) during training.

Here is the consolidated research brief and the architectural roadmap to build your MVP codebase.

---

## 1. Landscape Analysis: The "White Space" Verified

The following table summarizes the state-of-the-art SWE benchmarks and precisely why your proposed dataset remains completely novel.

| Benchmark / Project | Core Focus & Scale | Why It Misses the "Agent-Native" White Space |
| :--- | :--- | :--- |
| **SWE-RL** (Meta, Feb 2025) | 4.6M repos mined | **Too Old:** Data cutoff is Aug 2024, missing the late-2025 explosion of agent configs. |
| **SWE-rebench V2** (Nebius) | 32K tasks, 20 languages | **No Context Filtering:** Mines historical PRs based on language diversity, completely ignoring repository rule files. |
| **daVinci-Env** (GAIR-NLP) | 45K environments | **Basic Filtering:** Only filters by GitHub stars (>5). No metadata or file-content checks. |
| **SWE-Next** (Mar 2026) | 2.3K tasks | **Execution-Only:** Filters purely for base/merged commit pairs that fix a broken test. No rule-adherence checks. |
| **SWE-Universe** (Alibaba) | 800K environments | **Blind Reward Signal:** Agents are rewarded solely for passing unit tests, even if they explicitly violate repo guidelines. |
| **SWE-Gym** (NeurIPS 2025) | 2.4K tasks | **Ecosystem Bias:** Limited to 11 legacy Python repos (e.g., Django, SymPy) which do not use modern agent config files. |
| **SWE-Smith** (SWE-bench) | 50K synthetic tasks | **Synthetic:** Uses AST parsing to artificially break tests. Does not use real-world PRs or human-written instructions. |

---

## 2. MVP Codebase: Next Steps & Architecture

To prove this concept, you do not need millions of environments. A high-quality MVP of **100 to 500 validated tasks** will be enough to publish or demonstrate the training-time impact of agent files.

Here is the step-by-step blueprint for your codebase.

### Phase 1: The Targeted Mining Pipeline
Shift focus away from legacy Python and target the ecosystems where agent instructions are actually used.
* **Target Languages:** JavaScript, TypeScript, React, Next.js, and modern Python (FastAPI/Pydantic).
* **The Query:** Use the GitHub GraphQL API to fetch PRs merged **after June 2025**.
* **The Filter:** Discard any repository that does not contain one of the following in its root directory at the time of the PR:
  * `.cursorrules`
  * `CLAUDE.md`
  * `AGENTS.md`
  * `.github/copilot-instructions.md`
* **Output:** A JSON/JSONL dataset of `{repo_name, commit_base, commit_merged, agent_config_content, pr_description}`.

### Phase 2: The Dual-Reward Evaluation Engine
This is your core differentiator. The environment must calculate a score based on two distinct axes.
* **Axis A: Execution (The Standard)**
  * Spin up the Docker container for the repo.
  * Apply the agent's generated patch.
  * Run the specific test command for that PR. Did it pass? (Binary: 0 or 1).
* **Axis B: Adherence (The Novelty)**
  * Extract the rules from the repo's agent config.
  * Evaluate the agent's patch against these specific rules (e.g., "Did it use `fetch` instead of `axios` as mandated?").
  * This is your new metric: **Instruction Compliance Rate (ICR)**.

### Phase 3: Environment Scaffolding (Docker)
Do not build your own sandbox from scratch. Fork or heavily borrow from existing open-source frameworks to handle the execution layer.
* **Leverage Existing Tools:** Use the open-source runner from `SWE-bench` or the recently released `SWE-Universe` execution engine.
* **Modification:** Inject the `agent_config` file content into the system prompt of the agent you are evaluating, exactly as a modern IDE (like Cursor or Windsurf) does at inference time.

---

To tackle Phase 2 effectively, the system needs to grade the "Adherence" axis. Will you build a static analysis tool (AST parsing) to verify rule compliance, or are you planning to use an LLM-as-a-judge (e.g., GPT-4o or Claude 3.5 Sonnet) to read the diff and grade if it followed the `.cursorrules`?