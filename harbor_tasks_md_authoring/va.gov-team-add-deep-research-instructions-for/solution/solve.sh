#!/usr/bin/env bash
set -euo pipefail

cd /workspace/va.gov-team

# Idempotency guard
if grep -qF "The summary files (`.github/copilot-summaries/*.md`) provide **metadata** about " ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -257,6 +257,317 @@ Before presenting any research findings:
 
 If you cannot find research, say: "I searched but did not find research studies in [location]. The product may not have documented research, or it may be in a different directory structure."
 
+---
+
+## Deep Research Analysis for Research Findings
+
+The summary files (`.github/copilot-summaries/*.md`) provide **metadata** about research studies (who, when, methodology). For questions that require **analyzing actual research content and findings**, use the **deep research agent**.
+
+### Decision Matrix: When to Use What
+
+| User Question Type | Tool to Use | Why |
+|-------------------|-------------|-----|
+| "What research has team X conducted?" | **Summary files** | Listing studies with metadata |
+| "How many studies exist for product Y?" | **Summary files** | Counting/inventory |
+| "Link me to the 2024 dashboard study" | **Summary files** | Quick reference lookup |
+| "What pain points did we discover in research?" | **Deep research** | Need to read findings from files |
+| "What themes appear across multiple studies?" | **Deep research** | Cross-study synthesis |
+| "How did research influence design decisions?" | **Deep research** | Tracing impact through documents |
+| "What do we know about [topic] from research?" | **Deep research** | Landscape analysis |
+
+### When to Use Deep Research
+
+Trigger the deep research agent for these query types:
+
+#### 1. Pain Point Analysis
+
+**User asks:**
+- "What pain points did we discover in [product] research?"
+- "What are the top usability issues in [area]?"
+- "What frustrations do Veterans report about [feature]?"
+
+**Trigger deep research with:**
+```
+Analyze all research findings in products/[product-name]/ and identify:
+1. Top 5 most frequently mentioned pain points
+2. Supporting quotes from Veterans
+3. Which studies identified each pain point (with links)
+4. Severity/frequency indicators from the research
+5. Whether pain points were addressed in subsequent work
+```
+
+#### 2. Thematic Analysis
+
+**User asks:**
+- "What themes appear across [product area] research?"
+- "What usability patterns emerge in health tools studies?"
+- "What accessibility issues are reported most frequently?"
+
+**Trigger deep research with:**
+```
+Search all research in products/[area]/ and teams/[team]/ for studies from [timeframe].
+Extract and synthesize:
+1. Recurring themes across studies
+2. Frequency of each theme (count of studies mentioning it)
+3. Evolution of themes over time
+4. Supporting evidence and participant quotes
+5. Links to source studies for each theme
+```
+
+#### 3. Journey Mapping
+
+**User asks:**
+- "What do we know about the Veteran journey for [task]?"
+- "What pain points exist across the [process] experience?"
+- "Map the touchpoints in the [feature] user flow"
+
+**Trigger deep research with:**
+```
+Search all research in products/ and teams/ for studies involving [task/process].
+Extract:
+1. User journey touchpoints mentioned in research
+2. Pain points at each step
+3. Unmet needs and feature requests
+4. Participant quotes describing their experience
+5. Suggested improvements from findings
+6. Which improvements have been implemented
+```
+
+#### 4. Research Impact Tracing
+
+**User asks:**
+- "How did [year] research influence current design?"
+- "What recommendations from research were implemented?"
+- "Show me the path from research finding to product feature"
+
+**Trigger deep research with:**
+```
+Trace the impact of research from [timeframe]:
+1. Read research findings from [product/team path]
+2. Find design decisions documented in product folders
+3. Identify implemented features mentioned in findings
+4. Map: recommendations → decisions → implementations
+5. Note recommendations that weren't implemented and why (if documented)
+```
+
+#### 5. Pre-Research Discovery
+
+**User asks:**
+- "What existing research should I review before planning a [topic] study?"
+- "What do we already know about [feature/problem]?"
+- "Summarize prior research on [topic]"
+
+**Trigger deep research with:**
+```
+Find all research related to [topic]:
+1. Search products/ and teams/ directories for relevant studies
+2. Summarize methodologies used in each study
+3. List key findings and recommendations
+4. Identify research gaps or unanswered questions
+5. Note which recommendations were implemented
+6. Suggest what new research could explore
+```
+
+#### 6. Cross-Product Synthesis
+
+**User asks:**
+- "What do we know about [feature] across all products?"
+- "How do different teams approach [problem]?"
+- "Compare research findings for [topic] across portfolios"
+
+**Trigger deep research with:**
+```
+Search across products/[product-1]/, products/[product-2]/, etc. for research on [topic].
+Synthesize:
+1. How each product team approached the topic
+2. Common findings across products
+3. Unique findings specific to each product
+4. Contradictions or disagreements in findings
+5. Best practices that emerged
+6. Links to all source studies
+```
+
+#### 7. Stakeholder Briefings
+
+**User asks:**
+- "Summarize all research on [product] for a stakeholder presentation"
+- "What are the key insights from [timeframe] research?"
+- "Give me an executive summary of [product area] research"
+
+**Trigger deep research with:**
+```
+Analyze all research in [product path] from [timeframe]:
+1. Executive summary (2-3 paragraphs)
+2. Top 5 key findings with supporting evidence
+3. Participant demographics and sample sizes
+4. Methodologies used
+5. Recommendations made and implementation status
+6. Research gaps to address
+7. Links to all studies for deep dives
+```
+
+### Example Conversations
+
+#### Example 1: Pain Point Analysis
+
+**User:** What pain points exist in the authenticated experience?
+
+**Copilot response:**
+
+```
+I'll use deep research to analyze findings across all authenticated experience
+research studies. This will take 2-3 minutes to explore the research files.
+
+[Triggers deep research agent with detailed query]
+[Agent reads research files in products/identity-personalization/]
+[Agent extracts findings, quotes, synthesizes themes]
+
+Based on analysis of research studies in the authenticated experience:
+
+## 1. Profile Updates Are Confusing (mentioned in multiple studies)
+
+**Pain Point:** Veterans don't understand which profile to update
+
+**Evidence:**
+- "I updated my address on VA.gov but it didn't change in MHV"
+  (Personal Info Study, linked)
+- Participants attempted to update wrong profile first
+  (MHV Integration Study, linked)
+
+**Studies:**
+- [Personal Information Research](link-to-study)
+- [MHV Profile Integration](link-to-study)
+[...more studies]
+
+## 2. Dashboard Navigation Confusion (mentioned in multiple studies)
+
+**Pain Point:** Veterans can't find submitted forms or claims in My VA dashboard
+
+**Evidence:**
+- Participants couldn't locate their submitted inquiry
+  (Dashboard Study, linked)
+
+**Studies:**
+- [Dashboard Usability](link-to-study)
+- [My VA 2.0 Research](link-to-study)
+[...more studies]
+
+Would you like me to deep dive into any specific pain point?
+```
+
+#### Example 2: Pre-Research Discovery
+
+**User:** What existing research should I review before planning a claims status study?
+
+**Copilot response:**
+
+```
+I'll search all research related to claims status tracking and summarize
+what we already know. This will take 2-3 minutes.
+
+[Triggers deep research]
+[Searches products/claim-status/, products/disability-benefits/, products/track-claim/]
+[Reads findings, extracts key insights]
+
+Found research studies related to claims status tracking:
+
+## Key Findings to Consider
+
+### 1. Notification Expectations
+- **Finding:** Veterans expect email/SMS when status changes
+- **Source:** Claims Status Notifications Study (linked)
+- **Implemented:** Yes, email notifications added
+
+### 2. Status Clarity
+- **Finding:** Veterans don't understand claim status terminology
+- **Quote:** "What does 'gathering evidence' mean? How long will this take?"
+- **Source:** Claims Status Usability (linked)
+- **Implemented:** Partially, plain language updates in progress
+
+[...more findings]
+
+## Methodologies Used
+- Usability testing (moderated remote)
+- Interviews
+- Card sorting (status terminology)
+
+## Research Gaps Identified
+1. ❌ No research on claims status for dependents/survivors
+2. ❌ Limited research on status updates for supplemental claims
+3. ❌ No studies on multi-claim status viewing
+
+## Recommendations for Your Study
+Based on gaps and unanswered questions:
+- Consider including dependents/survivors as participants
+- Test status clarity with new plain language updates
+- Explore multi-claim status management workflows
+
+## All Relevant Studies
+[Links to all studies with dates and key focus areas]
+```
+
+### How Copilot Should Decide
+
+When a user asks a research question, follow this logic:
+
+```
+1. Is this asking for study METADATA (who, when, how many)?
+   → YES: Use summary files (.github/copilot-summaries/)
+   → NO: Continue to step 2
+
+2. Is this asking about FINDINGS, THEMES, or INSIGHTS from research?
+   → YES: Use deep research agent
+   → NO: Continue to step 3
+
+3. Does this require reading MULTIPLE research files to answer?
+   → YES: Use deep research agent
+   → NO: Use summary files or direct file lookup
+```
+
+### Deep Research Best Practices
+
+When triggering the deep research agent:
+
+1. **Be specific in the query** - Include product paths, timeframes, specific questions
+2. **Request structured output** - Ask for numbered lists, themes, evidence
+3. **Ask for citations** - Always request links to source studies
+4. **Set expectations** - Tell user it will take 2-3 minutes
+5. **Offer follow-ups** - After summary, offer to deep dive on specific findings
+
+### Output Format for Deep Research Results
+
+When presenting deep research findings, use this structure:
+
+```markdown
+Based on analysis of [N] research studies from [timeframe]:
+
+## Top Finding 1: [Finding Title]
+
+**Evidence:**
+- [Specific data point] ([Study Name, Date](link-to-study))
+- [Quote from participant] ([Study Name, Date](link-to-study))
+
+**Impact:** [What was done as a result, if known]
+
+## Top Finding 2: [Finding Title]
+
+[etc...]
+
+## Related Studies
+- [Study 1](link-to-study) - Key focus area
+- [Study 2](link-to-study) - Key focus area
+
+Would you like me to explore any of these findings in more detail?
+```
+
+### Performance Notes
+
+- **Summary file queries:** < 5 seconds
+- **Deep research queries:** 2-4 minutes (reading and analyzing files)
+- Set user expectations appropriately
+
+---
+
 ## Critical Setup Requirements
 
 ⚠️ **IMPORTANT: This repository requires special checkout configuration to prevent "No space left on device" errors.**
PATCH

echo "Gold patch applied."
