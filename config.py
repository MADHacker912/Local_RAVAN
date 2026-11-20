# user ki configurations load aur save karne wala module
# cloud api (openrouter, openai, claude, gemini, custom) aur local uncensored llm settings manage karta hai

import os
from pathlib import Path

# user ki home directory me hidden env file ka path
ENV_PATH = Path.home() / ".hex_agent.env"

# default configuration values jab tak user apna custom setup na kare
DEFAULT_CONFIG = {
    "PROVIDER_TYPE": "api",
    "API_PROVIDER": "openrouter",
    "API_KEY": "",
    "API_BASE_URL": "https://openrouter.ai/api/v1",
    "OPENROUTER_API_KEY": "",
    "OPENROUTER_BASE_URL": "https://openrouter.ai/api/v1",
    "DEFAULT_MODEL": "anthropic/claude-3.5-sonnet",
    "LOCAL_MODEL_NAME": "",
    "LOCAL_MODEL_PATH": "",
    "LOCAL_BACKEND": "airllm",
    "HEXSTRIKE_SERVER": "http://127.0.0.1:8888",
    "DEFAULT_MODE": "bugbounty"
}

# config file se settings load karne ka function
def load_config() -> dict:
    config = DEFAULT_CONFIG.copy()
    if ENV_PATH.exists():
        with open(ENV_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    config[k.strip()] = v.strip().strip('"').strip("'")

    # backward compatibility ke liye openrouter keys ko sync kar rahe hain
    if config.get("OPENROUTER_API_KEY") and not config.get("API_KEY"):
        config["API_KEY"] = config["OPENROUTER_API_KEY"]
    if config.get("API_KEY") and not config.get("OPENROUTER_API_KEY"):
        config["OPENROUTER_API_KEY"] = config["API_KEY"]

    # agar system environment me koi variable pehle se set hai toh usko priority do
    for k in config:
        if k in os.environ:
            config[k] = os.environ[k]

    return config

# user ki nayi settings ya api key ko env file me save karne ka function
def save_config(config: dict):
    with open(ENV_PATH, "w") as f:
        for k, v in config.items():
            f.write(f'{k}="{v}"\n')
