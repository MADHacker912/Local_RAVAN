#!/usr/bin/env python3
# ravan ka first time setup wizard
# user se cloud api ya local uncensored llm ka option puchhta hai
# system specs check karta hai aur 4gb se kam ram par local llm block kar deta hai

import os
import sys
import shutil
import warnings
warnings.filterwarnings("ignore")
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

import psutil
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

from config import load_config, save_config

console = Console()

MODELS_DIR = Path("/home/obito/hex-cyber-agent/models")

# 3 top uncensored aur cybersecurity ke liye behtareen models ki list
CURATED_LOCAL_MODELS = [
    {
        "id": "dolphin-2.9-llama3-8b",
        "name": "Dolphin 2.9 Llama-3 8B (Uncensored / Offensive Security)",
        "hf_repo": "cognitivecomputations/dolphin-2.9-llama3-8b",
        "size_gb": 4.5,
        "min_ram_gb": 8.0,
        "desc": "Elite uncensored model, offensive security, exploit analysis aur full ethical hacking ke liye behtareen"
    },
    {
        "id": "qwen2.5-coder-7b-abliterated",
        "name": "Qwen 2.5 Coder 7B (Uncensored / Exploit & Code Audit)",
        "hf_repo": "huihui-ai/Qwen2.5-Coder-7B-Instruct-abliterated",
        "size_gb": 4.4,
        "min_ram_gb": 8.0,
        "desc": "Code analysis, reverse engineering payloads aur custom security scripts likhne ke liye top model"
    },
    {
        "id": "llama-3.2-3b-uncensored",
        "name": "Llama 3.2 3B Instruct (Uncensored / Fast Lightweight)",
        "hf_repo": "charent/Llama-3.2-3B-Instruct-uncensored",
        "size_gb": 2.0,
        "min_ram_gb": 6.0,
        "desc": "Lightweight model jo kam ram wale system par bhi ultra fast aur smooth chalta hai"
    }
]

# system hardware specs jaise ram cpu aur gpu check karne ka function
def get_system_specs() -> Dict[str, Any]:
    mem = psutil.virtual_memory()
    total_ram = mem.total / (1024 ** 3)
    available_ram = mem.available / (1024 ** 3)
    cores = os.cpu_count() or 1
    
    cuda_available = False
    gpu_name = "None"
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            gpu_name = torch.cuda.get_device_name(0)
    except Exception:
        pass

    disk_free = shutil.disk_usage(str(MODELS_DIR.parent)).free / (1024 ** 3)

    return {
        "total_ram": total_ram,
        "available_ram": available_ram,
        "cores": cores,
        "cuda_available": cuda_available,
        "gpu_name": gpu_name,
        "disk_free": disk_free
    }

# models folder me pehle se maujood custom models scan karne ka function
def scan_local_models() -> list:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    found = []
    for item in MODELS_DIR.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            found.append({"name": item.name, "path": str(item), "type": "directory"})
        elif item.suffix.lower() in [".gguf", ".bin", ".safetensors"]:
            found.append({"name": item.name, "path": str(item), "type": "file"})
    return found

# huggingface se model download karne ka function
def download_hf_model(repo_id: str, target_dir: Path) -> bool:
    try:
        from huggingface_hub import snapshot_download
        console.print(f"\n[bold cyan][*] Downloading model from HuggingFace: {repo_id}[/bold cyan]")
        console.print(f"[dim]Destination: {target_dir}[/dim]\n")
        
        target_dir.mkdir(parents=True, exist_ok=True)
        snapshot_download(
            repo_id=repo_id,
            local_dir=str(target_dir),
            local_dir_use_symlinks=False,
            resume_download=True
        )
        console.print(f"\n[bold green][+] Model download complete: {target_dir.name}[/bold green]\n")
        return True
    except Exception as e:
        console.print(f"\n[bold red][x] Model download error: {str(e)}[/bold red]\n")
        return False

# cloud api provider setup wizard
def setup_api_provider(config: dict) -> dict:
    console.print(Panel(
        "[bold cyan]Select Cloud AI API Provider:[/bold cyan]\n\n"
        "[bold yellow][1][/bold yellow] OpenRouter (Default / Recommended - Claude 3.5, DeepSeek, GPT-4o, Llama)\n"
        "[bold yellow][2][/bold yellow] OpenAI (ChatGPT / GPT-4o / o1)\n"
        "[bold yellow][3][/bold yellow] Anthropic Claude (Direct Claude API / Compatible)\n"
        "[bold yellow][4][/bold yellow] Google Gemini (OpenAI-compatible Endpoint)\n"
        "[bold yellow][5][/bold yellow] Other / Custom Provider (Custom Base URL + API Key)",
        title="[bold red]RAVAN // API PROVIDER SETUP[/bold red]",
        border_style="cyan"
    ))

    choice = console.input("[bold cyan]Enter choice (1-5) [default: 1]: [/bold cyan]").strip() or "1"
    
    if choice == "1":
        provider = "openrouter"
        base_url = "https://openrouter.ai/api/v1"
        default_model = "anthropic/claude-3.5-sonnet"
        prompt_txt = "Enter your OpenRouter API Key (sk-or-v1-...): "
    elif choice == "2":
        provider = "openai"
        base_url = "https://api.openai.com/v1"
        default_model = "gpt-4o"
        prompt_txt = "Enter your OpenAI API Key (sk-...): "
    elif choice == "3":
        provider = "claude"
        base_url = "https://api.anthropic.com/v1"
        default_model = "claude-3-5-sonnet-20241022"
        prompt_txt = "Enter your Anthropic Claude API Key (sk-ant-...): "
    elif choice == "4":
        provider = "gemini"
        base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        default_model = "gemini-2.0-flash-exp"
        prompt_txt = "Enter your Google Gemini API Key (AIza...): "
    else:
        provider = "custom"
        base_url = console.input("[bold cyan]Enter Custom Provider Base URL (e.g. http://localhost:11434/v1 or https://api.groq.com/openai/v1): [/bold cyan]").strip()
        default_model = console.input("[bold cyan]Enter Default Model Name (e.g. llama3, mistral): [/bold cyan]").strip() or "default"
        prompt_txt = "Enter Provider API Key (leave blank if local/not required): "

    api_key = console.input(f"[bold cyan]{prompt_txt}[/bold cyan]").strip()
    if not api_key and provider in ["openrouter", "openai", "claude", "gemini"]:
        console.print("[yellow][!] Warning: No API key entered. You can set it later in ~/.hex_agent.env[/yellow]")

    config["PROVIDER_TYPE"] = "api"
    config["API_PROVIDER"] = provider
    config["API_KEY"] = api_key
    config["OPENROUTER_API_KEY"] = api_key
    config["API_BASE_URL"] = base_url
    config["OPENROUTER_BASE_URL"] = base_url
    config["DEFAULT_MODEL"] = default_model
    save_config(config)

    console.print(f"\n[bold green][+] Cloud API configured successfully! Provider: {provider.upper()}, Model: {default_model}[/bold green]\n")
    return config

# local llm setup wizard
def setup_local_llm(config: dict, specs: Dict[str, Any]) -> dict:
    total_ram = specs["total_ram"]
    
    # agar system ki ram 4gb ya usse kam hai toh local llm allow nahi hoga
    if total_ram <= 4.0:
        console.print(Panel(
            f"[bold red][x] SYSTEM SPECIFICATION INSUFFICIENT FOR LOCAL LLM[/bold red]\n\n"
            f"Detected Total RAM: [bold yellow]{total_ram:.2f} GB[/bold yellow]\n\n"
            "[bold red]System requirement check failed:[/bold red] Local LLM execution requires at least [bold green]6 GB - 8 GB RAM[/bold green].\n"
            "4 GB RAM par local LLM run karne se system freeze aur Out Of Memory crash ho jayega.\n\n"
            "[bold cyan]Action:[/bold cyan] Please use Cloud API (Option 1) or an external server (e.g. Ollama/vLLM on another machine).",
            title="[bold red]LOCAL LLM BLOCKED[/bold red]",
            border_style="red"
        ))
        console.input("\n[dim]Press Enter to switch to Cloud API setup...[/dim]")
        return setup_api_provider(config)

    console.print(Panel(
        f"[bold green]System Hardware Specs Detected:[/bold green]\n"
        f"• Total RAM: [bold yellow]{total_ram:.2f} GB[/bold yellow] (Available: {specs['available_ram']:.2f} GB)\n"
        f"• CPU Cores: [bold yellow]{specs['cores']}[/bold yellow]\n"
        f"• GPU Acceleration: [bold yellow]{specs['gpu_name']}[/bold yellow] (CUDA: {specs['cuda_available']})\n"
        f"• Free Disk Space: [bold yellow]{specs['disk_free']:.2f} GB[/bold yellow]\n"
        f"• Local Models Directory: [bold cyan]{MODELS_DIR}[/bold cyan]\n"
        f"  [dim](Tip: Aap apna koi bhi custom model is folder me khud bhi daal sakte hain!)[/dim]",
        title="[bold red]SYSTEM HARDWARE AUDIT[/bold red]",
        border_style="green"
    ))

    # pehle se models folder me maujood custom models check kar rahe hain
    existing_models = scan_local_models()
    
    table = Table(title="Select Local Uncensored Model", border_style="red")
    table.add_column("#", style="bold yellow", width=4)
    table.add_column("Model Name", style="bold cyan")
    table.add_column("Size", style="magenta")
    table.add_column("Min RAM", style="green")
    table.add_column("Description", style="dim white")

    idx = 1
    # agar user ne pehle se custom model daala hua hai toh pehle dikhao
    for m in existing_models:
        table.add_row(str(idx), f"[CUSTOM] {m['name']}", "Installed", "Local", f"Path: {m['path']}")
        idx += 1

    for cm in CURATED_LOCAL_MODELS:
        table.add_row(str(idx), cm["name"], f"{cm['size_gb']} GB", f"{cm['min_ram_gb']} GB", cm["desc"])
        idx += 1

    console.print(table)

    # hardware ke hisab se recommendation nikal rahe hain
    if total_ram >= 12.0:
        recommended_idx = 1 if not existing_models else len(existing_models) + 1
        rec_model = CURATED_LOCAL_MODELS[0]
    elif total_ram >= 8.0:
        recommended_idx = 2 if not existing_models else len(existing_models) + 2
        rec_model = CURATED_LOCAL_MODELS[1]
    else:
        recommended_idx = 3 if not existing_models else len(existing_models) + 3
        rec_model = CURATED_LOCAL_MODELS[2]

    console.print(f"\n[bold green][+] Recommended for your system ({total_ram:.1f} GB RAM):[/bold green] [bold yellow]Option {recommended_idx} ({rec_model['name']})[/bold yellow]")
    choice_str = console.input(f"[bold cyan]Enter model number to select/download [default: {recommended_idx}]: [/bold cyan]").strip() or str(recommended_idx)

    try:
        choice_num = int(choice_str)
    except ValueError:
        choice_num = recommended_idx

    selected_model_name = ""
    selected_model_path = ""

    # user ne existing custom model select kiya
    if existing_models and 1 <= choice_num <= len(existing_models):
        sel = existing_models[choice_num - 1]
        selected_model_name = sel["name"]
        selected_model_path = sel["path"]
        console.print(f"[bold green][+] Using existing local model: {selected_model_name}[/bold green]")
    else:
        # curated list me se select kiya
        offset = len(existing_models)
        curated_index = choice_num - offset - 1
        if 0 <= curated_index < len(CURATED_LOCAL_MODELS):
            sel = CURATED_LOCAL_MODELS[curated_index]
        else:
            sel = rec_model

        model_dir = MODELS_DIR / sel["id"]
        selected_model_name = sel["name"]
        selected_model_path = str(model_dir)

        # check kar rahe hain ki model pehle se downloaded hai ya nahi
        if model_dir.exists() and any(model_dir.iterdir()):
            console.print(f"\n[bold green][+] Model already downloaded in: {model_dir}[/bold green]\n")
        else:
            console.print(f"\n[bold yellow]Yeh model lage ga: {sel['name']}[/bold yellow]")
            console.print(f"Download size lagbhag [bold magenta]{sel['size_gb']} GB[/bold magenta] hai.")
            confirm = console.input("[bold cyan]Download start karein? (y/n) [default: y]: [/bold cyan]").strip().lower() or "y"
            
            if confirm in ["y", "yes"]:
                download_success = download_hf_model(sel["hf_repo"], model_dir)
                if not download_success:
                    console.print("[yellow][!] Download complete nahi ho paya. Fallback to Cloud API.[/yellow]")
                    return setup_api_provider(config)
            else:
                console.print(f"\n[yellow][!] Download cancelled. Aap model files manually is folder me daal sakte hain: {MODELS_DIR}[/yellow]\n")

    config["PROVIDER_TYPE"] = "local"
    config["LOCAL_MODEL_NAME"] = selected_model_name
    config["LOCAL_MODEL_PATH"] = selected_model_path
    config["LOCAL_BACKEND"] = "airllm"
    config["DEFAULT_MODEL"] = selected_model_name
    save_config(config)

    console.print(Panel(
        f"[bold green]Local LLM configured successfully![/bold green]\n\n"
        f"• Active Model: [bold yellow]{selected_model_name}[/bold yellow]\n"
        f"• Model Storage: [cyan]{selected_model_path}[/cyan]\n"
        f"• Inference Engine: [magenta]AirLLM (Layer-by-Layer Memory Offloading)[/magenta]\n\n"
        f"[dim]Tip: RAVAN ab bina internet API ke puri tarah local machine par chalega.[/dim]",
        title="[bold green]LOCAL LLM READY[/bold green]",
        border_style="green"
    ))
    return config

# main interactive first-startup setup function
def run_setup_wizard(force: bool = False) -> dict:
    config = load_config()
    
    # agar pehle se configured hai aur force nahi kiya gaya toh bypass karo
    if not force and (config.get("API_KEY") or config.get("OPENROUTER_API_KEY") or config.get("LOCAL_MODEL_PATH")):
        return config

    specs = get_system_specs()

    console.print(Panel(
        "[bold white]Welcome to RAVAN Cybersecurity AI Agent Setup[/bold white]\n"
        "[dim]Choose how RAVAN should power its reasoning & autonomous offensive security engine:[/dim]\n\n"
        "[bold yellow][1] Cloud AI API[/bold yellow] (OpenRouter, ChatGPT, Claude, Gemini, or Custom Provider)\n"
        "    • Ultra-fast reasoning & cloud models\n"
        "    • Claude 3.5 Sonnet, DeepSeek R1/Chat, GPT-4o, Llama 3.3\n\n"
        "[bold yellow][2] Local LLM[/bold yellow] (Run directly on this machine - 100% Private & Uncensored)\n"
        f"    • Memory-efficient AirLLM layer-by-layer offloading\n"
        f"    • System Specs: [cyan]{specs['total_ram']:.1f} GB RAM[/cyan] | [cyan]{specs['cores']} Cores[/cyan] | CUDA: [cyan]{specs['cuda_available']}[/cyan]\n"
        f"    • Requires minimum 6-8 GB RAM (Status: {'[bold green]Eligible[/bold green]' if specs['total_ram'] > 4.0 else '[bold red]Blocked (RAM <= 4GB)[/bold red]'})\n"
        f"    • Support custom model drop inside: [cyan]/home/obito/hex-cyber-agent/models/[/cyan]",
        title="[bold red]⚡ RAVAN FIRST TIME SETUP ⚡[/bold red]",
        border_style="red",
        padding=(1, 2)
    ))

    choice = console.input("[bold cyan]Select Option (1 or 2) [default: 1]: [/bold cyan]").strip() or "1"

    if choice == "2":
        return setup_local_llm(config, specs)
    else:
        return setup_api_provider(config)

if __name__ == "__main__":
    run_setup_wizard(force=True)
