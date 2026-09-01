"""Minimal Ollama client. Standard library only."""

import json
import urllib.error
import urllib.request

BASE_URL = "http://127.0.0.1:11434"
MODEL = "qwen3:8b"


class OllamaError(RuntimeError):
    pass


def ask(prompt: str, temperature: float = 0.0, max_tokens: int = 60, stop=None,
        raw: bool = False) -> str:
    """Send one prompt, return the raw reply.

    `stop` is a list of strings that halt generation. It matters for few-shot
    prompts: given a prompt that ends "Category:", a model will happily keep
    going and re-list all the worked examples, so the answer to the real email
    gets buried. Stopping at the next "Email:" or blank line keeps the completion
    to the one label that was asked for.

    `raw=True` bypasses the model's chat template and sends the prompt through as
    plain text to be continued. This is what a few-shot prompt needs. Without it
    llama3.2:3b treated the prompt as a chat turn and replied conversationally --
    measured as "Here are the classifications:" followed by a re-listing of the
    worked examples, with the actual answer never reached. qwen3:8b does not
    derail that way; through the chat path it answers "Category: Personal", which
    parses but is not the bare label. Raw mode returns "Personal" on both, so it
    stays.

    With raw=True the same prompt returns " Personal": the model continues the
    pattern instead of talking about it. Zero-shot is an instruction, so it is
    sent the normal way, which is also how a person would really use it.

    temperature=0 so a rerun gives the same answer. Classification is not a
    creative task, and comparing two prompting techniques only means something
    if the randomness is held still.
    """
    payload = {
        "model": MODEL,
        # qwen3 reasons by default and then returns an EMPTY "response", with the
        # chain of thought in a separate field. Every caller here parses the
        # answer, so thinking is off.
        "think": False,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }

    if stop:
        payload["options"]["stop"] = list(stop)

    if raw:
        payload["raw"] = True

    request = urllib.request.Request(
        f"{BASE_URL}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return json.loads(response.read().decode("utf-8")).get("response", "").strip()
    except urllib.error.URLError as error:
        raise OllamaError(
            f"Could not reach Ollama at {BASE_URL} ({error}). Start it with: ollama serve"
        ) from error


def check_ready() -> None:
    try:
        with urllib.request.urlopen(f"{BASE_URL}/api/tags", timeout=10) as response:
            names = {
                m["name"].split(":")[0]
                for m in json.loads(response.read().decode("utf-8")).get("models", [])
            }
    except urllib.error.URLError as error:
        raise OllamaError(f"Ollama is not running ({error}). Start it with: ollama serve") from error

    if MODEL.split(":")[0] not in names:
        raise OllamaError(f"Model {MODEL} missing. Pull it with: ollama pull {MODEL}")
