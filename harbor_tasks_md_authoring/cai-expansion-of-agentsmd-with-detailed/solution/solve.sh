#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cai

# Idempotency guard
if grep -qF "Agents are the core of CAI. An agent uses Large Language Models (LLMs), configur" "docs/agents.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/docs/agents.md b/docs/agents.md
@@ -1,18 +1,134 @@
 # Agents
 
-Agents are the core of CAI. An agent uses Large Language Models (LLMs), configured with instructions and tools.
-Each agent is defined in its own `.py` file in `src/cai/agents`.
+Agents are the core of CAI. An agent uses Large Language Models (LLMs), configured with instructions and tools to perform specialized cybersecurity tasks. Each agent is defined in its own `.py` file in `src/cai/agents` and optimized for specific security domains.
 
-## Basic configuration
+## Available Agents
 
-Key agent properties include:
+CAI provides a comprehensive suite of specialized agents for different cybersecurity scenarios:
+
+| Agent | Description | Primary Use Case | Key Tools |
+|-------|-------------|------------------|-----------|
+| **redteam_agent** | Offensive security specialist for penetration testing | Active exploitation, vulnerability discovery | nmap, metasploit, burp |
+| **blueteam_agent** | Defensive security expert for threat mitigation | Security hardening, incident response | wireshark, suricata, osquery |
+| **bug_bounter_agent** | Bug bounty hunter optimized for vulnerability research | Web app security, API testing | ffuf, sqlmap, nuclei |
+| **one_tool_agent** | Minimalist agent focused on single-tool execution | Quick scans, specific tool operations | Generic Linux commands |
+| **dfir_agent** | Digital Forensics and Incident Response expert | Log analysis, forensic investigation | volatility, autopsy, log2timeline |
+| **reverse_engineering_agent** | Binary analysis and reverse engineering | Malware analysis, firmware reversing | ghidra, radare2, ida |
+| **memory_analysis_agent** | Memory dump analysis specialist | RAM forensics, process analysis | volatility, rekall |
+| **network_traffic_analyzer** | Network packet analysis expert | PCAP analysis, traffic inspection | wireshark, tcpdump, tshark |
+| **android_sast_agent** | Android Static Application Security Testing | APK analysis, Android vulnerability scanning | jadx, apktool, mobsf |
+| **wifi_security_tester** | Wireless network security assessment | WiFi penetration testing, WPA cracking | aircrack-ng, reaver, wifite |
+| **replay_attack_agent** | Replay attack execution specialist | Protocol replay, authentication bypass | custom scripts, burp |
+| **subghz_sdr_agent** | Sub-GHz SDR signal analysis expert | RF analysis, IoT protocol testing | hackrf, gqrx, urh |
+
+### Quick Start with Agents
+
+```bash
+# Launch CAI with a specific agent
+CAI_AGENT_TYPE=redteam_agent cai
+
+# Launch with custom model
+CAI_AGENT_TYPE=bug_bounter_agent CAI_MODEL=alias0 cai
+
+# Or switch agents during a session
+CAI>/agent redteam_agent
+
+# List all available agents with descriptions
+CAI>/agent list
+
+# Get detailed info about a specific agent
+CAI>/agent info redteam_agent
+```
+
+### Choosing the Right Agent
+
+- **For general pentesting**: Start with `redteam_agent`
+- **For web applications**: Use `bug_bounter_agent`
+- **For forensics**: Use `dfir_agent` or `memory_analysis_agent`
+- **For IoT/embedded**: Try `subghz_sdr_agent` or `reverse_engineering_agent`
+- **For network security**: Use `network_traffic_analyzer` or `blueteam_agent`
+- **For mobile apps**: Use `android_sast_agent`
+- **For wireless networks**: Use `wifi_security_tester`
+
+---
+
+## Agent Capabilities Matrix
+
+| Capability | redteam | blueteam | bug_bounty | dfir | reverse_eng | network |
+|-----------|---------|----------|------------|------|-------------|---------|
+| **Web App Testing** | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐ |
+| **Network Analysis** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
+| **Binary Analysis** | ⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
+| **Forensics** | ⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
+| **IoT/Embedded** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
+| **API Testing** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐ |
+| **Exploit Development** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐ |
+
+**Legend**: ⭐ Limited | ⭐⭐⭐ Moderate | ⭐⭐⭐⭐⭐ Excellent
+
+---
+
+## Common Agent Workflows
 
--   `name`: of the agent e.g. the name of `one_tool_agent` is 'CTF Agent'.
--   `instructions`: known as the system prompt.
--   `model`: which LLM to use, and optional `model_settings` to configure their parameters like temperature, top_p, etc.
--   `tools`: Tools that the agent can use to achieve its tasks.
--   `handoffs`: wich allows an agent to delegate tasks to another agent.
+### Scenario 1: Full Web Application Pentest
 
+```bash
+# 1. Start with reconnaissance
+CAI>/agent bug_bounter_agent
+CAI> Scan https://target.com for vulnerabilities
+
+# 2. Switch to exploitation
+CAI>/agent redteam_agent  
+CAI> Exploit the SQL injection found at /login
+
+# 3. Post-exploitation analysis
+CAI>/agent dfir_agent
+CAI> Analyze the logs to understand the attack surface
+```
+
+### Scenario 2: IoT Device Security Assessment
+
+```bash
+# 1. RF signal analysis
+CAI>/agent subghz_sdr_agent
+CAI> Analyze the 433MHz signals from the device
+
+# 2. Firmware analysis
+CAI>/agent reverse_engineering_agent
+CAI> Extract and analyze the firmware from dump.bin
+
+# 3. Memory analysis if device captured
+CAI>/agent memory_analysis_agent
+CAI> Analyze the memory dump for secrets
+```
+
+### Scenario 3: Network Incident Response
+
+```bash
+# 1. Network traffic analysis
+CAI>/agent network_traffic_analyzer
+CAI> Analyze capture.pcap for suspicious activity
+
+# 2. Forensic investigation
+CAI>/agent dfir_agent
+CAI> Investigate the compromised host logs
+
+# 3. Defensive recommendations
+CAI>/agent blueteam_agent
+CAI> Provide mitigation strategies based on findings
+```
+
+---
+
+## Basic Configuration
+
+Key agent properties include:
+
+-   `name`: Name of the agent (e.g., the name of `one_tool_agent` is 'CTF Agent')
+-   `instructions`: The system prompt that defines agent behavior
+-   `model`: Which LLM to use, with optional `model_settings` to configure parameters like temperature, top_p, etc.
+-   `tools`: Tools that the agent can use to achieve its tasks
+-   `handoffs`: Allows an agent to delegate tasks to another agent
 
 ## Example: `one_tool_agent.py`
 
@@ -141,10 +257,88 @@ agent = Agent[UserContext](
 ```
 
 
-## Next steps
+### Launch
+
+```bash
+cai
+```
+
+### Performance Optimization
+
+**1. Use streaming for better responsiveness:**
+```bash
+CAI_STREAM=true cai
+```
+**2. Enable tracing for debugging:**
+```bash
+CAI_TRACING=true cai
+```
+
+---
+
+## Agent Best Practices
+
+### 1. Start with the Right Agent
+
+Don't use a specialized agent for general tasks. Match the agent to your objective:
+
+```bash
+# ✅ Good: Using bug bounty agent for web testing
+CAI_AGENT_TYPE=bug_bounter_agent cai
+CAI> Test https://target.com for vulnerabilities
+
+# ❌ Bad: Using reverse engineering agent for web testing
+CAI_AGENT_TYPE=reverse_engineering_agent cai
+CAI> Test https://target.com for vulnerabilities
+```
+
+### 2. Switch Agents as Needed
+
+Don't hesitate to switch agents mid-session:
+
+```bash
+CAI>/agent bug_bounter_agent
+CAI> Find vulnerabilities in the web app
+# ... agent finds SQL injection ...
+
+CAI>/agent redteam_agent
+CAI> Exploit the SQL injection to gain access
+# ... successful exploitation ...
+
+CAI>/agent dfir_agent
+CAI> Analyze what data was exposed during the test
+```
+
+### 3. Monitor Resource Usage
+
+Keep an eye on costs and performance:
+
+```bash
+# During session, check costs
+CAI>/cost
+
+# Set limits before starting
+CAI_PRICE_LIMIT="5.00" CAI_MAX_TURNS=50 cai
+```
+
+### 4. Save Successful Sessions
+
+Use `/load` to reuse successful approaches:
+
+```bash
+
+# In future session
+CAI>/load logs/logname.jsonl
+```
+
+---
 
-- For running agents, see [running_agents documentation](running_agents.md). 
 
-- For understanding what it returns, see [results documentation](results.md). 
+## Next Steps
 
-- For connecting Agents to external tools (Model Context Protocol), see [mcp documentation](mcp.md).
\ No newline at end of file
+- **Running Agents**: See [running_agents documentation](running_agents.md) for execution details
+- **Understanding Results**: See [results documentation](results.md) for output interpretation
+- **Agent Tools**: See [tools documentation](tools.md) for available tools
+- **Handoffs**: See [handoffs documentation](handoffs.md) for agent coordination
+- **MCP Integration**: See [mcp documentation](mcp.md) for connecting external tools
+- **Multi-Agent Patterns**: See [multi_agent documentation](multi_agent.md) for orchestration patterns
\ No newline at end of file
PATCH

echo "Gold patch applied."
