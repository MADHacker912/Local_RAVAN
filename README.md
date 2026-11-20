# ⚡ RAVAN // TERMINAL AI AGENT

<p align="center">
  <img src="assets/logo.png" width="300" alt="RAVAN 16-Bit Cyber Pixel Art Logo" />
  <br>
  <em>Autonomous 16-Bit Cyber-Hacker AI Agent | OpenRouter x HexStrike MCP</em>
</p>

---

Autonomous White-Hat Cybersecurity Terminal Assistant powered by **OpenRouter API** and **HexStrike MCP (150+ Security Tools)**.

---

## 🚀 Features

- **Web Surfer & Bug Bounty Scope Extractor**: Automatically surfs any target URL, HackerOne, Bugcrowd, or disclosure policy link to parse in-scope wildcard domains (`*.target.com`), API endpoints, forms, technologies, and security headers before testing.
- **Agent Live Browser**: Persistent Chromium browser with live interactive streaming at `http://localhost:7654` for single-page applications (SPAs) and authenticated workflows.
- **OpenRouter Multi-Model Support**: Use `anthropic/claude-3.5-sonnet`, `openai/gpt-4o`, `deepseek/deepseek-chat`, or any model on OpenRouter with smart alias resolution.
- **HexStrike FastMCP Integration**: Direct access to 150+ specialized security tools (`nmap`, `nuclei`, `sqlmap`, `httpx`, `subfinder`, `amass`, `ffuf`, `dirb`, `dalfox`, `arjun`, `katana`, `wpscan`, `radare2`, `strings`, `binwalk`, `checksec`).
- **Interactive Cyber Terminal**: Rich-styled cyberpunk terminal with ANSI formatting, live execution spinners, and markdown output.
- **Auto Markdown Reports**: Every scan and assessment automatically saves a complete `.md` report to `/home/obito/hex-cyber-agent/reports/`.

---

## 🛠️ Quick Start

### 1. Launch Agent
Terminal me kahin se bhi run karein:
```bash
ravan
```
*(Ya alternative alias `hex-agent`)*
ya phir direct script se:
```bash
cd /home/obito/hex-cyber-agent
./run.sh
```

### 2. Enter OpenRouter API Key
Pehli baar launch karne par ye aapse OpenRouter API Key maangega aur use securely `~/.hex_agent.env` me store kar dega:
```env
OPENROUTER_API_KEY="sk-or-v1-xxxxxxxx"
DEFAULT_MODEL="anthropic/claude-3.5-sonnet"
DEFAULT_MODE="bugbounty"
```

---

## ⚡ Terminal Slash Commands

- `/mode <bugbounty|malware|all>` : Switch active toolset profile
- `/model <model_id>` : Switch OpenRouter LLM model dynamically
- `/tools` : Display all available HexStrike MCP tools loaded in current mode
- `/clear` : Clear current conversation context
- `/key` : Update OpenRouter API key
- `/exit` : Quit terminal agent

---

## 🛡️ Example Prompts

1. **Subdomain & Web Recon**:
   `"Analyze target https://example.com: run httpx probe, discover subdomains, and check for open ports."`
2. **Vulnerability Scanning**:
   `"Run a quick nuclei scan on https://target.com for critical and high severity CVEs."`
3. **Malware Static Analysis**:
   `"I have a suspicious binary at /tmp/sample.bin. Extract strings, run checksec and binwalk analysis."`
4. **SQLi / API Audit**:
   `"Test this endpoint for SQL injection using sqlmap through HexStrike tools."`
