#!/usr/bin/env python3
# local llm inference engine aur openai compatible client adapter
# airllm aur transformers ke zariye low memory layer by layer inference chalata hai
# autonomous tool calling aur json parsing ko seamlessly handle karta hai

import os
import sys
import json
import re
import time
import uuid
import warnings
warnings.filterwarnings("ignore")
from pathlib import Path
from typing import List, Dict, Any, Optional

# openrouter aur openai ke response format jaisi mock classes
class LocalFunctionCall:
    def __init__(self, name: str, arguments: str):
        self.name = name
        self.arguments = arguments

class LocalToolCall:
    def __init__(self, tool_id: str, name: str, arguments: str):
        self.id = tool_id
        self.type = "function"
        self.function = LocalFunctionCall(name, arguments)

class LocalMessage:
    def __init__(self, content: Optional[str], tool_calls: Optional[List[LocalToolCall]] = None):
        self.role = "assistant"
        self.content = content
        self.tool_calls = tool_calls or []

    # openai sdk ke model_dump format me dictionary return karne ka method
    def model_dump(self, exclude_unset: bool = True) -> Dict[str, Any]:
        data = {
            "role": "assistant",
            "content": self.content
        }
        if self.tool_calls:
            data["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in self.tool_calls
            ]
        return data

class LocalChoice:
    def __init__(self, message: LocalMessage):
        self.index = 0
        self.message = message
        self.finish_reason = "tool_calls" if message.tool_calls else "stop"

class LocalChatCompletion:
    def __init__(self, message: LocalMessage):
        self.id = f"chatcmpl-local-{uuid.uuid4().hex[:8]}"
        self.created = int(time.time())
        self.choices = [LocalChoice(message)]

# messages aur tools ko local model ke format me prompt banane ka function
def format_prompt_with_tools(messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]]) -> str:
    prompt_parts = []
    
    # system instruction me tools call karne ka format samjha rahe hain
    tool_instructions = ""
    if tools:
        tool_instructions = "\n\nAvailable Security Tools:\n"
        for t in tools:
            fn = t.get("function", {})
            name = fn.get("name", "")
            desc = fn.get("description", "")
            params = fn.get("parameters", {})
            tool_instructions += f"- Tool: {name}\n  Description: {desc}\n  Parameters: {json.dumps(params)}\n\n"
        
        tool_instructions += (
            "To execute a security tool autonomously, output your action using the exact JSON format:\n"
            "```json\n"
            "{\n"
            '  "tool": "<tool_name>",\n'
            '  "parameters": { ... }\n'
            "}\n"
            "```\n"
            "Do not ask user permission. Execute the required tool directly."
        )

    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "") or ""
        
        if role == "system":
            prompt_parts.append(f"<|im_start|>system\n{content}{tool_instructions}<|im_end|>")
        elif role == "user":
            prompt_parts.append(f"<|im_start|>user\n{content}<|im_end|>")
        elif role == "assistant":
            # assistant response me tool calls check kar rahe hain
            tc_text = ""
            if "tool_calls" in msg and msg["tool_calls"]:
                for tc in msg["tool_calls"]:
                    fn_name = tc.get("function", {}).get("name", "")
                    fn_args = tc.get("function", {}).get("arguments", "{}")
                    tc_text += f"\n```json\n{{\"tool\": \"{fn_name}\", \"parameters\": {fn_args}}}\n```\n"
            full_assistant = f"{content}\n{tc_text}".strip()
            prompt_parts.append(f"<|im_start|>assistant\n{full_assistant}<|im_end|>")
        elif role == "tool":
            tool_name = msg.get("name", "tool")
            prompt_parts.append(f"<|im_start|>tool\nTool [{tool_name}] output:\n{content}<|im_end|>")

    prompt_parts.append("<|im_start|>assistant\n")
    return "\n".join(prompt_parts)

# model output me se tool call json dhoondh kar parse karne ka function
def parse_tool_calls_from_text(text: str, tools: Optional[List[Dict[str, Any]]]) -> Tuple[Optional[str], List[LocalToolCall]]:
    tool_names = set()
    if tools:
        for t in tools:
            fn = t.get("function", {})
            if "name" in fn:
                tool_names.add(fn["name"])

    tool_calls = []
    
    # json blocks match kar rahe hain
    json_blocks = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    
    # direct curly braces match
    if not json_blocks:
        json_blocks = re.findall(r"(\{\s*\"tool\"\s*:\s*\"[^\"]+\".*?\})", text, re.DOTALL)

    for block in json_blocks:
        try:
            data = json.loads(block)
            tool_name = data.get("tool") or data.get("name") or data.get("function")
            params = data.get("parameters") or data.get("arguments") or data.get("args") or {}
            
            if tool_name and (not tool_names or tool_name in tool_names):
                call_id = f"call_{uuid.uuid4().hex[:8]}"
                args_str = json.dumps(params) if isinstance(params, dict) else str(params)
                tool_calls.append(LocalToolCall(call_id, tool_name, args_str))
        except Exception:
            continue

    # agar tool call mil gaya toh text response clean kar rahe hain
    cleaned_content = text
    for b in json_blocks:
        cleaned_content = cleaned_content.replace(b, "").replace("```json", "").replace("```", "").strip()

    return cleaned_content or None, tool_calls

# local inference chalane wala main class
class LocalLLMCompletions:
    def __init__(self, parent_client):
        self.client = parent_client

    def create(self, model: str = "", messages: List[Dict[str, Any]] = None, tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> LocalChatCompletion:
        messages = messages or []
        prompt = format_prompt_with_tools(messages, tools)

        raw_output = self.client.generate(prompt, max_tokens=kwargs.get("max_tokens", 2048))
        content, tool_calls = parse_tool_calls_from_text(raw_output, tools)

        msg = LocalMessage(content=content, tool_calls=tool_calls)
        return LocalChatCompletion(msg)

class LocalChat:
    def __init__(self, parent_client):
        self.completions = LocalLLMCompletions(parent_client)

class LocalLLMClient:
    def __init__(self, model_path: str, backend: str = "airllm"):
        self.model_path = model_path
        self.backend = backend
        self.model = None
        self.tokenizer = None
        self.chat = LocalChat(self)
        self.is_loaded = False
        self._load_model()

    # airllm ya transformers ke zariye model load karne ka internal method
    def _load_model(self):
        print(f"[*] Initializing Local LLM Engine ({self.backend}) from: {self.model_path}...")
        try:
            from transformers import AutoTokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
            
            if self.backend == "airllm":
                from airllm import AutoModel
                # airllm layer by layer memory offload use karta hai
                self.model = AutoModel.from_pretrained(self.model_path)
            else:
                from transformers import AutoModelForCausalLM
                import torch
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else "cpu",
                    trust_remote_code=True
                )
            self.is_loaded = True
            print("[+] Local LLM model loaded successfully.")
        except Exception as e:
            print(f"[!] Warning: Local model loading deferred or failed: {str(e)}")
            self.is_loaded = False

    # prompt se text generate karne ka method
    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        if not self.is_loaded or self.model is None:
            # fallback mock output agar model weights load na huye hon
            return "Local model weights are not loaded. Please ensure model directory exists in models/ folder."

        try:
            if self.backend == "airllm":
                input_tokens = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
                output = self.model.generate(
                    input_tokens["input_ids"],
                    max_new_tokens=max_tokens,
                    use_cache=True,
                    return_dict_in_generate=True
                )
                generated_text = self.tokenizer.decode(output.sequences[0], skip_special_tokens=True)
            else:
                input_ids = self.tokenizer.encode(prompt, return_tensors="pt")
                output_ids = self.model.generate(input_ids, max_new_tokens=max_tokens, do_sample=False)
                generated_text = self.tokenizer.decode(output_ids[0][len(input_ids[0]):], skip_special_tokens=True)

            return generated_text
        except Exception as err:
            return f"[Local Inference Error: {str(err)}]"
