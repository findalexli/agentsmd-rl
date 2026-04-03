# Agent-Native SWE Benchmark: Research Findings & MVP Roadmap over tonight.

You have uncovered a structural blind spot in the current multi-million-dollar race to build Software Engineering (SWE) environments. While major labs are optimizing for sheer volume and unit-test execution, they are entirely missing **Contextual Instruction Adherence**—how AI agents interact with modern, human-written rule files (`.cursorrules`, `CLAUDE.md`, `AGENTS.md`) during training.

Here is the consolidated research brief and the architectural roadmap to build your MVP codebase, lets aim for at least a couple hundred task using the next plan. 

---

## 1. Landscape Analysis: The "White Space" Verified

The following table summarizes the state-of-the-art SWE benchmarks and precisely why your proposed dataset remains completely novel. But their sourcing, pr filtering, are helpful. Reminder, i alredy logged into github in the comand line, which you could use in gh native api to do things


| Benchmark / Project         | Core Focus & Scale      | Why It Misses the "Agent-Native" White Space                                                                                 |
| --------------------------- | ----------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **SWE-RL** (Meta, Feb 2025) | 4.6M repos mined        | **Too Old:** Data cutoff is Aug 2024, missing the late-2025 explosion of agent configs.                                      |
| **SWE-rebench V2** (Nebius) | 32K tasks, 20 languages | **No Context Filtering:** Mines historical PRs based on language diversity, completely ignoring repository rule files.       |
| **daVinci-Env** (GAIR-NLP)  | 45K environments        | **Basic Filtering:** Only filters by GitHub stars (>5). No metadata or file-content checks.                                  |
| **SWE-Next** (Mar 2026)     | 2.3K tasks              | **Execution-Only:** Filters purely for base/merged commit pairs that fix a broken test. No rule-adherence checks.            |
| **SWE-Universe** (Alibaba)  | 800K environments       | **Blind Reward Signal:** Agents are rewarded solely for passing unit tests, even if they explicitly violate repo guidelines. |
| **SWE-Gym** (NeurIPS 2025)  | 2.4K tasks              | **Ecosystem Bias:** Limited to 11 legacy Python repos (e.g., Django, SymPy) which do not use modern agent config files.      |
| **SWE-Smith** (SWE-bench)   | 50K synthetic tasks     | **Synthetic:** Uses AST parsing to artificially break tests. Does not use real-world PRs or human-written instructions.      |


## Those prior work do provide some guildelines on what might be a good PR to use here, 
  probably use some heurrics to filter for some github issues. you should total study how those prior work filter it down. 

## 2. MVP Codebase: Next Steps & Architecture

To prove this concept, you do not need millions of environments. A high-quality MVP of **100 to 500 validated tasks** will be enough to publish or demonstrate the training-time impact of agent files.

Here is the step-by-step blueprint for your codebase.

### Phase 1: The Targeted Mining Pipeline

Shift focus away from legacy Python and target the ecosystems where agent instructions are actually used.

- **Target Languages:** JavaScript, TypeScript, React, Next.js, and modern Python (FastAPI/Pydantic).
- **The Query:** Use the GitHub GraphQL API to fetch PRs merged **in the past three month**.
- **The Filter:** Discard any repository that does not contain one of the following in its root directory at the time of the PR:
  - `.cursorrules`
  - `CLAUDE.md`
  - `AGENTS.md`
- **Output:** A JSON/JSONL dataset of `{repo_name, commit_base, commit_merged, agent_config_content, pr_description}`.

To start, you can use the following repos

Lets use the following repos
Python

1. sglang (we alredy have)
2. vllm (we already have)
3. skyrl
4. tinker (thinking machine)
5. SLIME
6. OpenCode
7. Prime-RL/Verifies
8. OpenClaw (but you need to be extra careful, lots of vibecoded)
9. zeroclaw (also super careful, entire repo vibecoded)
10. huggingface/transformers
11. Areal.
12. [https://github.com/gradio-app/gradio](https://github.com/gradio-app/gradio)
13. [https://github.com/pytorch/pytorch](https://github.com/pytorch/pytorch) (maybe triple check as pytorch might be too big?)

Non-Python

[https://github.com/oven-sh/bun](https://github.com/oven-sh/bun)
[https://github.com/astral-sh/ruff](https://github.com/astral-sh/ruff)
[https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)
[https://github.com/vercel/next.js/](https://github.com/vercel/next.js/)
[https://github.com/NVIDIA/NemoClaw](https://github.com/NVIDIA/NemoClaw)

### Phase 2: The Dual-Reward Evaluation Engine

After filtering down the PRs, you need to refer to  /home/alex/agentsmd-rl/CLAUDE.md for the exact plan. 

Each PR might need a whole army of subagents to help build the docker appropiately, validate-task, make sure the test make sense, and also research the right rubrics (attributing to the right markdown is not trivial at all!), and the right static tests, fail to pass and pass to pass tests. 

I want you to run the actual thing e2e. To do this at scale, we use the harbor framework calling claude code as harness, and use Haiku 4.5 as the executor so it is fast, cheap, and we could observe the actual tracteory.json as output to help debug report and debug the rubrics, tests, etc. 

I wanna wake up in the next 8 hours to at lest >100 tasks, if not around 500 engineered from those mentioned repos, and alredy have e2e runs, grading schema with all the programmatic tests/rubrics from agents, etc. 

But be careful that my machine have limited storage for Docker and overall, so we might need to preriodly monitor and clean the docker storage. 