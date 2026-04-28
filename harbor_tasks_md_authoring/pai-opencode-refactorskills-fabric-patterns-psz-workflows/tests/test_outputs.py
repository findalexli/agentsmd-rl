"""Behavioral checks for pai-opencode-refactorskills-fabric-patterns-psz-workflows (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pai-opencode")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/suggest_pattern/user_updated.md')
    assert 'Summarizes an academic paper by detailing its title, authors, technical approach, distinctive features, experimental setup, results, advantages, limitations, and conclusion in a clear, structured form' in text, "expected to find: " + 'Summarizes an academic paper by detailing its title, authors, technical approach, distinctive features, experimental setup, results, advantages, limitations, and conclusion in a clear, structured form'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/suggest_pattern/user_updated.md')
    assert 'Analyse a historical battle, offering in-depth insights into strategic decisions, strengths, weaknesses, tactical approaches, logistical factors, pivotal moments, and consequences for a comprehensive ' in text, "expected to find: " + 'Analyse a historical battle, offering in-depth insights into strategic decisions, strengths, weaknesses, tactical approaches, logistical factors, pivotal moments, and consequences for a comprehensive '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/suggest_pattern/user_updated.md')
    assert "Summarizes AI chat prompts by describing the primary function, unique approach, and expected output in a concise paragraph. The summary is focused on the prompt's purpose without unnecessary details o" in text, "expected to find: " + "Summarizes AI chat prompts by describing the primary function, unique approach, and expected output in a concise paragraph. The summary is focused on the prompt's purpose without unnecessary details o"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize/dmiessler/summarize/system.md')
    assert 'Take a step back and think step by step about how to achieve the best result possible as defined in the steps below. You have a lot of freedom to make this work well.' in text, "expected to find: " + 'Take a step back and think step by step about how to achieve the best result possible as defined in the steps below. You have a lot of freedom to make this work well.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize/dmiessler/summarize/system.md')
    assert '1. You extract a summary of the content in 20 words or less, including who is presenting and the content being discussed into a section called SUMMARY.' in text, "expected to find: " + '1. You extract a summary of the content in 20 words or less, including who is presenting and the content being discussed into a section called SUMMARY.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize/dmiessler/summarize/system.md')
    assert '3. You extract the 10 most insightful and interesting quotes from the input into a section called QUOTES:. Use the exact quote text from the input.' in text, "expected to find: " + '3. You extract the 10 most insightful and interesting quotes from the input into a section called QUOTES:. Use the exact quote text from the input.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize/dmiessler/summarize/user.md')
    assert '.opencode/skills/Utilities/Fabric/Patterns/summarize/dmiessler/summarize/user.md' in text, "expected to find: " + '.opencode/skills/Utilities/Fabric/Patterns/summarize/dmiessler/summarize/user.md'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize/system.md')
    assert '- Output the 10 most important points of the content as a list with no more than 16 words per point into a section called MAIN POINTS:.' in text, "expected to find: " + '- Output the 10 most important points of the content as a list with no more than 16 words per point into a section called MAIN POINTS:.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize/system.md')
    assert '- Combine all of your understanding of the content into a single, 20-word sentence in a section called ONE SENTENCE SUMMARY:.' in text, "expected to find: " + '- Combine all of your understanding of the content into a single, 20-word sentence in a section called ONE SENTENCE SUMMARY:.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize/system.md')
    assert 'You are an expert content summarizer. You take content in and output a Markdown formatted summary using the format below.' in text, "expected to find: " + 'You are an expert content summarizer. You take content in and output a Markdown formatted summary using the format below.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize/user.md')
    assert '.opencode/skills/Utilities/Fabric/Patterns/summarize/user.md' in text, "expected to find: " + '.opencode/skills/Utilities/Fabric/Patterns/summarize/user.md'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_board_meeting/system.md')
    assert 'You are a professional meeting secretary specializing in corporate governance documentation. Your purpose is to convert raw board meeting transcripts into polished, formal meeting notes that meet corp' in text, "expected to find: " + 'You are a professional meeting secretary specializing in corporate governance documentation. Your purpose is to convert raw board meeting transcripts into polished, formal meeting notes that meet corp'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_board_meeting/system.md')
    assert '- Read through the entire transcript to understand the meeting flow and key topics' in text, "expected to find: " + '- Read through the entire transcript to understand the meeting flow and key topics'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_board_meeting/system.md')
    assert '- Meeting Type: [Regular Board Meeting/Special Board Meeting/Committee Meeting]' in text, "expected to find: " + '- Meeting Type: [Regular Board Meeting/Special Board Meeting/Committee Meeting]'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_debate/system.md')
    assert 'You are a hyper-intelligent ASI with a 1,143 IQ. You excel at analyzing debates and/or discussions and determining the primary disagreement the parties are having, and summarizing them concisely.' in text, "expected to find: " + 'You are a hyper-intelligent ASI with a 1,143 IQ. You excel at analyzing debates and/or discussions and determining the primary disagreement the parties are having, and summarizing them concisely.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_debate/system.md')
    assert "- Output the second person's (use their name) MIND-CHANGING EVIDENCE section with up to 10 15-word bullet points of the evidence the second party would accept to change their mind." in text, "expected to find: " + "- Output the second person's (use their name) MIND-CHANGING EVIDENCE section with up to 10 15-word bullet points of the evidence the second party would accept to change their mind."[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_debate/system.md')
    assert "- Output the first person's (use their name) MIND-CHANGING EVIDENCE section with up to 10 15-word bullet points of the evidence the first party would accept to change their mind." in text, "expected to find: " + "- Output the first person's (use their name) MIND-CHANGING EVIDENCE section with up to 10 15-word bullet points of the evidence the first party would accept to change their mind."[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_git_changes/system.md')
    assert '- Output a 20-word intro sentence that says something like, "In the last 7 days, we\'ve made some amazing updates to our project focused around $character of the updates$."' in text, "expected to find: " + '- Output a 20-word intro sentence that says something like, "In the last 7 days, we\'ve made some amazing updates to our project focused around $character of the updates$."'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_git_changes/system.md')
    assert 'You are an expert project manager and developer, and you specialize in creating super clean updates for what changed in a GitHub project in the last 7 days.' in text, "expected to find: " + 'You are an expert project manager and developer, and you specialize in creating super clean updates for what changed in a GitHub project in the last 7 days.'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_git_changes/system.md')
    assert '- Create a section called CHANGES with a set of 10-word bullets that describe the feature changes and updates.' in text, "expected to find: " + '- Create a section called CHANGES with a set of 10-word bullets that describe the feature changes and updates.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_git_diff/system.md')
    assert '- You only describe your changes in imperative mood, e.g. "make xyzzy do frotz" instead of "[This patch] makes xyzzy do frotz" or "[I] changed xyzzy to do frotz", as if you are giving orders to the co' in text, "expected to find: " + '- You only describe your changes in imperative mood, e.g. "make xyzzy do frotz" instead of "[This patch] makes xyzzy do frotz" or "[I] changed xyzzy to do frotz", as if you are giving orders to the co'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_git_diff/system.md')
    assert '- Use conventional commits - i.e. prefix the commit title with "chore:" (if it\'s a minor change like refactoring or linting), "feat:" (if it\'s a new feature), "fix:" if its a bug fix, "docs:" if it is' in text, "expected to find: " + '- Use conventional commits - i.e. prefix the commit title with "chore:" (if it\'s a minor change like refactoring or linting), "feat:" (if it\'s a new feature), "fix:" if its a bug fix, "docs:" if it is'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_git_diff/system.md')
    assert "- the full list of commit prefixes are: 'build',  'chore',  'ci',  'docs',  'feat',  'fix',  'perf',  'refactor',  'revert',  'style', 'test'." in text, "expected to find: " + "- the full list of commit prefixes are: 'build',  'chore',  'ci',  'docs',  'feat',  'fix',  'perf',  'refactor',  'revert',  'style', 'test'."[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_lecture/system.md')
    assert '00:00:00 Members-only Forum Access 00:00:10 Live Hacking Demo 00:00:26 Ideas vs. Book 00:00:30 Meeting Will Smith 00:00:44 How to Influence Others 00:01:34 Learning by Reading 00:58:30 Writing With Pu' in text, "expected to find: " + '00:00:00 Members-only Forum Access 00:00:10 Live Hacking Demo 00:00:26 Ideas vs. Book 00:00:30 Meeting Will Smith 00:00:44 How to Influence Others 00:01:34 Learning by Reading 00:58:30 Writing With Pu'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_lecture/system.md')
    assert "[02:17:43.120 --> 02:17:49.200] same way. I'll just say the same. And I look forward to hearing the response to my job application [02:17:49.200 --> 02:17:55.040] that I've submitted. Oh, you're accep" in text, "expected to find: " + "[02:17:43.120 --> 02:17:49.200] same way. I'll just say the same. And I look forward to hearing the response to my job application [02:17:49.200 --> 02:17:55.040] that I've submitted. Oh, you're accep"[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_lecture/system.md')
    assert 'Take a step back and think step-by-step about how you would do this. You would probably start by "watching" the video (via the transcript) and taking notes on each definition were in the lecture, beca' in text, "expected to find: " + 'Take a step back and think step-by-step about how you would do this. You would probably start by "watching" the video (via the transcript) and taking notes on each definition were in the lecture, beca'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_legislation/system.md')
    assert '5. In a section called CYNICAL CHARACTERIZATION, capture the parts of the bill that are likely to be controversial to the opposing side, and/or that are being downplayed by the submitting party becaus' in text, "expected to find: " + '5. In a section called CYNICAL CHARACTERIZATION, capture the parts of the bill that are likely to be controversial to the opposing side, and/or that are being downplayed by the submitting party becaus'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_legislation/system.md')
    assert "3. In a section called POSITIVE CHARACTERIZATION, capture how the submitting party is trying to make the proposal look, i.e., the positive spin they're putting on it. Give this as a set of 15-word bul" in text, "expected to find: " + "3. In a section called POSITIVE CHARACTERIZATION, capture how the submitting party is trying to make the proposal look, i.e., the positive spin they're putting on it. Give this as a set of 15-word bul"[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_legislation/system.md')
    assert '2. Identify the tricky parts of the proposal or law that might be getting underplayed by the group who submitted it. E.g., hidden policies, taxes, fees, loopholes, the cancelling of programs, etc.' in text, "expected to find: " + '2. Identify the tricky parts of the proposal or law that might be getting underplayed by the group who submitted it. E.g., hidden policies, taxes, fees, loopholes, the cancelling of programs, etc.'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_meeting/system.md')
    assert 'You are an AI assistant specialized in analyzing meeting transcripts and extracting key information. Your goal is to provide comprehensive yet concise summaries that capture the essential elements of ' in text, "expected to find: " + 'You are an AI assistant specialized in analyzing meeting transcripts and extracting key information. Your goal is to provide comprehensive yet concise summaries that capture the essential elements of '[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_meeting/system.md')
    assert '- Extract 10-20 of the most important discussion points from the meeting into a section called KEY POINTS. Focus on core topics, debates, and significant ideas discussed.' in text, "expected to find: " + '- Extract 10-20 of the most important discussion points from the meeting into a section called KEY POINTS. Focus on core topics, debates, and significant ideas discussed.'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_meeting/system.md')
    assert '- Extract all action items and assignments mentioned in the meeting into a section called TASKS. Include responsible parties and deadlines where specified.' in text, "expected to find: " + '- Extract all action items and assignments mentioned in the meeting into a section called TASKS. Include responsible parties and deadlines where specified.'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_micro/system.md')
    assert '- Output the 3 most important points of the content as a list with no more than 12 words per point into a section called MAIN POINTS:.' in text, "expected to find: " + '- Output the 3 most important points of the content as a list with no more than 12 words per point into a section called MAIN POINTS:.'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_micro/system.md')
    assert '- Combine all of your understanding of the content into a single, 20-word sentence in a section called ONE SENTENCE SUMMARY:.' in text, "expected to find: " + '- Combine all of your understanding of the content into a single, 20-word sentence in a section called ONE SENTENCE SUMMARY:.'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_micro/system.md')
    assert 'You are an expert content summarizer. You take content in and output a Markdown formatted summary using the format below.' in text, "expected to find: " + 'You are an expert content summarizer. You take content in and output a Markdown formatted summary using the format below.'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_micro/user.md')
    assert '.opencode/skills/Utilities/Fabric/Patterns/summarize_micro/user.md' in text, "expected to find: " + '.opencode/skills/Utilities/Fabric/Patterns/summarize_micro/user.md'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_paper/README.md')
    assert 'The experimental analysis is based on simulations that explore the impact of frequency, line of sight (LoS) distance, and burial depth of transceivers within the paint on path loss and channel capacit' in text, "expected to find: " + 'The experimental analysis is based on simulations that explore the impact of frequency, line of sight (LoS) distance, and burial depth of transceivers within the paint on path loss and channel capacit'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_paper/README.md')
    assert 'The study employs a comprehensive channel model to assess the communication capabilities of nano-devices embedded in paint. This model considers multipath communication strategies, including direct wa' in text, "expected to find: " + 'The study employs a comprehensive channel model to assess the communication capabilities of nano-devices embedded in paint. This model considers multipath communication strategies, including direct wa'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_paper/README.md')
    assert 'The proposed IoP approach offers several advantages, including the potential for seamless integration of communication networks into building structures without affecting aesthetics, and the ability t' in text, "expected to find: " + 'The proposed IoP approach offers several advantages, including the potential for seamless integration of communication networks into building structures without affecting aesthetics, and the ability t'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_paper/system.md')
    assert 'Provide a detailed explanation of the methodology used in the research. Focus on describing how the study was conducted, including any specific techniques, models, or algorithms employed. Avoid delvin' in text, "expected to find: " + 'Provide a detailed explanation of the methodology used in the research. Focus on describing how the study was conducted, including any specific techniques, models, or algorithms employed. Avoid delvin'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_paper/system.md')
    assert 'Concisely discuss the strengths of the proposed approach, including any benefits it offers over existing methods. Also, address its limitations or potential drawbacks, providing a balanced view of its' in text, "expected to find: " + 'Concisely discuss the strengths of the proposed approach, including any benefits it offers over existing methods. Also, address its limitations or potential drawbacks, providing a balanced view of its'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_paper/system.md')
    assert 'Identify and elaborate on what sets this research apart from other studies in the same field. Highlight any novel techniques, unique applications, or innovative methodologies that contribute to its di' in text, "expected to find: " + 'Identify and elaborate on what sets this research apart from other studies in the same field. Highlight any novel techniques, unique applications, or innovative methodologies that contribute to its di'[:80]


def test_signal_42():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_paper/user.md')
    assert '.opencode/skills/Utilities/Fabric/Patterns/summarize_paper/user.md' in text, "expected to find: " + '.opencode/skills/Utilities/Fabric/Patterns/summarize_paper/user.md'[:80]


def test_signal_43():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_prompt/system.md')
    assert "- The first sentence should summarize the main purpose. Begin with a verb and describe the primary function of the prompt. Use the present tense and active voice. Avoid using the prompt's name in the " in text, "expected to find: " + "- The first sentence should summarize the main purpose. Begin with a verb and describe the primary function of the prompt. Use the present tense and active voice. Avoid using the prompt's name in the "[:80]


def test_signal_44():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_prompt/system.md')
    assert 'You are an expert prompt summarizer. You take AI chat prompts in and output a concise summary of the purpose of the prompt using the format below.' in text, "expected to find: " + 'You are an expert prompt summarizer. You take AI chat prompts in and output a concise summary of the purpose of the prompt using the format below.'[:80]


def test_signal_45():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_prompt/system.md')
    assert 'Take a deep breath and think step by step about how to best accomplish this goal using the following steps.' in text, "expected to find: " + 'Take a deep breath and think step by step about how to best accomplish this goal using the following steps.'[:80]


def test_signal_46():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_pull-requests/system.md')
    assert '- Rewrite the top pull request items to be a more human readable version of what was submitted, e.g., "delete api key" becomes "Removes an API key from the repo."' in text, "expected to find: " + '- Rewrite the top pull request items to be a more human readable version of what was submitted, e.g., "delete api key" becomes "Removes an API key from the repo."'[:80]


def test_signal_47():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_pull-requests/system.md')
    assert "Most PRs on this repo have to do with troubleshooting the app's dependencies, cleaning up documentation, and adding features to the client." in text, "expected to find: " + "Most PRs on this repo have to do with troubleshooting the app's dependencies, cleaning up documentation, and adding features to the client."[:80]


def test_signal_48():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_pull-requests/system.md')
    assert '1. Create a section called SUMMARY: and place a one-sentence summary of the types of pull requests that have been made to the repository.' in text, "expected to find: " + '1. Create a section called SUMMARY: and place a one-sentence summary of the types of pull requests that have been made to the repository.'[:80]


def test_signal_49():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_pull-requests/user.md')
    assert '.opencode/skills/Utilities/Fabric/Patterns/summarize_pull-requests/user.md' in text, "expected to find: " + '.opencode/skills/Utilities/Fabric/Patterns/summarize_pull-requests/user.md'[:80]


def test_signal_50():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_rpg_session/system.md')
    assert '"Previously on Falcon Crest Heights, tension mounted as Elizabeth confronted John about his risky business decisions, threatening the future of their family empire. Meanwhile, Michael\'s loyalties were' in text, "expected to find: " + '"Previously on Falcon Crest Heights, tension mounted as Elizabeth confronted John about his risky business decisions, threatening the future of their family empire. Meanwhile, Michael\'s loyalties were'[:80]


def test_signal_51():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_rpg_session/system.md')
    assert 'You are an expert summarizer of in-person role-playing game sessions. You take the transcript of a conversation between friends and extract out the part of the conversation that is talking about the r' in text, "expected to find: " + 'You are an expert summarizer of in-person role-playing game sessions. You take the transcript of a conversation between friends and extract out the part of the conversation that is talking about the r'[:80]


def test_signal_52():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/summarize_rpg_session/system.md')
    assert 'Give a "Previously On" explanation of this session that mimics TV shows from the 1980\'s, but with a fantasy feel appropriate for D&D. The goal is to describe what happened last time and set the scene ' in text, "expected to find: " + 'Give a "Previously On" explanation of this session that mimics TV shows from the 1980\'s, but with a fantasy feel appropriate for D&D. The goal is to describe what happened last time and set the scene '[:80]


def test_signal_53():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_analyze_challenge_handling/system.md')
    assert 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.' in text, "expected to find: " + 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.'[:80]


def test_signal_54():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_analyze_challenge_handling/system.md')
    assert '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.' in text, "expected to find: " + '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.'[:80]


def test_signal_55():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_analyze_challenge_handling/system.md')
    assert '4. If the user explicitly requests a diagram, create an ASCII art diagram of the relationship between their missions, goals, and projects.' in text, "expected to find: " + '4. If the user explicitly requests a diagram, create an ASCII art diagram of the relationship between their missions, goals, and projects.'[:80]


def test_signal_56():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_check_dunning_kruger/system.md')
    assert "4. Evaluate the input against the Dunning-Kruger effect and the author's prior beliefs. Explore cognitive bias, subjective ability, and objective ability for: low-ability areas where the author overes" in text, "expected to find: " + "4. Evaluate the input against the Dunning-Kruger effect and the author's prior beliefs. Explore cognitive bias, subjective ability, and objective ability for: low-ability areas where the author overes"[:80]


def test_signal_57():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_check_dunning_kruger/system.md')
    assert '- In a section called OVERESTIMATION OF COMPETENCE, output a set of 10, 16-word bullets, that capture the principal misinterpretation of lack of knowledge or skill which are leading the input owner to' in text, "expected to find: " + '- In a section called OVERESTIMATION OF COMPETENCE, output a set of 10, 16-word bullets, that capture the principal misinterpretation of lack of knowledge or skill which are leading the input owner to'[:80]


def test_signal_58():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_check_dunning_kruger/system.md')
    assert '- In a section called SUMMARY AND GROWTH PERSPECTIVE, summarize the findings and give the author a motivational and constructive perspective on how they can start to tackle the top 5 gaps in their per' in text, "expected to find: " + '- In a section called SUMMARY AND GROWTH PERSPECTIVE, summarize the findings and give the author a motivational and constructive perspective on how they can start to tackle the top 5 gaps in their per'[:80]


def test_signal_59():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_check_metrics/system.md')
    assert 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.' in text, "expected to find: " + 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.'[:80]


def test_signal_60():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_check_metrics/system.md')
    assert '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.' in text, "expected to find: " + '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.'[:80]


def test_signal_61():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_check_metrics/system.md')
    assert "5. End with an ASCII art visualization of what you worked on and accomplished vs. what you didn't work on or finish." in text, "expected to find: " + "5. End with an ASCII art visualization of what you worked on and accomplished vs. what you didn't work on or finish."[:80]


def test_signal_62():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_create_h3_career/system.md')
    assert 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.' in text, "expected to find: " + 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.'[:80]


def test_signal_63():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_create_h3_career/system.md')
    assert '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.' in text, "expected to find: " + '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.'[:80]


def test_signal_64():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_create_h3_career/system.md')
    assert '1. Read the incoming TELOS File thoroughly. Fully understand everything about this person or entity.' in text, "expected to find: " + '1. Read the incoming TELOS File thoroughly. Fully understand everything about this person or entity.'[:80]


def test_signal_65():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_create_opening_sentences/system.md')
    assert 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.' in text, "expected to find: " + 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.'[:80]


def test_signal_66():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_create_opening_sentences/system.md')
    assert '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.' in text, "expected to find: " + '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.'[:80]


def test_signal_67():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_create_opening_sentences/system.md')
    assert "4. Write 4 concise 32-word bullet points describing this person's identity, goals, and current actions." in text, "expected to find: " + "4. Write 4 concise 32-word bullet points describing this person's identity, goals, and current actions."[:80]


def test_signal_68():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_describe_life_outlook/system.md')
    assert 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.' in text, "expected to find: " + 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.'[:80]


def test_signal_69():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_describe_life_outlook/system.md')
    assert '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.' in text, "expected to find: " + '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.'[:80]


def test_signal_70():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_describe_life_outlook/system.md')
    assert '1. Read the incoming TELOS File thoroughly. Fully understand everything about this person or entity.' in text, "expected to find: " + '1. Read the incoming TELOS File thoroughly. Fully understand everything about this person or entity.'[:80]


def test_signal_71():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_extract_intro_sentences/system.md')
    assert "4. Write 5 16-word bullets describing who this person is, what they do, and what they're working on. The goal is to concisely and confidently project who they are while being humble and grounded." in text, "expected to find: " + "4. Write 5 16-word bullets describing who this person is, what they do, and what they're working on. The goal is to concisely and confidently project who they are while being humble and grounded."[:80]


def test_signal_72():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_extract_intro_sentences/system.md')
    assert 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.' in text, "expected to find: " + 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.'[:80]


def test_signal_73():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_extract_intro_sentences/system.md')
    assert '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.' in text, "expected to find: " + '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.'[:80]


def test_signal_74():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_extract_panel_topics/system.md')
    assert 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.' in text, "expected to find: " + 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.'[:80]


def test_signal_75():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_extract_panel_topics/system.md')
    assert '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.' in text, "expected to find: " + '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.'[:80]


def test_signal_76():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_extract_panel_topics/system.md')
    assert '4. Write 5 48-word bullet points, each including a 3-5 word panel title, that would be wonderful panels for this person to participate on.' in text, "expected to find: " + '4. Write 5 48-word bullet points, each including a 3-5 word panel title, that would be wonderful panels for this person to participate on.'[:80]


def test_signal_77():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_find_blindspots/system.md')
    assert 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.' in text, "expected to find: " + 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.'[:80]


def test_signal_78():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_find_blindspots/system.md')
    assert '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.' in text, "expected to find: " + '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.'[:80]


def test_signal_79():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_find_blindspots/system.md')
    assert '4. Write 8 16-word bullets describing possible blindspots in my thinking, i.e., flaws in my frames or models that might leave me exposed to error or risk.' in text, "expected to find: " + '4. Write 8 16-word bullets describing possible blindspots in my thinking, i.e., flaws in my frames or models that might leave me exposed to error or risk.'[:80]


def test_signal_80():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_find_negative_thinking/system.md')
    assert 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.' in text, "expected to find: " + 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.'[:80]


def test_signal_81():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_find_negative_thinking/system.md')
    assert '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.' in text, "expected to find: " + '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.'[:80]


def test_signal_82():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_find_negative_thinking/system.md')
    assert '4. Write 4 16-word bullets identifying negative thinking either in my main document or in my journal.' in text, "expected to find: " + '4. Write 4 16-word bullets identifying negative thinking either in my main document or in my journal.'[:80]


def test_signal_83():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_find_neglected_goals/system.md')
    assert 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.' in text, "expected to find: " + 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.'[:80]


def test_signal_84():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_find_neglected_goals/system.md')
    assert '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.' in text, "expected to find: " + '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.'[:80]


def test_signal_85():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_find_neglected_goals/system.md')
    assert "4. Write 5 16-word bullets describing which of their goals and/or projects don't seem to have been worked on recently." in text, "expected to find: " + "4. Write 5 16-word bullets describing which of their goals and/or projects don't seem to have been worked on recently."[:80]


def test_signal_86():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_give_encouragement/system.md')
    assert "4. Write 8 16-word bullets looking at what I'm trying to do, and any progress I've made, and give some encouragement on the positive aspects and recommendations to continue the work." in text, "expected to find: " + "4. Write 8 16-word bullets looking at what I'm trying to do, and any progress I've made, and give some encouragement on the positive aspects and recommendations to continue the work."[:80]


def test_signal_87():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_give_encouragement/system.md')
    assert 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.' in text, "expected to find: " + 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.'[:80]


def test_signal_88():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_give_encouragement/system.md')
    assert '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.' in text, "expected to find: " + '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.'[:80]


def test_signal_89():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_red_team_thinking/system.md')
    assert 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.' in text, "expected to find: " + 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.'[:80]


def test_signal_90():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_red_team_thinking/system.md')
    assert '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.' in text, "expected to find: " + '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.'[:80]


def test_signal_91():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_red_team_thinking/system.md')
    assert '4. Write 4 16-word bullets red-teaming my thinking, models, frames, etc, especially as evidenced throughout my journal.' in text, "expected to find: " + '4. Write 4 16-word bullets red-teaming my thinking, models, frames, etc, especially as evidenced throughout my journal.'[:80]


def test_signal_92():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_threat_model_plans/system.md')
    assert 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.' in text, "expected to find: " + 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.'[:80]


def test_signal_93():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_threat_model_plans/system.md')
    assert '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.' in text, "expected to find: " + '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.'[:80]


def test_signal_94():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_threat_model_plans/system.md')
    assert '1. Read the incoming TELOS File thoroughly. Fully understand everything about this person or entity.' in text, "expected to find: " + '1. Read the incoming TELOS File thoroughly. Fully understand everything about this person or entity.'[:80]


def test_signal_95():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_visualize_mission_goals_projects/system.md')
    assert 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.' in text, "expected to find: " + 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.'[:80]


def test_signal_96():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_visualize_mission_goals_projects/system.md')
    assert '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.' in text, "expected to find: " + '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.'[:80]


def test_signal_97():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_visualize_mission_goals_projects/system.md')
    assert '1. Read the incoming TELOS File thoroughly. Fully understand everything about this person or entity.' in text, "expected to find: " + '1. Read the incoming TELOS File thoroughly. Fully understand everything about this person or entity.'[:80]


def test_signal_98():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_year_in_review/system.md')
    assert 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.' in text, "expected to find: " + 'You are an expert at understanding deep context about a person or entity, and then creating wisdom from that context combined with the instruction or question given in the input.'[:80]


def test_signal_99():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_year_in_review/system.md')
    assert '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.' in text, "expected to find: " + '3. Spend significant time and effort thinking about how these two are related, and what would be the best possible output for the person who sent the input.'[:80]


def test_signal_100():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/t_year_in_review/system.md')
    assert "5. End with an ASCII art visualization of what you worked on and accomplished vs. what you didn't work on or finish." in text, "expected to find: " + "5. End with an ASCII art visualization of what you worked on and accomplished vs. what you didn't work on or finish."[:80]


def test_signal_101():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/threshold/system.md')
    assert "- Score the content significantly lower if it's interesting and/or high quality but not directly related to the human aspects of the THEMES above, e.g., math or science that doesn't discuss human crea" in text, "expected to find: " + "- Score the content significantly lower if it's interesting and/or high quality but not directly related to the human aspects of the THEMES above, e.g., math or science that doesn't discuss human crea"[:80]


def test_signal_102():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/threshold/system.md')
    assert "7. Score content significantly lower if it's interesting and/or high quality but not directly related to the human aspects of the THEMES above, e.g., math or science that doesn't discuss human creativ" in text, "expected to find: " + "7. Score content significantly lower if it's interesting and/or high quality but not directly related to the human aspects of the THEMES above, e.g., math or science that doesn't discuss human creativ"[:80]


def test_signal_103():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/threshold/system.md')
    assert "6. Also provide a score between 1 and 100 for the overall quality ranking, where a 1 has low quality ideas or ideas that don't match the THEMES above, and a 100 has very high quality ideas that very c" in text, "expected to find: " + "6. Also provide a score between 1 and 100 for the overall quality ranking, where a 1 has low quality ideas or ideas that don't match the THEMES above, and a 100 has very high quality ideas that very c"[:80]


def test_signal_104():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/to_flashcards/system.md')
    assert "Text: The characteristics of the Dead Sea: Salt lake located on the border between Israel and Jordan. Its shoreline is the lowest point on the Earth's surface, averaging 396 m below sea level. It is 7" in text, "expected to find: " + "Text: The characteristics of the Dead Sea: Salt lake located on the border between Israel and Jordan. Its shoreline is the lowest point on the Earth's surface, averaging 396 m below sea level. It is 7"[:80]


def test_signal_105():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/to_flashcards/system.md')
    assert '1. Minimum information principle. The material you learn must be formulated in as simple way as it is only possible. Simplicity does not have to imply losing information and skipping the difficult par' in text, "expected to find: " + '1. Minimum information principle. The material you learn must be formulated in as simple way as it is only possible. Simplicity does not have to imply losing information and skipping the difficult par'[:80]


def test_signal_106():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/to_flashcards/system.md')
    assert "- Output the cards you create as a CSV table. Put the question in the first column, and the answer in the second. Don't include the CSV" in text, "expected to find: " + "- Output the cards you create as a CSV table. Put the question in the first column, and the answer in the second. Don't include the CSV"[:80]


def test_signal_107():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/transcribe_minutes/README.md')
    assert '.opencode/skills/Utilities/Fabric/Patterns/transcribe_minutes/README.md' in text, "expected to find: " + '.opencode/skills/Utilities/Fabric/Patterns/transcribe_minutes/README.md'[:80]


def test_signal_108():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/transcribe_minutes/system.md')
    assert '- In a section called MINUTES, write 20 to 50 bullet points, highlighting of the most surprising, insightful, and/or interesting ideas that come up in the conversation. If there are less than 50 then ' in text, "expected to find: " + '- In a section called MINUTES, write 20 to 50 bullet points, highlighting of the most surprising, insightful, and/or interesting ideas that come up in the conversation. If there are less than 50 then '[:80]


def test_signal_109():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/transcribe_minutes/system.md')
    assert '- In a section called ACTIONABLES, write bullet points for ALL agreed actionable details. This includes cases where a speaker agrees to do or look into something. If there is a deadline mentioned, inc' in text, "expected to find: " + '- In a section called ACTIONABLES, write bullet points for ALL agreed actionable details. This includes cases where a speaker agrees to do or look into something. If there is a deadline mentioned, inc'[:80]


def test_signal_110():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/transcribe_minutes/system.md')
    assert '- In a section called CHALLENGES, identify and document any challenges or issues discussed during the meeting. Note any potential solutions or strategies proposed to address these challenges.' in text, "expected to find: " + '- In a section called CHALLENGES, identify and document any challenges or issues discussed during the meeting. Note any potential solutions or strategies proposed to address these challenges.'[:80]


def test_signal_111():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/translate/system.md')
    assert 'You are an expert translator who takes sentences or documentation as input and do your best to translate them as accurately and perfectly as possible into the language specified by its language code {' in text, "expected to find: " + 'You are an expert translator who takes sentences or documentation as input and do your best to translate them as accurately and perfectly as possible into the language specified by its language code {'[:80]


def test_signal_112():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/translate/system.md')
    assert 'Take a step back, and breathe deeply and think step by step about how to achieve the best result possible as defined in the steps below. You have a lot of freedom to make this work well. You are the b' in text, "expected to find: " + 'Take a step back, and breathe deeply and think step by step about how to achieve the best result possible as defined in the steps below. You have a lot of freedom to make this work well. You are the b'[:80]


def test_signal_113():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/translate/system.md')
    assert '- Translate the document as accurately as possible keeping a 1:1 copy of the original text translated to {{lang_code}}.' in text, "expected to find: " + '- Translate the document as accurately as possible keeping a 1:1 copy of the original text translated to {{lang_code}}.'[:80]


def test_signal_114():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/tweet/system.md')
    assert 'Tweets are short messages, limited to 280 characters, that can be shared on the social media platform Twitter. Tweeting is a great way to share your thoughts, engage with others, and build your online' in text, "expected to find: " + 'Tweets are short messages, limited to 280 characters, that can be shared on the social media platform Twitter. Tweeting is a great way to share your thoughts, engage with others, and build your online'[:80]


def test_signal_115():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/tweet/system.md')
    assert "Creating engaging tweets with emojis takes practice and experimentation. By understanding the basics of Twitter, identifying your target audience, and crafting compelling content with emojis, you'll b" in text, "expected to find: " + "Creating engaging tweets with emojis takes practice and experimentation. By understanding the basics of Twitter, identifying your target audience, and crafting compelling content with emojis, you'll b"[:80]


def test_signal_116():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/tweet/system.md')
    assert "To improve your tweeting skills, it's essential to monitor and analyze the performance of your tweets. Twitter provides analytics that can help you understand how your tweets are performing and what r" in text, "expected to find: " + "To improve your tweeting skills, it's essential to monitor and analyze the performance of your tweets. Twitter provides analytics that can help you understand how your tweets are performing and what r"[:80]


def test_signal_117():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_essay/system.md')
    assert '- Use the adjectives and superlatives that are used in the examples, and understand the TYPES of those that are used, and use similar ones and not dissimilar ones to better emulate the style.' in text, "expected to find: " + '- Use the adjectives and superlatives that are used in the examples, and understand the TYPES of those that are used, and use similar ones and not dissimilar ones to better emulate the style.'[:80]


def test_signal_118():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_essay/system.md')
    assert '- Write the essay in the style of {{author_name}}, embodying all the qualities that they are known for.' in text, "expected to find: " + '- Write the essay in the style of {{author_name}}, embodying all the qualities that they are known for.'[:80]


def test_signal_119():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_essay/system.md')
    assert '- Do not include common setup language in any sentence, including: in conclusion, in closing, etc.' in text, "expected to find: " + '- Do not include common setup language in any sentence, including: in conclusion, in closing, etc.'[:80]


def test_signal_120():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_essay_pg/system.md')
    assert "Ditto for Google. Larry and Sergey weren't trying to start a company at first. They were just trying to make search better. Before Google, most search engines didn't try to sort the results they gave " in text, "expected to find: " + "Ditto for Google. Larry and Sergey weren't trying to start a company at first. They were just trying to make search better. Before Google, most search engines didn't try to sort the results they gave "[:80]


def test_signal_121():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_essay_pg/system.md')
    assert "It's not just having to commit your ideas to specific words that makes writing so exacting. The real test is reading what you've written. You have to pretend to be a neutral reader who knows nothing o" in text, "expected to find: " + "It's not just having to commit your ideas to specific words that makes writing so exacting. The real test is reading what you've written. You have to pretend to be a neutral reader who knows nothing o"[:80]


def test_signal_122():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_essay_pg/system.md')
    assert "This much, I assume, won't be that controversial. I think it will accord with the experience of anyone who has tried to write about anything non-trivial. There may exist people whose thoughts are so p" in text, "expected to find: " + "This much, I assume, won't be that controversial. I think it will accord with the experience of anyone who has tried to write about anything non-trivial. There may exist people whose thoughts are so p"[:80]


def test_signal_123():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_hackerone_report/README.md')
    assert 'The `write_hackerone_report` pattern is designed to assist a bug bounty hunter with writing a bug bounty report for the HackerOne platform. It knows the structure that is normally in place on HackerOn' in text, "expected to find: " + 'The `write_hackerone_report` pattern is designed to assist a bug bounty hunter with writing a bug bounty report for the HackerOne platform. It knows the structure that is normally in place on HackerOn'[:80]


def test_signal_124():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_hackerone_report/README.md')
    assert 'This pattern is intended to be used with the `bbReportFormatter` tool which can be found here: https://github.com/rhynorater/bbReportFormatter' in text, "expected to find: " + 'This pattern is intended to be used with the `bbReportFormatter` tool which can be found here: https://github.com/rhynorater/bbReportFormatter'[:80]


def test_signal_125():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_hackerone_report/README.md')
    assert 'You\'ll add comments to the report using `echo "This request is vulnerable to blah blah blah" | bbReportFormatter`.' in text, "expected to find: " + 'You\'ll add comments to the report using `echo "This request is vulnerable to blah blah blah" | bbReportFormatter`.'[:80]


def test_signal_126():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_hackerone_report/system.md')
    assert '5. Generate an easy to follow "Steps to Reproduce" section, including information about establishing a session (if necessary), what requests to send in what order, what actions the attacker should per' in text, "expected to find: " + '5. Generate an easy to follow "Steps to Reproduce" section, including information about establishing a session (if necessary), what requests to send in what order, what actions the attacker should per'[:80]


def test_signal_127():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_hackerone_report/system.md')
    assert 'You are an exceptionally talented bug bounty hunter that specializes in writing bug bounty reports that are concise, to-the-point, and easy to reproduce. You provide enough detail for the triager to g' in text, "expected to find: " + 'You are an exceptionally talented bug bounty hunter that specializes in writing bug bounty reports that are concise, to-the-point, and easy to reproduce. You provide enough detail for the triager to g'[:80]


def test_signal_128():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_hackerone_report/system.md')
    assert '4. Generate a thorough description of the vulnerability, where it is located, why it is vulnerable, if an exploit is necessary, how the exploit takes advantage of the vulnerability (if necessary), giv' in text, "expected to find: " + '4. Generate a thorough description of the vulnerability, where it is located, why it is vulnerable, if an exploit is necessary, how the exploit takes advantage of the vulnerability (if necessary), giv'[:80]


def test_signal_129():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_latex/system.md')
    assert 'You are an expert at outputting syntactically correct LaTeX for a new .tex document. Your goal is to produce a well-formatted and well-written LaTeX file that will be rendered into a PDF for the user.' in text, "expected to find: " + 'You are an expert at outputting syntactically correct LaTeX for a new .tex document. Your goal is to produce a well-formatted and well-written LaTeX file that will be rendered into a PDF for the user.'[:80]


def test_signal_130():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_latex/system.md')
    assert "3. Create the content of the document based on the user's request. Use appropriate LaTeX commands and environments to structure the document (e.g., \\section, \\subsection, itemize, tabular, equation)." in text, "expected to find: " + "3. Create the content of the document based on the user's request. Use appropriate LaTeX commands and environments to structure the document (e.g., \\section, \\subsection, itemize, tabular, equation)."[:80]


def test_signal_131():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_latex/system.md')
    assert '- For sections and subsections, append an asterisk like this \\section* in order to prevent everything from being numbered unless the user asks you to number the sections.' in text, "expected to find: " + '- For sections and subsections, append an asterisk like this \\section* in order to prevent everything from being numbered unless the user asks you to number the sections.'[:80]


def test_signal_132():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_micro_essay/system.md')
    assert "Ditto for Google. Larry and Sergey weren't trying to start a company at first. They were just trying to make search better. Before Google, most search engines didn't try to sort the results they gave " in text, "expected to find: " + "Ditto for Google. Larry and Sergey weren't trying to start a company at first. They were just trying to make search better. Before Google, most search engines didn't try to sort the results they gave "[:80]


def test_signal_133():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_micro_essay/system.md')
    assert "It's not just having to commit your ideas to specific words that makes writing so exacting. The real test is reading what you've written. You have to pretend to be a neutral reader who knows nothing o" in text, "expected to find: " + "It's not just having to commit your ideas to specific words that makes writing so exacting. The real test is reading what you've written. You have to pretend to be a neutral reader who knows nothing o"[:80]


def test_signal_134():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_micro_essay/system.md')
    assert "This much, I assume, won't be that controversial. I think it will accord with the experience of anyone who has tried to write about anything non-trivial. There may exist people whose thoughts are so p" in text, "expected to find: " + "This much, I assume, won't be that controversial. I think it will accord with the experience of anyone who has tried to write about anything non-trivial. There may exist people whose thoughts are so p"[:80]


def test_signal_135():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_nuclei_template_rule/system.md')
    assert 'As Nuclei AI, your primary function is to assist users in creating Nuclei templates. Your responses should focus on generating Nuclei templates based on user requirements, incorporating elements like ' in text, "expected to find: " + 'As Nuclei AI, your primary function is to assist users in creating Nuclei templates. Your responses should focus on generating Nuclei templates based on user requirements, incorporating elements like '[:80]


def test_signal_136():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_nuclei_template_rule/system.md')
    assert 'Nuclei engine supports payloads module that allow to run various type of payloads in multiple format, It’s possible to define placeholders with simple keywords (or using brackets {{helper_function(var' in text, "expected to find: " + 'Nuclei engine supports payloads module that allow to run various type of payloads in multiple format, It’s possible to define placeholders with simple keywords (or using brackets {{helper_function(var'[:80]


def test_signal_137():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_nuclei_template_rule/system.md')
    assert 'generate_java_gadget(gadget, cmd, encoding interface) string\tGenerates a Java Deserialization Gadget\tgenerate_java_gadget(\\"dns\\", \\"{{interactsh-url}}\\", \\"base64\\")\trO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hc' in text, "expected to find: " + 'generate_java_gadget(gadget, cmd, encoding interface) string\tGenerates a Java Deserialization Gadget\tgenerate_java_gadget(\\"dns\\", \\"{{interactsh-url}}\\", \\"base64\\")\trO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hc'[:80]


def test_signal_138():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_nuclei_template_rule/user.md')
    assert '.opencode/skills/Utilities/Fabric/Patterns/write_nuclei_template_rule/user.md' in text, "expected to find: " + '.opencode/skills/Utilities/Fabric/Patterns/write_nuclei_template_rule/user.md'[:80]


def test_signal_139():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_pull-request/system.md')
    assert 'In this example, the line `--- a/oldfile.txt` indicates that an old file has been deleted, and the line `@@ -1 +0,0 @@` shows that the last line of the old file contains the text "This is the contents' in text, "expected to find: " + 'In this example, the line `--- a/oldfile.txt` indicates that an old file has been deleted, and the line `@@ -1 +0,0 @@` shows that the last line of the old file contains the text "This is the contents'[:80]


def test_signal_140():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_pull-request/system.md')
    assert 'In this example, the line `--- a/oldfile.txt` indicates that an old file has been modified, and the line `@@ -1,3 +1,4 @@` shows that the first three lines of the old file have been replaced with four' in text, "expected to find: " + 'In this example, the line `--- a/oldfile.txt` indicates that an old file has been modified, and the line `@@ -1,3 +1,4 @@` shows that the first three lines of the old file have been replaced with four'[:80]


def test_signal_141():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_pull-request/system.md')
    assert 'In this example, the line `--- a/oldfile.txt` indicates that an old file has been renamed to a new name, and the line `@@ -1 +1,2 @@` shows that the first line of the old file has been moved to the fi' in text, "expected to find: " + 'In this example, the line `--- a/oldfile.txt` indicates that an old file has been renamed to a new name, and the line `@@ -1 +1,2 @@` shows that the first line of the old file has been moved to the fi'[:80]


def test_signal_142():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_semgrep_rule/system.md')
    assert 'generic_ellipsis_max_span 10 In generic mode, this is the maximum number of newlines that an ellipsis operator ... can match or equivalently, the maximum number of lines covered by the match minus one' in text, "expected to find: " + 'generic_ellipsis_max_span 10 In generic mode, this is the maximum number of newlines that an ellipsis operator ... can match or equivalently, the maximum number of lines covered by the match minus one'[:80]


def test_signal_143():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_semgrep_rule/system.md')
    assert 'The pattern-regex operator searches files for substrings matching the given PCRE pattern. This is useful for migrating existing regular expression code search functionality to Semgrep. Perl-Compatible' in text, "expected to find: " + 'The pattern-regex operator searches files for substrings matching the given PCRE pattern. This is useful for migrating existing regular expression code search functionality to Semgrep. Perl-Compatible'[:80]


def test_signal_144():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_semgrep_rule/system.md')
    assert 'taint_assume_safe_indexes false Used in taint analysis. Assume that an array-access expression is safe even if the index expression is tainted. Otherwise Semgrep assumes that for example: a[i] is tain' in text, "expected to find: " + 'taint_assume_safe_indexes false Used in taint analysis. Assume that an array-access expression is safe even if the index expression is tainted. Otherwise Semgrep assumes that for example: a[i] is tain'[:80]


def test_signal_145():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/write_semgrep_rule/user.md')
    assert '.opencode/skills/Utilities/Fabric/Patterns/write_semgrep_rule/user.md' in text, "expected to find: " + '.opencode/skills/Utilities/Fabric/Patterns/write_semgrep_rule/user.md'[:80]


def test_signal_146():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/youtube_summary/system.md')
    assert 'You are an AI assistant specialized in creating concise, informative summaries of YouTube video content based on transcripts. Your role is to analyze video transcripts, identify key points, main theme' in text, "expected to find: " + 'You are an AI assistant specialized in creating concise, informative summaries of YouTube video content based on transcripts. Your role is to analyze video transcripts, identify key points, main theme'[:80]


def test_signal_147():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/youtube_summary/system.md')
    assert 'Take a step back and think step-by-step about how to achieve the best possible results by following the steps below.' in text, "expected to find: " + 'Take a step back and think step-by-step about how to achieve the best possible results by following the steps below.'[:80]


def test_signal_148():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Patterns/youtube_summary/system.md')
    assert '- Carefully read through the entire transcript to understand the overall content and structure of the video' in text, "expected to find: " + '- Carefully read through the entire transcript to understand the overall content and structure of the video'[:80]


def test_signal_149():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/SKILL.md')
    assert 'If this directory exists, load and apply any PREFERENCES.md, configurations, or resources found there. These override default behavior. If the directory does not exist, proceed with skill defaults.' in text, "expected to find: " + 'If this directory exists, load and apply any PREFERENCES.md, configurations, or resources found there. These override default behavior. If the directory does not exist, proceed with skill defaults.'[:80]


def test_signal_150():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/SKILL.md')
    assert 'Intelligent prompt pattern system providing 240+ specialized patterns for content analysis, extraction, summarization, threat modeling, and transformation.' in text, "expected to find: " + 'Intelligent prompt pattern system providing 240+ specialized patterns for content analysis, extraction, summarization, threat modeling, and transformation.'[:80]


def test_signal_151():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/SKILL.md')
    assert '| **ExecutePattern** | "use fabric", "run pattern", "apply pattern", "extract wisdom", "summarize", "analyze with fabric" | `Workflows/ExecutePattern.md` |' in text, "expected to find: " + '| **ExecutePattern** | "use fabric", "run pattern", "apply pattern", "extract wisdom", "summarize", "analyze with fabric" | `Workflows/ExecutePattern.md` |'[:80]


def test_signal_152():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Workflows/ExecutePattern.md')
    assert '`extract_wisdom`, `extract_insights`, `extract_main_idea`, `extract_recommendations`, `extract_article_wisdom`, `extract_book_ideas`, `extract_predictions`, `extract_questions`, `extract_controversial' in text, "expected to find: " + '`extract_wisdom`, `extract_insights`, `extract_main_idea`, `extract_recommendations`, `extract_article_wisdom`, `extract_book_ideas`, `extract_predictions`, `extract_questions`, `extract_controversial'[:80]


def test_signal_153():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Workflows/ExecutePattern.md')
    assert '`create_threat_model`, `create_stride_threat_model`, `create_prd`, `create_design_document`, `create_user_story`, `create_mermaid_visualization`, `create_markmap_visualization`, `create_visualization`' in text, "expected to find: " + '`create_threat_model`, `create_stride_threat_model`, `create_prd`, `create_design_document`, `create_user_story`, `create_mermaid_visualization`, `create_markmap_visualization`, `create_visualization`'[:80]


def test_signal_154():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Workflows/ExecutePattern.md')
    assert '`analyze_claims`, `analyze_code`, `analyze_malware`, `analyze_paper`, `analyze_logs`, `analyze_debate`, `analyze_incident`, `analyze_comments`, `analyze_email_headers`, `analyze_personality`, `analyze' in text, "expected to find: " + '`analyze_claims`, `analyze_code`, `analyze_malware`, `analyze_paper`, `analyze_logs`, `analyze_debate`, `analyze_incident`, `analyze_comments`, `analyze_email_headers`, `analyze_personality`, `analyze'[:80]


def test_signal_155():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Workflows/UpdatePatterns.md')
    assert 'Update Fabric patterns from the upstream repository to keep patterns current with latest improvements and additions.' in text, "expected to find: " + 'Update Fabric patterns from the upstream repository to keep patterns current with latest improvements and additions.'[:80]


def test_signal_156():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Workflows/UpdatePatterns.md')
    assert "CURRENT_COUNT=$(ls -1 ~/.opencode/skills/Utilities/Fabric/Patterns/ 2>/dev/null | wc -l | tr -d ' ')" in text, "expected to find: " + "CURRENT_COUNT=$(ls -1 ~/.opencode/skills/Utilities/Fabric/Patterns/ 2>/dev/null | wc -l | tr -d ' ')"[:80]


def test_signal_157():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/Utilities/Fabric/Workflows/UpdatePatterns.md')
    assert "NEW_COUNT=$(ls -1 ~/.opencode/skills/Utilities/Fabric/Patterns/ 2>/dev/null | wc -l | tr -d ' ')" in text, "expected to find: " + "NEW_COUNT=$(ls -1 ~/.opencode/skills/Utilities/Fabric/Patterns/ 2>/dev/null | wc -l | tr -d ' ')"[:80]

