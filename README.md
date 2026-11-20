# RAVAN // AUTONOMOUS CYBERSECURITY AI AGENT

<p align="center">
  <img src="assets/logo.png" width="320" alt="RAVAN 16-Bit Cyber Pixel Art Logo" />
  <br>
  <em>Autonomous 16-Bit Offensive Cyber-Intelligence Terminal Agent | OpenRouter x HexStrike FastMCP</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/Tools-150+-E02424?style=flat&logo=kalilinux&logoColor=white" alt="150+ Tools" />
  <img src="https://img.shields.io/badge/OpenRouter-API-6366F1?style=flat" alt="OpenRouter API" />
  <img src="https://img.shields.io/badge/Format-HackerOne_Advisory-4F46E5?style=flat" alt="HackerOne Format" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="MIT License" />
</p>

---

## Overview

**RAVAN** is an elite terminal-native, autonomous cybersecurity AI agent designed for authorized penetration testing, vulnerability assessment, bug bounty hunting, and binary analysis.

Integrated with **OpenRouter** for multi-model LLM reasoning (Claude 3.5 Sonnet, DeepSeek R1/Chat, GPT-4o, Llama 3.3) and **HexStrike FastMCP** (150+ automated security tools), RAVAN operates with complete autonomy. It autonomously surfs target scopes, uncovers attack surfaces, identifies business logic risks, executes security tools in a continuous feedback loop, and produces comprehensive, evidence-backed security reports formatted to professional **HackerOne Security Advisory** standards.

---

## Key Features

- **100% Autonomous Hands-Off Execution**: Zero confirmation loops. Once given an assessment objective, RAVAN executes tools, analyzes output, pivots based on discovered findings, and delivers final reports without asking permission.
- **Deep Web Surfing & Business Logic Profiling**: Analyzes web targets to identify company business models (E-Commerce, FinTech, SaaS, Healthcare) and automatically tailors vulnerability discovery toward critical business logic vectors (e.g., cart tampering, BOLA/IDOR, payment bypasses, PostMessage wildcards).
- **Automated Scope Extraction**: Parses bug bounty programs (HackerOne, Bugcrowd, private disclosure policies) to instantly extract in-scope wildcard domains (`*.target.com`), out-of-scope targets, APIs, and client-side technology stacks.
- **HexStrike FastMCP Integration (150+ Tools)**:
  - **Recon & Discovery**: `httpx`, `subfinder`, `amass`, `katana`, `dirb`, `ffuf`, `arjun`, `dnsenum`, `wafw00f`.
  - **Vulnerability Auditing**: `nuclei`, `sqlmap`, `dalfox`, `jaeles`, `wfuzz`, `nikto`, `wpscan`.
  - **Binary & Malware Analysis**: `radare2`, `binwalk`, `checksec`, `strings`, `ropgadget`, `volatility`.
  - **Network & Infrastructure**: `nmap`, `masscan`, `rustscan`, `enum4linux`, `netexec`, `hydra`.
- **HackerOne Standard Reporting**: Every assessment generates a structured `.md` advisory matching industry bug bounty disclosure standards (CVSS 3.1 scoring, Root Cause, Bundle/Endpoint Analysis, Runnable PoC, and Remediation Guidelines).
- **Dynamic Multi-Model Switching**: Seamlessly change LLM backends on the fly (`/model deepseek`, `/model claude`, `/model gpt4`) to leverage different reasoning strengths.
- **Cyberpunk Terminal UI**: Styled terminal interface built with Rich ANSI formatting, live execution spinners, telemetry logs, and interactive command prompts.

---

## Architecture Pipeline

```
┌────────────────────────────────────────────────────────┐
│                      USER PROMPT                       │
│       e.g., "Audit api.target.com for critical bugs"   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                   STAGE 1: SURF & OSINT                │
│  • web_surf_target: Crawls scope, headers, postMessage │
│  • web_search_osint: Gathers past CVEs and writeups    │
│  • Business Logic Classification (FinTech, SaaS, etc.) │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│              STAGE 2: AUTONOMOUS RECON & TOOLS         │
│  • HexStrike FastMCP: httpx, subfinder, nuclei, etc.   │
│  • Dynamic Tool Chaining & Output Parsing              │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│               STAGE 3: TRIAGE & REPORTING              │
│  • HackerOne Security Advisory Formatting              │
│  • CVSS 3.1 Vector & Root Cause Technical Breakdown    │
│  • Auto-saved to reports/hackerone_report_*.md         │
└────────────────────────────────────────────────────────┘
```

---

## Installation & Setup

### Prerequisites

- Linux (Ubuntu/Debian, Arch, Kali, Fedora)
- Python 3.10+
- Git & Curl
- [Optional] Running HexStrike Server on port `8888` (for the 150+ security tools suite)

### 1. Clone the Repository

```bash
git clone https://github.com/MADHacker912/ravan.git
cd ravan
```

### 2. Install Dependencies & CLI Alias

Run the automated installer:

```bash
./install.sh
```

This installs Python dependencies and creates a global `ravan` symlink in `~/.local/bin/`.

Alternatively, install dependencies manually:

```bash
pip install -r requirements.txt
```

### 3. Launch Agent

From anywhere in your terminal, run:

```bash
ravan
```

*(Or use the direct launch script: `./run.sh`)*

---

## Configuration

On your first run, RAVAN prompts for your **OpenRouter API Key** and securely saves it to `~/.hex_agent.env`. You can also configure this file manually:

```env
OPENROUTER_API_KEY="sk-or-v1-xxxxxxxxxxxxxxxx"
OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
DEFAULT_MODEL="anthropic/claude-3.5-sonnet"
HEXSTRIKE_SERVER="http://127.0.0.1:8888"
DEFAULT_MODE="bugbounty"
```

### Supported Model Aliases

You can reference models using short aliases:
- `claude` / `sonnet` -> `anthropic/claude-3.5-sonnet`
- `deepseek` / `deepseek-chat` -> `deepseek/deepseek-chat`
- `r1` / `deepseek-r1` -> `deepseek/deepseek-r1`
- `gpt4` / `gpt-4o` -> `openai/gpt-4o`
- `llama` -> `meta-llama/llama-3.3-70b-instruct`
- `gemini` -> `google/gemini-2.0-flash-exp:free`

---

## Terminal Slash Commands

Control operational modes and models directly from the interactive prompt:

| Command | Description |
|---|---|
| `/mode <name>` | Switch active toolset profile (`bugbounty`, `malware`, `essential`, `all`) |
| `/model <id>` | Switch OpenRouter LLM backend dynamically |
| `/tools` | List all active HexStrike MCP tools loaded in the current mode |
| `/key` | Update or change OpenRouter API Key |
| `/clear` | Clear the current conversation context |
| `/help` | Display command help sheet |
| `/exit` | Exit RAVAN agent |

---

## Example Usage

### 1. Web Target Recon & Scope Extraction
```text
╭─[ RAVAN | anthropic/claude-3.5-sonnet | BUGBOUNTY ]
╰─❯ Surf target https://example.com, discover in-scope assets, audit response headers, and check for missing CSP frame-ancestors.
```

### 2. Targeted Vulnerability Probing
```text
╭─[ RAVAN | deepseek/deepseek-chat | BUGBOUNTY ]
╰─❯ Execute a nuclei scan against https://api.target.com focusing on high and critical templates, and search for exposed API parameters with arjun.
```

### 3. Binary Static Analysis
```text
╭─[ RAVAN | openai/gpt-4o | MALWARE ]
╰─❯ Analyze the ELF binary at /tmp/suspicious_sample. Run checksec, extract printable strings, and inspect architecture headers.
```

---

## HackerOne Report Structure

Reports are automatically generated and saved to `reports/` following the format:

```markdown
# Security Report: <Descriptive Vulnerability Title>

**Program:** Target Scope Assessment  
**Asset:** `target.com`  
**Severity:** High (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N — Score: 6.5)  
**Weakness:** CWE-1021 (Improper Restriction of Rendered UI Layers)  
**Researcher Verification:** `X-HackerOne-Research: obito_gupta`  

## 1. Summary
[Executive summary of the issue]

## 2. Technical Analysis & Root Cause
### 2.1 Bundle / Endpoint Inspection
### 2.2 Response Header Audit

## 3. Impact
- Threat vectors and exploitation consequences

## 4. Steps to Reproduce
### Step 1: PoC Setup (HTML / curl / Python)
### Step 2: Verification

## 5. Remediation Guidelines
## 6. References
## 7. Automated Tool Telemetry
```

---

## Disclaimer

> **IMPORTANT**: RAVAN is engineered strictly for authorized security assessments, penetration testing, bug bounty hunting, and educational research on systems you own or have explicit, documented permission to test. Unauthorized access or attacks against systems without prior consent is illegal. Users are solely responsible for ensuring compliance with all applicable local, national, and international laws.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
