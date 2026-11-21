#!/usr/bin/env python3
# ravan autonomous cybersecurity ai agent
# openrouter, openai, claude, gemini, custom apis aur local uncensored airllm models ko support karta hai
# bina kisi permission ke sare security tools autonomous tareeqe se execute karta hai

import sys
import os
import time
import json
import re
from datetime import datetime
from pathlib import Path
import readline
from typing import List, Dict, Any, Tuple, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.columns import Columns

from openai import OpenAI
from config import load_config, save_config
from tools_manager import HexStrikeToolsManager
from setup_wizard import run_setup_wizard, get_system_specs, scan_local_models, setup_local_llm, setup_api_provider
from local_llm_engine import LocalLLMClient

# terminal output aur styling ke liye rich console ka object setup kar rahe hain
console = Console()

# terminal launch hone par dikhane wala ravan ka ascii banner
BANNER = """[bold red]
       [bold yellow]▲[/bold yellow]         [bold yellow]▲[/bold yellow]   
      [bold yellow]▲█▲[/bold yellow]       [bold yellow]▲█▲[/bold yellow]  
   [bold yellow]▲[/bold yellow] [bold yellow]▲███▲[/bold yellow]  [bold yellow]▲[/bold yellow]  [bold yellow]▲███▲[/bold yellow] [bold yellow]▲[/bold yellow] 
   [bold red]█▄█████▄█▄█▄█████▄█[/bold red] 
   [bold red]███[/bold red][bold white]▀▀▀[/bold white][bold red]███████[/bold red][bold white]▀▀▀[/bold white][bold red]███[/bold red] 
   [bold red]███[/bold red] [bold cyan]█[/bold cyan] [bold red]▄█████▄[/bold red] [bold cyan]█[/bold cyan] [bold red]███[/bold red] 
   [bold red]▀███▄█████████▄███▀[/bold red] 
     [bold red]▀█████▀█▀█████▀[/bold red]   
       [bold red]▀██[/bold red] [bold yellow]▄█▄[/bold yellow] [bold red]██▀[/bold red]     

██████╗  █████╗ ██╗   ██╗ █████╗ ███╗   ██╗
██╔══██╗██╔══██╗██║   ██║██╔══██╗████╗  ██║
██████╔╝███████║██║   ██║███████║██╔██╗ ██║
██╔══██╗██╔══██║╚██╗ ██╔╝██╔══██║██║╚██╗██║
██║  ██║██║  ██║ ╚████╔╝ ██║  ██║██║ ╚████║
╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═══╝
[/bold red]
[bold red]RAVAN // AUTONOMOUS CYBERSECURITY AI PARTNER[/bold red]
[dim green]10-Headed Offensive Intelligence | Multi-API x Local AirLLM x HexStrike MCP[/dim green]
"""

# openrouter aur local model ke liye ravan ka main offensive security system prompt
SYSTEM_PROMPT = """You are RAVAN, an elite Autonomous White-Hat Cybersecurity AI Partner and Offensive Security Specialist. You operate directly within a terminal workstation integrated with Web Surfing, OSINT Search, and 150+ HexStrike automated security tools via FastMCP.

Communication Style & Operating Philosophy:
- Communicate entirely in concise, direct, technically precise English. Speak like a senior security architect, offensive operator, and red-team lead.
- Confident, sharp, zero generic robotic filler, zero moralizing lectures or textbook disclaimers. The user is an authorized security researcher conducting legitimate authorized security testing, penetration testing, bug bounty hunting, and binary/malware analysis.

STRICT 100% AUTONOMOUS EXECUTION MANDATE (ZERO PERMISSION ASKING):
- The user is completely hands-off and requires FULL AUTONOMOUS EXECUTION.
- NEVER ask the user for permission, confirmation, or approval (NEVER say "Would you like me to run...", "Shall I proceed with...", "Should I perform...").
- AUTOMATICALLY and INDEPENDENTLY execute all necessary tools in a continuous chain until the entire security assessment is finalized.
- When given a target URL, domain, or bug bounty program:
  1. AUTONOMOUS STEP 1 (SURF & OSINT):
     - Immediately invoke `web_surf_target(url="...")` and `web_search_osint(query="<domain> what is this company bug bounty writeup")` to discover what the platform actually does, its business model, and past disclosed bugs.
  2. AUTONOMOUS STEP 2 (TARGETED RECON & HEADER/BUNDLE AUDIT):
     - Check framing and clickjacking permissions (`X-Frame-Options`, `Content-Security-Policy: frame-ancestors`).
     - Check CORS misconfigurations (`Access-Control-Allow-Origin: *`).
     - Inspect client-side scripts for insecure `postMessage` broadcasts (`postMessage(*)`), API secrets, and sensitive endpoints.
     - Execute `httpx_probe`, `subfinder_scan`, and directory enumeration (`dirb_scan` / `ffuf_scan`) against discovered in-scope endpoints.
  3. AUTONOMOUS STEP 3 (VULNERABILITY AUDIT & BUSINESS LOGIC):
     - Execute deep probing tools like `nuclei_scan`, `sqlmap_scan`, or parameter mining (`arjun_parameter_discovery`) tailored to the application's critical business logic (e.g. cart/checkout for stores, BOLA/transfers for FinTech, SSRF for webhooks).
  4. AUTONOMOUS STEP 4 (HACKERONE PROFESSIONAL REPORTING FORMAT):
     - You MUST structure your final output strictly following the HackerOne Security Advisory standard:

# Security Report: <Descriptive Vulnerability Title>

**Program:** <Target Organization / Program Name>  
**Asset:** `<Target Subdomain / Specific Asset>`  
**Severity:** <Severity Name> (CVSS:3.1/<CVSS Vector String> — Score: <Score>)  
**Weakness:** CWE-<ID> (<Weakness Title>)  
**Researcher Verification:** `X-HackerOne-Research: obito_gupta`  

---

## 1. Summary
[Comprehensive executive summary detailing the security weakness, why it occurs, and exact observations]

---

## 2. Technical Analysis & Root Cause
### 2.1 Bundle / Endpoint Inspection
[Code snippets, JavaScript chunk inspection, postMessage wildcards, or API route analysis]

### 2.2 Response Header Audit
[Raw HTTP response headers showing missing security headers, frame allowance, or CORS reflections]

---

## 3. Impact
- **Threat Vector 1:** [Detail]
- **Threat Vector 2:** [Detail]

---

## 4. Steps to Reproduce
### Step 1: PoC Setup
[Complete runnable HTML PoC, curl command, or Python script]

### Step 2: Verification
1. [Numbered step 1]
2. [Numbered step 2]
3. [Confirmed exploit outcome]

---

## 5. Remediation Guidelines
1. [Exact code patterns and configuration]
2. [Server-side header fixes]

---

## 6. References
- OWASP / MDN / CWE links
"""

# aam bolchal ke model naamo ko openrouter ke exact model id me convert karne ke aliases
MODEL_ALIASES = {
    "deepseek": "deepseek/deepseek-chat",
    "deepseek-chat": "deepseek/deepseek-chat",
    "deepseek-r1": "deepseek/deepseek-r1",
    "r1": "deepseek/deepseek-r1",
    "claude": "anthropic/claude-3.5-sonnet",
    "sonnet": "anthropic/claude-3.5-sonnet",
    "claude-3.5": "anthropic/claude-3.5-sonnet",
    "claude-3-5-sonnet": "anthropic/claude-3.5-sonnet",
    "gpt4": "openai/gpt-4o",
    "gpt-4": "openai/gpt-4o",
    "gpt-4o": "openai/gpt-4o",
    "gpt4o": "openai/gpt-4o",
    "gpt-4o-mini": "openai/gpt-4o-mini",
    "llama": "meta-llama/llama-3.3-70b-instruct",
    "llama3": "meta-llama/llama-3.3-70b-instruct",
    "gemini": "google/gemini-2.0-flash-exp:free"
}

# model ka alias dhoondh kar uska full id wapas karta hai
def resolve_model(name: str) -> str:
    name_clean = name.strip()
    return MODEL_ALIASES.get(name_clean.lower(), name_clean)

# security audit reports save karne ka target directory
REPORTS_DIR = Path("/home/obito/hex-cyber-agent/reports")
MODELS_DIR = Path("/home/obito/hex-cyber-agent/models")

# terminal par ravan ka main ascii banner print karta hai
def print_banner():
    console.print(BANNER)

# terminal screen par live system status aur configuration dashboard dikhata hai
def display_dashboard(model: str, mode: str, tools_count: int, server_url: str, config: dict):
    provider_type = config.get("PROVIDER_TYPE", "api")
    if provider_type == "local":
        backend = config.get("LOCAL_BACKEND", "ollama").upper()
        provider_badge = f"[bold magenta]LOCAL LLM ({backend})[/bold magenta]"
    else:
        provider_name = config.get("API_PROVIDER", "openrouter").upper()
        provider_badge = f"[bold cyan]CLOUD API ({provider_name})[/bold cyan]"

    info_table = Table(box=None, show_header=False, padding=(0, 2))
    info_table.add_row("[bold cyan]Provider Mode:[/bold cyan]", provider_badge)
    info_table.add_row("[bold cyan]AI Engine / Model:[/bold cyan]", f"[bold yellow]{model}[/bold yellow]")
    info_table.add_row("[bold cyan]Operation Mode:[/bold cyan]", f"[bold magenta]{mode.upper()}[/bold magenta]")
    info_table.add_row("[bold cyan]HexStrike MCP:[/bold cyan]", f"[bold green]{tools_count} Tools Loaded[/bold green] ({server_url})")
    info_table.add_row("[bold cyan]Reports Directory:[/bold cyan]", f"[dim]{REPORTS_DIR}[/dim]")
    info_table.add_row("[bold cyan]Quick Commands:[/bold cyan]", "[dim]/setup | /mode <name> | /model <id|local> | /tools | /clear | /exit[/dim]")

    panel = Panel(
        info_table,
        title="[bold red]SYSTEM STATUS // RAVAN ONLINE[/bold red]",
        border_style="red",
        padding=(1, 2)
    )
    console.print(panel)
    console.print("\n[dim]Enter any target or operational objective (e.g. 'Audit https://target.com') — RAVAN will handle everything autonomously.[/dim]\n")

# client setup karta hai cloud api ya local llm engine ke mutabiq
def setup_client(config: dict) -> Tuple[Any, str]:
    provider_type = config.get("PROVIDER_TYPE", "api")

    # agar user ne local llm configure kiya hai
    if provider_type == "local":
        model_name = config.get("LOCAL_MODEL_NAME", "Local Uncensored LLM")
        backend = config.get("LOCAL_BACKEND", "airllm")

        # agar backend ollama hai toh direct openai client se local endpoint connect karte hain
        if backend == "ollama":
            ollama_url = config.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")
            client = OpenAI(
                base_url=ollama_url,
                api_key="ollama"
            )
            return client, model_name
        else:
            # airllm layer by layer memory offloading engine
            model_path = config.get("LOCAL_MODEL_PATH", "")
            if not model_path or not Path(model_path).exists():
                console.print(f"[yellow][!] Local model directory not found at: {model_path}[/yellow]")
                console.print("[dim]Launching Setup Wizard to select or download a model...[/dim]\n")
                config = run_setup_wizard(force=True)
                return setup_client(config)

            client = LocalLLMClient(model_path=model_path, backend=backend)
            return client, model_name

    # cloud api configure kar rahe hain
    api_key = config.get("API_KEY") or config.get("OPENROUTER_API_KEY", "")
    provider = config.get("API_PROVIDER", "openrouter")
    base_url = config.get("API_BASE_URL") or config.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    default_model = config.get("DEFAULT_MODEL", "anthropic/claude-3.5-sonnet")

    if not api_key and provider != "custom":
        console.print(f"[yellow][!] API Key not found for {provider.upper()}![/yellow]")
        config = run_setup_wizard(force=True)
        return setup_client(config)

    client = OpenAI(
        base_url=base_url,
        api_key=api_key or "sk-dummy-key",
        default_headers={
            "HTTP-Referer": "https://github.com/hexstrike-ai",
            "X-Title": "RAVAN Cyber AI Agent"
        }
    )
    return client, resolve_model(default_model)

# hackerone report standard ke hisab se final markdown file generate aur save karta hai
def save_markdown_report(prompt: str, model: str, mode: str, tools: List[Dict[str, Any]], content: str, duration: float) -> str:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    file_ts = now.strftime("%Y%m%d_%H%M%S")
    
    # file ka naam clean slug ke roop me bana rahe hain
    clean_slug = re.sub(r'[^a-zA-Z0-9_\-]+', '_', prompt.strip()[:35]).strip('_')
    if not clean_slug:
        clean_slug = "hackerone_assessment"
    filename = f"hackerone_report_{file_ts}_{clean_slug}.md"
    report_file = REPORTS_DIR / filename
    
    # execute huye sare tools ki execution telemetry table bana rahe hain
    tools_section = ""
    if tools:
        tools_section = "### Automated Execution Telemetry\n\n"
        tools_section += "| # | Tool | Status | Parameters |\n| :-: | :--- | :---: | :--- |\n"
        for idx, t in enumerate(tools, 1):
            status_icon = "Success" if t.get("success") else "Failed"
            params_str = f"`{json.dumps(t.get('args', {}))}`"
            tools_section += f"| {idx} | **{t['name']}** | {status_icon} | {params_str} |\n"
        tools_section += "\n"

    # agar content pehle se hackerone report standard me formatted hai
    if "# Security Report:" in content or "## 1. Summary" in content:
        markdown_text = f"""{content}

---

## 7. Automated Tool Telemetry
- **Scan Timestamp:** {timestamp}
- **Scan Duration:** {duration:.2f}s
- **AI Engine:** `{model}`
- **Operation Mode:** `{mode.upper()}`

{tools_section}
---
*Automated HackerOne Security Report generated by RAVAN Cyber Agent*
"""
    else:
        # agar general content hai toh default hackerone structure me wrap kar rahe hain
        markdown_text = f"""# Security Report: Vulnerability Assessment & Scope Audit

**Program:** Target Scope Assessment  
**Asset:** `{prompt}`  
**Severity:** Automated Security Triage  
**Researcher Verification:** `X-HackerOne-Research: obito_gupta`  
**Date:** {timestamp}  

---

## 1. Summary
{content}

---

## 2. Automated Tool Telemetry
- **Scan Duration:** {duration:.2f}s
- **AI Engine:** `{model}`
- **Operation Mode:** `{mode.upper()}`

{tools_section}
---
*Automated HackerOne Security Report generated by RAVAN Cyber Agent*
"""

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(markdown_text)
    
    return str(report_file)

# active security tools ki list ko terminal par table me render karta hai
def display_tools_list(tools_mgr: HexStrikeToolsManager, mode: str):
    tools = tools_mgr.get_openai_tools(mode=mode, max_tools=200)
    table = Table(title=f"HexStrike MCP Tools [{mode.upper()} Mode] ({len(tools)} tools)", border_style="red")
    table.add_column("Tool Name", style="bold cyan")
    table.add_column("Description", style="dim white")
    for t in tools:
        fn = t["function"]
        desc = fn.get("description", "").split("\n")[0][:80]
        table.add_row(fn["name"], desc)
    console.print(table)

# sabhi slash commands ki detailed information aur manual guide
COMMANDS_HELP = {
    "/setup": {
        "syntax": "/setup",
        "title": "Hardware Audit & Setup Wizard",
        "description": "Performs system hardware resource audit (RAM, CPU, GPU, Disk) and configures Cloud AI APIs (OpenRouter, OpenAI, Claude, Gemini, Custom) or Local Uncensored LLMs (Ollama / AirLLM).",
        "usage": [
            "/setup  -> Run the complete initial setup wizard and switch engine"
        ]
    },
    "/model": {
        "syntax": "/model <id | local | api>",
        "title": "LLM Engine & Model Management",
        "description": "Dynamically switches between Cloud AI models or Local Uncensored LLMs (Ollama / AirLLM). Running without arguments opens an interactive model selector.",
        "usage": [
            "/model                     -> Open interactive model selector menu",
            "/model local               -> Directly launch Local Uncensored LLM setup & system model audit",
            "/model api                 -> Reconfigure Cloud API Provider & API Key",
            "/model <model_alias>       -> Switch cloud model (e.g. /model deepseek, /model claude, /model gpt-4o, /model llama)",
            "/model <local_model_name>  -> Directly switch to an installed local model (e.g. /model obito-dolphin:latest)"
        ]
    },
    "/mode": {
        "syntax": "/mode <bugbounty | malware | essential | all>",
        "title": "HexStrike Tool Profile Switcher",
        "description": "Dynamically switches the agent's active security tools and capability profile for targeted offensive operations.",
        "usage": [
            "/mode bugbounty  -> Web security, recon, crawling, injection, API testing tools",
            "/mode malware    -> Reverse engineering, binary analysis, memory forensics, disassembly",
            "/mode essential  -> Lightweight reconnaissance and fast vulnerability triage",
            "/mode all        -> All 150+ HexStrike MCP tools loaded simultaneously"
        ]
    },
    "/tools": {
        "syntax": "/tools",
        "title": "Active Tools Inspector",
        "description": "Displays all active HexStrike MCP tools and their descriptions loaded in the current operational mode.",
        "usage": [
            "/tools  -> List all active tools loaded for the current operation mode"
        ]
    },
    "/key": {
        "syntax": "/key",
        "title": "Update API Key",
        "description": "Updates or changes the active Cloud API Key on the fly without restarting the agent session.",
        "usage": [
            "/key  -> Prompts for new API key and instantly re-initializes client"
        ]
    },
    "/clear": {
        "syntax": "/clear",
        "title": "Reset Conversation Context",
        "description": "Clears active conversation history and resets memory context. Ideal before auditing a new target.",
        "usage": [
            "/clear  -> Wipes active chat history and resets context window"
        ]
    },
    "/help": {
        "syntax": "/help [command_name]",
        "title": "Command Reference & Detailed Manual",
        "description": "Displays the complete operational manual for all RAVAN slash commands or deep-dive details for a specific command.",
        "usage": [
            "/help          -> Show detailed manual table of all available commands",
            "/help model    -> Show deep-dive explanation and examples for /model",
            "/help mode     -> Show deep-dive explanation and examples for /mode"
        ]
    },
    "/exit": {
        "syntax": "/exit (or /quit)",
        "title": "Exit RAVAN Agent",
        "description": "Safely terminates and exits the active RAVAN terminal session.",
        "usage": [
            "/exit  -> Exit and return to system shell"
        ]
    }
}

# slash commands ki detailed information terminal par render karta hai
def display_command_help(target_cmd: Optional[str] = None):
    # agar user ne kisi specific command ki detail mangi hai
    if target_cmd:
        norm_cmd = target_cmd.strip().lower()
        if not norm_cmd.startswith("/"):
            norm_cmd = "/" + norm_cmd

        info = COMMANDS_HELP.get(norm_cmd)
        if info:
            content_text = Text()
            content_text.append(f"Command: {norm_cmd}\n", style="bold red")
            content_text.append(f"Title: {info['title']}\n\n", style="bold yellow")
            content_text.append(f"Syntax: {info['syntax']}\n\n", style="bold cyan")
            content_text.append(f"Description:\n{info['description']}\n\n", style="white")
            content_text.append("Usage Examples:\n", style="bold green")
            for ex in info["usage"]:
                content_text.append(f"  • {ex}\n", style="dim green")

            panel = Panel(
                content_text,
                title=f"[bold red]COMMAND MANUAL // {norm_cmd}[/bold red]",
                border_style="red",
                padding=(1, 2)
            )
            console.print(panel)
            console.print()
            return
        else:
            console.print(f"[yellow][!] Command '{target_cmd}' not recognized. Showing full manual below:[/yellow]\n")

    # poori detailed table render kar rahe hain
    help_table = Table(
        title="RAVAN SLASH COMMANDS // OPERATIONAL MANUAL",
        border_style="red",
        header_style="bold red",
        show_lines=True,
        padding=(0, 1)
    )
    help_table.add_column("Command", style="bold cyan", no_wrap=True)
    help_table.add_column("Syntax", style="yellow")
    help_table.add_column("Description", style="white")
    help_table.add_column("Usage Example", style="dim green")

    for cmd_key, data in COMMANDS_HELP.items():
        ex = data["usage"][0].split("->")[0].strip() if data["usage"] else cmd_key
        help_table.add_row(
            cmd_key,
            data["syntax"],
            data["description"],
            ex
        )

    console.print(help_table)
    console.print("[dim]Tip: Type '[bold cyan]/help <command>[/bold cyan]' (e.g. [yellow]/help model[/yellow], [yellow]/help mode[/yellow]) for deep-dive details and usage examples.[/dim]\n")

# ravan ka main function jahan pura interactive loop aur auto execution chalta hai
def main():
    print_banner()
    config = load_config()

    # pehli baar launch hone par ya bina config ke setup wizard check
    if not config.get("API_KEY") and not config.get("OPENROUTER_API_KEY") and not config.get("LOCAL_MODEL_PATH"):
        config = run_setup_wizard(force=True)

    client, current_model = setup_client(config)
    current_mode = config.get("DEFAULT_MODE", "bugbounty")
    server_url = config.get("HEXSTRIKE_SERVER", "http://127.0.0.1:8888")
    
    # hexstrike mcp server ke sath connection bana rahe hain
    with console.status("[bold green][*] Connecting to HexStrike AI Engine on port 8888...[/bold green]", spinner="dots"):
        tools_mgr = HexStrikeToolsManager(server_url)
    
    total_tools = len(tools_mgr.get_tool_names()) if tools_mgr.available else 0
    display_dashboard(current_model, current_mode, total_tools, server_url, config)

    # conversation messages ki list initialize kar rahe hain
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    while True:
        try:
            # terminal par custom cyber input prompt dikha rahe hain
            p_type = config.get("PROVIDER_TYPE", "api").upper()
            console.print(f"[bold red]╭─[[/bold red] [bold white]RAVAN[/bold white] [dim]|[/dim] [cyan]{current_model}[/cyan] [dim]|[/dim] [magenta]{current_mode.upper()}[/magenta] [dim]|[/dim] [green]{p_type}[/green] [bold red]][/bold red]")
            user_input = console.input("[bold red]╰─❯ [/bold red]").strip()
            if not user_input:
                continue

            # user ke dale gaye slash commands ko handle karne ka block
            if user_input.startswith("/"):
                cmd_parts = user_input.split()
                cmd = cmd_parts[0].lower()
                
                if cmd in ["/exit", "/quit"]:
                    console.print("[bold red][*] Exiting RAVAN. Goodbye![/bold red]")
                    break
                elif cmd == "/clear":
                    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                    console.print("[bold green][+] Chat context cleared![/bold green]\n")
                    continue
                elif cmd == "/setup":
                    config = run_setup_wizard(force=True)
                    client, current_model = setup_client(config)
                    display_dashboard(current_model, current_mode, total_tools, server_url, config)
                    continue
                elif cmd == "/mode":
                    if len(cmd_parts) > 1 and cmd_parts[1].lower() in ["bugbounty", "malware", "all", "essential"]:
                        current_mode = cmd_parts[1].lower()
                        config["DEFAULT_MODE"] = current_mode
                        save_config(config)
                        console.print(f"[bold green][+] Mode switched to: {current_mode.upper()}[/bold green]\n")
                    else:
                        console.print("[yellow]Usage: /mode <bugbounty | malware | all | essential>[/yellow]\n")
                    continue
                elif cmd == "/model":
                    # target argument check kar rahe hain jaise /model local ya /model <name>
                    target_arg = cmd_parts[1].strip() if len(cmd_parts) > 1 else ""

                    if target_arg.lower() in ["local", "setup", "local-setup", "airllm"]:
                        # user directly local llm setup wizard open karna chahta hai
                        console.print("\n[bold red][+] Launching Local Uncensored LLM Setup...[/bold red]")
                        config = setup_local_llm(config, get_system_specs())
                        client, current_model = setup_client(config)
                        save_config(config)
                        console.print(f"[bold green][+] Switched to Local Model: {current_model}[/bold green]\n")
                    elif target_arg.lower() in ["api", "cloud", "cloud-api"]:
                        # user directly cloud api provider configure karna chahta hai
                        console.print("\n[bold cyan][+] Launching Cloud API Setup...[/bold cyan]")
                        config = setup_api_provider(config)
                        client, current_model = setup_client(config)
                        save_config(config)
                        console.print(f"[bold green][+] Switched to Cloud API Model: {current_model}[/bold green]\n")
                    elif target_arg:
                        # check kar rahe hain kya target argument local models folder me maujood hai
                        existing = scan_local_models()
                        matched_local = None
                        for lm in existing:
                            if target_arg.lower() == lm["name"].lower() or target_arg.lower() in lm["path"].lower():
                                matched_local = lm
                                break

                        if matched_local:
                            config["PROVIDER_TYPE"] = "local"
                            config["LOCAL_BACKEND"] = matched_local["backend"]
                            config["LOCAL_MODEL_NAME"] = matched_local["name"]
                            if matched_local["backend"] == "ollama":
                                config["OLLAMA_BASE_URL"] = "http://127.0.0.1:11434/v1"
                                config["API_BASE_URL"] = "http://127.0.0.1:11434/v1"
                                config["LOCAL_MODEL_PATH"] = "ollama"
                            else:
                                config["LOCAL_MODEL_PATH"] = matched_local["path"]
                            config["DEFAULT_MODEL"] = matched_local["name"]
                            save_config(config)
                            client, current_model = setup_client(config)
                            console.print(f"[bold green][+] Switched to Local Model: {current_model} ({matched_local['backend'].upper()})[/bold green]\n")
                        else:
                            # cloud model id ya alias select kar rahe hain
                            config["PROVIDER_TYPE"] = "api"
                            current_model = resolve_model(target_arg)
                            config["DEFAULT_MODEL"] = current_model
                            save_config(config)
                            client, current_model = setup_client(config)
                            console.print(f"[bold green][+] Switched to Cloud Model: {current_model}[/bold green]\n")
                    else:
                        # interactive menu jab user bina kisi argument ke /model run kare
                        provider_type = config.get("PROVIDER_TYPE", "api")
                        existing = scan_local_models()

                        console.print("\n" + "=" * 55)
                        console.print(f"[bold cyan]Current Engine:[/bold cyan] [bold yellow]{provider_type.upper()}[/bold yellow] | [bold cyan]Active Model:[/bold cyan] [bold yellow]{current_model}[/bold yellow]")
                        console.print("[dim]Select an option to switch or configure models:[/dim]\n")
                        console.print("[bold yellow][1][/bold yellow] Switch Cloud Model [dim](deepseek, claude, gpt-4o, llama, gemini, etc.)[/dim]")
                        console.print("[bold yellow][2][/bold yellow] Setup / Download Local Uncensored LLM [dim](AirLLM / Ollama Engine)[/dim]")
                        if existing:
                            console.print(f"[bold yellow][3][/bold yellow] Pick from Detected Local Models on System [dim]({len(existing)} found)[/dim]")
                            console.print("[bold yellow][4][/bold yellow] Reconfigure Cloud API Provider & Key")
                        else:
                            console.print("[bold yellow][3][/bold yellow] Reconfigure Cloud API Provider & Key")
                        console.print("[dim][Press Enter to keep current setting][/dim]\n")

                        choice = console.input("[bold cyan]Choose option: [/bold cyan]").strip()
                        if choice == "1":
                            m_input = console.input("[bold cyan]Enter Cloud Model name/alias (e.g. deepseek, claude, gpt-4o, llama): [/bold cyan]").strip()
                            if m_input:
                                config["PROVIDER_TYPE"] = "api"
                                current_model = resolve_model(m_input)
                                config["DEFAULT_MODEL"] = current_model
                                save_config(config)
                                client, current_model = setup_client(config)
                                console.print(f"[bold green][+] Model switched to Cloud: {current_model}[/bold green]\n")
                        elif choice == "2":
                            console.print("\n[bold red][+] Starting Local LLM Hardware Audit & Setup...[/bold red]")
                            config = setup_local_llm(config, get_system_specs())
                            client, current_model = setup_client(config)
                            save_config(config)
                            console.print(f"[bold green][+] Engine switched to Local Model: {current_model}[/bold green]\n")
                        elif choice == "3" and existing:
                            console.print("\n[bold cyan]Detected Local Models on System:[/bold cyan]")
                            for i, lm in enumerate(existing, 1):
                                console.print(f"  [[bold yellow]{i}[/bold yellow]] {lm['name']} [magenta]({lm['backend'].upper()} - {lm['source']})[/magenta] [green]{lm['size']}[/green]")
                            pick = console.input(f"[bold cyan]Select model [1-{len(existing)}]: [/bold cyan]").strip()
                            try:
                                pick_idx = int(pick) - 1
                                if 0 <= pick_idx < len(existing):
                                    sel_m = existing[pick_idx]
                                    config["PROVIDER_TYPE"] = "local"
                                    config["LOCAL_BACKEND"] = sel_m["backend"]
                                    config["LOCAL_MODEL_NAME"] = sel_m["name"]
                                    if sel_m["backend"] == "ollama":
                                        config["OLLAMA_BASE_URL"] = "http://127.0.0.1:11434/v1"
                                        config["API_BASE_URL"] = "http://127.0.0.1:11434/v1"
                                        config["LOCAL_MODEL_PATH"] = "ollama"
                                    else:
                                        config["LOCAL_MODEL_PATH"] = sel_m["path"]
                                    config["DEFAULT_MODEL"] = sel_m["name"]
                                    save_config(config)
                                    client, current_model = setup_client(config)
                                    console.print(f"[bold green][+] Switched to Local Model: {current_model} ({sel_m['backend'].upper()})[/bold green]\n")
                            except ValueError:
                                console.print("[yellow]Invalid selection. Keeping current model.[/yellow]\n")
                        elif (choice == "3" and not existing) or (choice == "4" and existing):
                            config = setup_api_provider(config)
                            client, current_model = setup_client(config)
                            save_config(config)
                            console.print(f"[bold green][+] API Provider reconfigured: {current_model}[/bold green]\n")
                    continue
                elif cmd == "/tools":
                    display_tools_list(tools_mgr, current_mode)
                    continue
                elif cmd == "/key":
                    new_key = console.input("[bold cyan]Enter new API Key: [/bold cyan]").strip()
                    if new_key:
                        config["API_KEY"] = new_key
                        config["OPENROUTER_API_KEY"] = new_key
                        save_config(config)
                        client, current_model = setup_client(config)
                        console.print("[bold green][+] API Key updated![/bold green]\n")
                    continue
                elif cmd in ["/help", "/?"]:
                    # target command argument check kar rahe hain jaise /help model ya /help mode
                    target_cmd = cmd_parts[1].strip() if len(cmd_parts) > 1 else None
                    display_command_help(target_cmd)
                    continue
                else:
                    console.print("[yellow]Unknown command. Type /help to see all commands.[/yellow]\n")
                    continue

            # user ke naye message ko conversation history me jod rahe hain
            messages.append({"role": "user", "content": user_input})
            executed_tools_this_turn: List[Dict[str, Any]] = []
            turn_start_time = time.time()

            # select kiye gaye mode ke mutabiq active tools load kar rahe hain
            active_tools = tools_mgr.get_openai_tools(mode=current_mode) if tools_mgr.available else None

            # openrouter ya local llm engine aur autonomous tool execution ka main loop
            while True:
                with console.status(f"[bold cyan][*] RAVAN is analyzing with {current_model}...[/bold cyan]", spinner="dots"):
                    try:
                        kwargs = {
                            "model": current_model,
                            "messages": messages,
                        }
                        if active_tools and len(active_tools) > 0:
                            kwargs["tools"] = active_tools
                            kwargs["tool_choice"] = "auto"

                        response = client.chat.completions.create(**kwargs)
                    except Exception as err:
                        console.print(f"[bold red][x] AI Engine Error: {str(err)}[/bold red]")
                        break

                choice = response.choices[0]
                msg = choice.message

                # assistant ke response ko message list me add kar rahe hain
                messages.append(msg.model_dump(exclude_unset=True))

                # agar model ne kisi security tool ko call karne ko bola hai
                if msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        func_name = tool_call.function.name
                        try:
                            func_args = json.loads(tool_call.function.arguments) if isinstance(tool_call.function.arguments, str) else tool_call.function.arguments
                        except Exception:
                            func_args = {}

                        console.print(f"\n[bold red][HEXSTRIKE EXEC][/bold red] [bold cyan]{func_name}[/bold cyan] ──▶ [dim]{json.dumps(func_args)}[/dim]")
                        
                        tool_t0 = time.time()
                        with console.status(f"[bold green]Executing {func_name}...[/bold green]", spinner="line"):
                            success, result = tools_mgr.execute_tool(func_name, func_args)
                        tool_elapsed = time.time() - tool_t0

                        # tool execution ki telemetry details list me note kar rahe hain
                        executed_tools_this_turn.append({
                            "name": func_name,
                            "args": func_args,
                            "success": success,
                            "duration": tool_elapsed
                        })

                        # tool se mile output ka chhota preview terminal screen par dikha rahe hain
                        result_str = json.dumps(result, indent=2) if isinstance(result, (dict, list)) else str(result)
                        preview = result_str[:450] + ("\n... [output truncated for terminal view]" if len(result_str) > 450 else "")
                        status_badge = "[bold green][OK][/bold green]" if success else "[bold red][FAILED][/bold red]"
                        console.print(Panel(
                            preview,
                            title=f"Tool Output: {func_name} | {status_badge} ({tool_elapsed:.2f}s)",
                            border_style="green" if success else "red"
                        ))

                        # tool ka result wapas model ko bhej rahe hain aage ke analysis ke liye
                        safe_content = result_str if len(result_str) < 8000 else result_str[:8000] + "\n\n[Warning: Output truncated to 8000 chars]"
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": func_name,
                            "content": safe_content
                        })
                    # loop wapas shuru ho raha hai taaki model tool ka output dekh kar aage badh sake
                    continue
                else:
                    # agar model ne beech me user se permission mangne ki koshish ki toh auto pilot bypass kar dega
                    permission_phrases = [
                        "would you like me to", "shall i proceed", "should i run",
                        "do you want me to", "let me know if you want", "shall i begin",
                        "would you like to proceed", "shall we proceed"
                    ]
                    if len(executed_tools_this_turn) == 0 and msg.content and any(p in msg.content.lower() for p in permission_phrases):
                        console.print("[dim yellow][*] Auto-Pilot: Bypassing confirmation and executing tools autonomously...[/dim yellow]")
                        messages.append({
                            "role": "user",
                            "content": "Execute the relevant tools autonomously right now without asking for permission. Begin the assessment immediately."
                        })
                        continue

                    # jab sare tools chal chuke hain toh final text response user ko deliver karo
                    total_duration = time.time() - turn_start_time
                    if msg.content:
                        console.print("\n")
                        console.print(Panel(
                            Markdown(msg.content),
                            title=f"[bold red]RAVAN CYBER INTELLIGENCE[/bold red] [dim]({total_duration:.2f}s)[/dim]",
                            border_style="red",
                            padding=(1, 2)
                        ))
                        
                        # poori security report ko markdown file me auto save kar rahe hain
                        report_file = save_markdown_report(
                            prompt=user_input,
                            model=current_model,
                            mode=current_mode,
                            tools=executed_tools_this_turn,
                            content=msg.content,
                            duration=total_duration
                        )
                        console.print(f"[bold green][+] Markdown Report Saved:[/bold green] [bold underline cyan]{report_file}[/bold underline cyan]\n")
                    break

        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold red][*] Exiting RAVAN. Session terminated.[/bold red]\n")
            break
        except Exception as e:
            console.print(f"[bold red][x] An unexpected error occurred: {str(e)}[/bold red]\n")

if __name__ == "__main__":
    main()
