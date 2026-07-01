# nomad-os
Rasperry Pi Nomad

## Local chat

Install the project in editable mode:

```powershell
python -m pip install -e .
```

Start a terminal chat:

```powershell
python -m nomad.main chat
```

Start the HTTP API:

```powershell
python -m nomad.main serve
```

Then send a text message to Nomad:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/chat -ContentType "application/json" -Body '{"message":"hello nomad"}'
```

## Local LLM with LM Studio

Nomad's brain is configured to use LM Studio's OpenAI-compatible local server by
default:

```yaml
ai:
  provider: lmstudio
  fallback_to_echo: true
  lmstudio:
    model: llama-3.2-1b-instruct
    base_url: http://127.0.0.1:1234/v1
    timeout_seconds: 120
```

In LM Studio:

1. Download and load a small instruct/chat model.
2. Start the local server.
3. Confirm the server is listening at `http://127.0.0.1:1234`.
4. Set `ai.lmstudio.model` to the model id shown by LM Studio.

Then start a terminal chat:

```powershell
python -m nomad.main chat
```

If LM Studio is not running, `fallback_to_echo: true` keeps local chat usable
with the simple `I heard: ...` response.

## Local LLM with Ollama

Ollama is still a good Raspberry Pi option. To use it, change `config/settings.yaml`:

```yaml
ai:
  provider: ollama
  fallback_to_echo: true
  ollama:
    model: llama3.2:1b
    base_url: http://localhost:11434/api
    timeout_seconds: 120
```

On a Raspberry Pi, start with a small model:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2:1b
ollama serve
```

Other lightweight models to try:

```bash
ollama pull qwen2.5:0.5b
ollama pull gemma3:1b
```
