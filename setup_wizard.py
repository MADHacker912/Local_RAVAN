#!/usr/bin/env python3
# ravan first time setup wizard
# cloud api aur local uncensored models ke beech switch karne ki suvidha deta hai
# system hardware audit karta hai aur pure system se local models scan karta hai

import os
import sys
import shutil
import urllib.request
import json
import warnings
warnings.filterwarnings("ignore")
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List

import psutil
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

from config import load_config, save_config

console = Console()

MODELS_DIR = Path("/home/obito/hex-cyber-agent/models")

# verified aur working uncensored offensive security models
CURATED_LOCAL_MODELS = [
    {
        "id": "dolphin-2.9-llama3-8b",
        "name": "Dolphin 2.9 Llama-3 8B (Uncensored / Offensive Security)",
        "hf_repo": "cognitivecomputations/dolphin-2.9-llama3-8b",
        "size_gb": 4.5,
        "min_ram_gb": 8.0,
        "desc": "Elite uncensored model for exploit reasoning, offensive intelligence, and white-hat operations"
    },
    {
        "id": "qwen2.5-coder-3b-instruct",
        "name": "Qwen 2.5 Coder 3B Instruct (Exploit & Code Audit)",
        "hf_repo": "Qwen/Qwen2.5-Coder-3B-Instruct",
        "size_gb": 3.0,
        "min_ram_gb": 6.0,
        "desc": "Specialized code intelligence for vulnerability hunting, reversing payloads, and script analysis"
    },
    {
        "id": "llama-3.2-3b-abliterated",
        "name": "Llama 3.2 3B Instruct Abliterated (Fast Uncensored)",
        "hf_repo": "huihui-ai/Llama-3.2-3B-Instruct-abliterated",
        "size_gb": 2.5,
        "min_ram_gb": 6.0,
        "desc": "Lightweight abliterated model optimized for fast responses and constrained RAM machines"
    }
]

# system ke hardware resources jaise ram cpu aur disk space audit karta hai
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

# pure system se sabhi local models scan karta hai (ollama, local folders, cache)
def scan_local_models() -> List[Dict[str, Any]]:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    models = []

    # 1. active ollama service scan kar rahe hain
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags", headers={"User-Agent": "RAVAN-Agent"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode())
            for m in data.get("models", []):
                size_gb = m.get("size", 0) / (1024 ** 3)
                models.append({
                    "name": m["name"],
                    "backend": "ollama",
                    "path": "http://127.0.0.1:11434/v1",
                    "size": f"{size_gb:.1f} GB",
                    "source": "Ollama Service",
                    "installed": True,
                    "desc": "Locally running Ollama model (Instant activation, no download required)"
                })
    except Exception:
        pass

    # 2. local directories me maujood models check kar rahe hain
    scan_paths = [
        MODELS_DIR,
        Path("/home/obito/custom_models"),
        Path.home() / ".cache/lm-studio/models"
    ]

    for p in scan_paths:
        if p.exists() and p.is_dir():
            for item in p.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    # sirf wahi directories le rahe hain jinme files maujood hain
                    try:
                        if any(item.iterdir()):
                            models.append({
                                "name": item.name,
                                "backend": "airllm",
                                "path": str(item),
                                "size": "Local Dir",
                                "source": f"{p.name}/",
                                "installed": True,
                                "desc": f"Local directory model located in {p}"
                            })
                    except Exception:
                        pass
                elif item.suffix.lower() in [".gguf", ".safetensors", ".bin"]:
                    sz = item.stat().st_size / (1024 ** 2)
                    models.append({
                        "name": item.name,
                        "backend": "airllm",
                        "path": str(item),
                        "size": f"{sz:.1f} MB",
                        "source": f"{p.name}/",
                        "installed": True,
                        "desc": f"Local model file in {p}"
                    })

    # 3. huggingface hub cache me downloaded models check kar rahe hain
    hf_hub = Path.home() / ".cache/huggingface/hub"
    if hf_hub.exists():
        for item in hf_hub.iterdir():
            if item.name.startswith("models--"):
                clean = item.name.replace("models--", "").replace("--", "/")
                if "whisper" in clean.lower():
                    continue
                snaps = item / "snapshots"
                if snaps.exists() and any(snaps.iterdir()):
                    models.append({
                        "name": clean,
                        "backend": "airllm",
                        "path": str(item),
                        "size": "Cached",
                        "source": "HuggingFace Cache",
                        "installed": True,
                        "desc": "Pre-downloaded HuggingFace cache"
                    })

    return models

# huggingface se snapshot download karne ka function
def download_hf_model(repo_id: str, target_dir: Path) -> bool:
    try:
        from huggingface_hub import snapshot_download
        console.print(f"\n[bold cyan][*] Downloading model snapshot from HuggingFace: {repo_id}[/bold cyan]")
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

# cloud api provider configure karne ka function
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

# local llm setup aur model selector wizard
def setup_local_llm(config: dict, specs: Dict[str, Any]) -> dict:
    total_ram = specs["total_ram"]

    # ram 4gb ya usse kam hone par execution block kar rahe hain
    if total_ram <= 4.0:
        console.print(Panel(
            f"[bold red][x] HARDWARE SPECIFICATION INSUFFICIENT FOR LOCAL LLM[/bold red]\n\n"
            f"Detected Total RAM: [bold yellow]{total_ram:.2f} GB[/bold yellow]\n\n"
            "[bold red]System requirement check failed:[/bold red] Local LLM execution requires at least [bold green]6 GB - 8 GB RAM[/bold green].\n"
            "Running an LLM on 4 GB RAM will lead to system freezes and Out-Of-Memory kernel panics.\n\n"
            "[bold cyan]Recommended Action:[/bold cyan] Please use Cloud API (Option 1) or an external server.",
            title="[bold red]LOCAL LLM BLOCKED[/bold red]",
            border_style="red"
        ))
        console.input("\n[dim]Press Enter to switch to Cloud API setup...[/dim]")
        return setup_api_provider(config)

    console.print(Panel(
        f"[bold green]System Hardware Audit:[/bold green]\n"
        f"• Total RAM: [bold yellow]{total_ram:.2f} GB[/bold yellow] (Available: {specs['available_ram']:.2f} GB)\n"
        f"• CPU Cores: [bold yellow]{specs['cores']}[/bold yellow]\n"
        f"• GPU Acceleration: [bold yellow]{specs['gpu_name']}[/bold yellow] (CUDA: {specs['cuda_available']})\n"
        f"• Free Disk Space: [bold yellow]{specs['disk_free']:.2f} GB[/bold yellow]\n"
        f"• Local Models Directory: [bold cyan]{MODELS_DIR}[/bold cyan]\n"
        f"  [dim](Tip: You can also place custom GGUF/SafeTensors models directly inside this folder)[/dim]",
        title="[bold red]SYSTEM HARDWARE & LOCAL AUDIT[/bold red]",
        border_style="green"
    ))

    # pure system se installed aur cached models dhoondh rahe hain
    with console.status("[bold cyan][*] Scanning system for installed local models (Ollama, HF Cache, models/)...[/bold cyan]", spinner="dots"):
        existing_models = scan_local_models()

    table = Table(title="Local AI Models (Detected On System & Available Downloads)", border_style="red", show_lines=True)
    table.add_column("#", style="bold yellow", width=4)
    table.add_column("Model Name", style="bold cyan")
    table.add_column("Engine / Source", style="magenta")
    table.add_column("Size", style="green")
    table.add_column("Status / Description", style="dim white")

    idx = 1
    # pehle system me maujood installed models dikha rahe hain
    for m in existing_models:
        status_label = f"[bold green][INSTALLED][/bold green] {m['desc']}"
        source_label = f"{m['backend'].upper()} ({m['source']})"
        table.add_row(str(idx), m["name"], source_label, m["size"], status_label)
        idx += 1

    # curated downloadable models add kar rahe hain
    for cm in CURATED_LOCAL_MODELS:
        table.add_row(
            str(idx),
            f"[bold white]{cm['name']}[/bold white]",
            "AirLLM (Download)",
            f"{cm['size_gb']} GB",
            f"[dim yellow][DOWNLOAD][/dim yellow] {cm['desc']}"
        )
        idx += 1

    console.print(table)

    # hardware recommendation nikal rahe hain
    if existing_models:
        recommended_idx = 1
        rec_name = existing_models[0]["name"]
        rec_type = "Installed Local Model"
    else:
        if total_ram >= 12.0:
            recommended_idx = len(existing_models) + 1
            rec_model = CURATED_LOCAL_MODELS[0]
        elif total_ram >= 8.0:
            recommended_idx = len(existing_models) + 2
            rec_model = CURATED_LOCAL_MODELS[1]
        else:
            recommended_idx = len(existing_models) + 3
            rec_model = CURATED_LOCAL_MODELS[2]
        rec_name = rec_model["name"]
        rec_type = "HuggingFace Download"

    console.print(f"\n[bold green][+] Recommended for your system ({total_ram:.1f} GB RAM):[/bold green] [bold yellow]Option {recommended_idx} ({rec_name})[/bold yellow]")
    choice_str = console.input(f"[bold cyan]Enter option number to select [default: {recommended_idx}]: [/bold cyan]").strip() or str(recommended_idx)

    try:
        choice_num = int(choice_str)
    except ValueError:
        choice_num = recommended_idx

    # 1. user ne installed local model select kiya
    if existing_models and 1 <= choice_num <= len(existing_models):
        sel = existing_models[choice_num - 1]
        selected_model_name = sel["name"]
        backend = sel["backend"]

        config["PROVIDER_TYPE"] = "local"
        config["LOCAL_BACKEND"] = backend
        config["LOCAL_MODEL_NAME"] = selected_model_name
        config["DEFAULT_MODEL"] = selected_model_name

        if backend == "ollama":
            config["OLLAMA_BASE_URL"] = "http://127.0.0.1:11434/v1"
            config["API_BASE_URL"] = "http://127.0.0.1:11434/v1"
            config["LOCAL_MODEL_PATH"] = "ollama"
        else:
            config["LOCAL_MODEL_PATH"] = sel["path"]

        save_config(config)

        console.print(Panel(
            f"[bold green]Local Model Activated Successfully![/bold green]\n\n"
            f"• Active Model: [bold yellow]{selected_model_name}[/bold yellow]\n"
            f"• Inference Engine: [bold cyan]{backend.upper()}[/bold cyan]\n"
            f"• Storage Location: [dim]{sel['path']}[/dim]\n\n"
            f"[bold white]Ready for autonomous cybersecurity operations with zero internet dependency.[/bold white]",
            title="[bold green]LOCAL MODEL ONLINE[/bold green]",
            border_style="green"
        ))
        return config

    # 2. user ne downloadable curated model select kiya
    offset = len(existing_models)
    curated_index = choice_num - offset - 1
    if 0 <= curated_index < len(CURATED_LOCAL_MODELS):
        sel = CURATED_LOCAL_MODELS[curated_index]
    else:
        sel = CURATED_LOCAL_MODELS[0]

    model_dir = MODELS_DIR / sel["id"]
    selected_model_name = sel["name"]
    selected_model_path = str(model_dir)

    # agar model pehle se downloaded hai
    if model_dir.exists() and any(model_dir.iterdir()):
        console.print(f"\n[bold green][+] Model already exists in local directory: {model_dir}[/bold green]\n")
    else:
        console.print(f"\n[bold yellow]Target Model:[/bold yellow] {sel['name']}")
        console.print(f"Estimated Download Size: [bold magenta]{sel['size_gb']} GB[/bold magenta]")
        confirm = console.input("[bold cyan]Start download from HuggingFace? (y/n) [default: y]: [/bold cyan]").strip().lower() or "y"

        if confirm in ["y", "yes"]:
            download_success = download_hf_model(sel["hf_repo"], model_dir)
            if not download_success:
                console.print("[yellow][!] Model download could not be completed. Falling back to Cloud API setup.[/yellow]")
                return setup_api_provider(config)
        else:
            console.print(f"\n[yellow][!] Download cancelled. You can manually place model files in: {MODELS_DIR}[/yellow]\n")
            return config

    config["PROVIDER_TYPE"] = "local"
    config["LOCAL_MODEL_NAME"] = selected_model_name
    config["LOCAL_MODEL_PATH"] = selected_model_path
    config["LOCAL_BACKEND"] = "airllm"
    config["DEFAULT_MODEL"] = selected_model_name
    save_config(config)

    console.print(Panel(
        f"[bold green]Local LLM Configured Successfully![/bold green]\n\n"
        f"• Active Model: [bold yellow]{selected_model_name}[/bold yellow]\n"
        f"• Model Storage: [cyan]{selected_model_path}[/cyan]\n"
        f"• Inference Engine: [magenta]AirLLM (Layer-by-Layer Offloading)[/magenta]\n\n"
        f"[bold white]Ready for autonomous cybersecurity operations with zero internet dependency.[/bold white]",
        title="[bold green]LOCAL AIRLLM READY[/bold green]",
        border_style="green"
    ))
    return config

# main interactive first-startup setup function
def run_setup_wizard(force: bool = False) -> dict:
    config = load_config()

    # agar pehle se configured hai aur force nahi kiya gaya toh bypass karo
    if not force and (config.get("API_KEY") or config.get("OPENROUTER_API_KEY") or config.get("LOCAL_MODEL_NAME")):
        return config

    specs = get_system_specs()

    console.print(Panel(
        "[bold white]Welcome to RAVAN Cybersecurity AI Agent Setup[/bold white]\n"
        "[dim]Choose how RAVAN should power its reasoning & autonomous offensive security engine:[/dim]\n\n"
        "[bold yellow][1] Cloud AI API[/bold yellow] (OpenRouter, ChatGPT, Claude, Gemini, or Custom Provider)\n"
        "    • Ultra-fast reasoning & top cloud frontier models\n"
        "    • Claude 3.5 Sonnet, DeepSeek R1/Chat, GPT-4o, Llama 3.3\n\n"
        "[bold yellow][2] Local LLM[/bold yellow] (Run directly on this machine - 100% Private & Uncensored)\n"
        f"    • Automatically detects Ollama models, HuggingFace cache, and AirLLM\n"
        f"    • System Specs: [cyan]{specs['total_ram']:.1f} GB RAM[/cyan] | [cyan]{specs['cores']} Cores[/cyan] | CUDA: [cyan]{specs['cuda_available']}[/cyan]\n"
        f"    • Requires minimum 6-8 GB RAM (Status: {'[bold green]Eligible[/bold green]' if specs['total_ram'] > 4.0 else '[bold red]Blocked (RAM <= 4GB)[/bold red]'})\n"
        f"    • Custom models supported inside: [cyan]/home/obito/hex-cyber-agent/models/[/cyan]",
        title="[bold red]RAVAN FIRST TIME SETUP[/bold red]",
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
