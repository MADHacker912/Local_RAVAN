#!/usr/bin/env python3
# fastmcp tools aur ravan ke web surfing tools ko openrouter ke format me bind karne wala manager

import sys
import os
import json
import logging
import subprocess
from typing import Dict, Any, List, Optional, Tuple

from browser_surfer import surf_webpage

# fastmcp aur requests ke faltu logs ko band kar rahe hain taaki screen saaf rahe
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# agar hexstrike ki directory exist karti hai toh usko python path me daal do
HEXSTRIKE_DIR = os.environ.get("HEXSTRIKE_DIR", "/home/obito/hexstrike-ai")
if HEXSTRIKE_DIR not in sys.path and os.path.exists(HEXSTRIKE_DIR):
    sys.path.insert(0, HEXSTRIKE_DIR)

AGENT_BROWSER_SCRIPT = "/home/obito/.agents/skills/agent-live-browser/scripts/agent_browser.py"

BUGBOUNTY_KEYWORDS = [
    "nmap", "gobuster", "nuclei", "dirb", "dirsearch", "ffuf", "sqlmap",
    "dalfox", "httpx", "subfinder", "amass", "arjun", "katana", "gau",
    "waybackurls", "wpscan", "wafw00f", "nikto", "bugbounty", "xsser", "x8",
    "recon", "paramspider", "jaeles", "uro", "qsreplace", "web_surf", "browser"
]

MALWARE_KEYWORDS = [
    "radare2", "gdb", "strings", "exiftool", "binwalk", "checksec", "objdump",
    "xxd", "ghidra", "pwntools", "volatility", "foremost", "steghide",
    "hashcat", "john", "hashpump", "ropgadget", "ropper", "pwninit",
    "angr", "libc_database", "one_gadget"
]

ESSENTIAL_TOOLS = [
    "web_surf_target", "agent_live_browser", "server_health", "execute_command",
    "create_file", "modify_file", "list_files", "execute_python_script",
    "generate_payload", "intelligent_smart_scan"
]

# apne banaye huye browser aur search tools ke schemas yahan define kiye hain
CUSTOM_TOOLS_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "web_surf_target",
            "description": (
                "Deeply surf and scrape any web application, target URL, or bug bounty program link "
                "(HackerOne, Bugcrowd, Intigriti, disclosure pages, or web apps). Extracts in-scope assets/domains, "
                "out-of-scope policies, internal links, API endpoints, HTML forms, input parameters, technologies, "
                "and security headers. Call this FIRST whenever the user gives you a link/target to investigate."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The target website or bug bounty program URL to surf"
                    },
                    "extract_scope": {
                        "type": "boolean",
                        "description": "Whether to extract in-scope wildcard domains and scope rules",
                        "default": True
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search_osint",
            "description": (
                "Search the public web (via DuckDuckGo) for target background, what the platform actually does, "
                "past disclosed bug bounty writeups, HackerOne reports, or known CVEs."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g. 'company.com what is this platform', 'company.com bug bounty writeup')"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Max search results to retrieve",
                        "default": 4
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "agent_live_browser",
            "description": (
                "Control persistent live Chromium browser with interactive streaming on http://localhost:7654. "
                "Use for complex SPAs, clicking elements, submitting forms, or solving logins/interactive tasks."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Browser command to execute",
                        "enum": ["goto", "read", "click", "type", "screenshot", "status"]
                    },
                    "target_or_text": {
                        "type": "string",
                        "description": "Target URL for 'goto', CSS selector or text for 'click', or input text for 'type'",
                        "default": ""
                    }
                },
                "required": ["command"]
            }
        }
    }
]

class HexStrikeToolsManager:
    def __init__(self, server_url: str = "http://127.0.0.1:8888"):
        self.server_url = server_url
        self.client = None
        self.mcp_server = None
        self.tools_map: Dict[str, Any] = {}
        self.available = False
        self._initialize()

    def _initialize(self):
        try:
            from hexstrike_mcp import HexStrikeClient, setup_mcp_server
            self.client = HexStrikeClient(self.server_url)
            self.mcp_server = setup_mcp_server(self.client)
            if hasattr(self.mcp_server, '_tool_manager') and hasattr(self.mcp_server._tool_manager, '_tools'):
                self.tools_map = self.mcp_server._tool_manager._tools
                self.available = True
        except Exception as e:
            self.available = False
            self.error_msg = str(e)

    def get_tool_names(self) -> List[str]:
        names = ["web_surf_target", "web_search_osint", "agent_live_browser"]
        names.extend(list(self.tools_map.keys()))
        return names

    def get_openai_tools(self, mode: str = "all", max_tools: int = 120) -> List[Dict[str, Any]]:
        """
        Convert FastMCP tools into OpenAI function calling format, prepending custom browser tools.
        """
        schemas = list(CUSTOM_TOOLS_SCHEMAS)
        mode = mode.lower()

        for name, tool in self.tools_map.items():
            # agar tool pehle se custom list me hai toh dubara add mat karo
            if name in ["web_surf_target", "web_search_osint", "agent_live_browser"]:
                continue

            # selected mode ke hisab se tools ko filter kar rahe hain jaise bugbounty ya malware
            if mode == "bugbounty":
                if not any(k in name for k in BUGBOUNTY_KEYWORDS) and name not in ESSENTIAL_TOOLS:
                    continue
            elif mode == "malware":
                if not any(k in name for k in MALWARE_KEYWORDS) and name not in ESSENTIAL_TOOLS:
                    continue
            elif mode == "essential":
                if name not in ESSENTIAL_TOOLS:
                    continue

            # openrouter ke liye tool ka function calling schema bana rahe hain
            desc = (tool.description or f"Execute HexStrike tool {name}").strip()
            if len(desc) > 800:
                desc = desc[:797] + "..."

            parameters = getattr(tool, "parameters", None)
            if not parameters or not isinstance(parameters, dict):
                parameters = {"type": "object", "properties": {}}

            parameters = dict(parameters)
            parameters.pop("title", None)

            schemas.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": desc,
                    "parameters": parameters
                }
            })

            if len(schemas) >= max_tools:
                break

        return schemas

    def execute_tool(self, name: str, args: Dict[str, Any]) -> Tuple[bool, Any]:
        # fastmcp ya custom browser tools ko execute karne ka main function

        # pehla custom tool jo target url ko deeply surf karta hai
        if name == "web_surf_target":
            try:
                url = args.get("url", "")
                extract_scope = args.get("extract_scope", True)
                res = surf_webpage(url, extract_scope=extract_scope)
                success = res.get("status") == "success"
                return success, res
            except Exception as e:
                return False, f"Failed to surf {args.get('url')}: {str(e)}"

        # doosra tool jo target ke baare me internet pe search karke osint nikalta hai
        elif name == "web_search_osint":
            try:
                from browser_surfer import search_web
                query = args.get("query", "")
                max_results = args.get("max_results", 4)
                hits = search_web(query, max_results=max_results)
                return True, {"query": query, "results": hits}
            except Exception as e:
                return False, f"Search failed: {str(e)}"

        # teesra tool jo live chromium browser ko control karta hai
        elif name == "agent_live_browser":
            try:
                cmd_type = args.get("command", "status")
                target = args.get("target_or_text", "")
                cmd = ["python3", AGENT_BROWSER_SCRIPT, cmd_type]
                if target:
                    cmd.append(target)
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
                output = proc.stdout.strip() or proc.stderr.strip() or "Command completed with no output."
                return (proc.returncode == 0), {
                    "action": cmd_type,
                    "output": output,
                    "live_stream": "http://localhost:7654"
                }
            except Exception as e:
                return False, f"agent_live_browser error: {str(e)}"

        # baki bache huye hexstrike ke fastmcp tools ko execute karne ka block
        if name not in self.tools_map:
            return False, f"Error: Tool '{name}' not found in HexStrike."

        tool = self.tools_map[name]
        try:
            if hasattr(tool, "fn"):
                result = tool.fn(**args)
                return True, result
            else:
                return False, f"Tool '{name}' has no callable function."
        except Exception as e:
            return False, f"Tool execution failed with exception: {str(e)}"
