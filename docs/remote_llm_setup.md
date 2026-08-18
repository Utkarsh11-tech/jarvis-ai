# JARVIS Remote LLM Setup

## Target architecture

```text
JARVIS laptop
  ├─ full JARVIS application
  ├─ XTTS architecture unchanged
  ├─ local Ollama + qwen3:8b (fallback)
  └─ LLM router
       ├─ AUTO  -> remote Ollama first -> local Ollama fallback
       ├─ REMOTE -> remote Ollama only
       └─ LOCAL  -> local Ollama only

Dedicated free computer
  └─ Ollama + qwen3:8b only
       └─ LAN endpoint: http://<LAN-IP>:11434
```

The RTX 5050/XTTS computer is not part of the LLM path.

## Remote computer

Install Ollama, then pull the same model used by the JARVIS laptop:

```powershell
ollama pull qwen3:8b
ollama list
```

Ollama must listen on the LAN rather than only loopback. On Windows, configure the Ollama host environment so it binds to the machine's LAN interface, then restart Ollama.

Use the remote computer's LAN IPv4 address in JARVIS as:

```text
http://<LAN-IP>:11434
```

Allow inbound TCP 11434 through Windows Firewall only on the trusted private network.

## JARVIS laptop

Keep local Ollama and the local Qwen model installed. Copy `.env.example` to `.env` and replace the placeholder remote IP:

```text
JARVIS_LLM_MODE=AUTO
JARVIS_LLM_REMOTE_HOST=http://192.168.1.100:11434
JARVIS_LLM_REMOTE_MODEL=qwen3:8b
JARVIS_LLM_LOCAL_HOST=http://127.0.0.1:11434
JARVIS_LLM_LOCAL_MODEL=qwen3:8b
JARVIS_LLM_TIMEOUT=30
```

Do not commit the real `.env` file.

## Routing behavior

- `AUTO`: every LLM decision tries the dedicated remote computer first. If that Ollama request fails, JARVIS retries locally.
- `REMOTE`: only the dedicated computer is used. A remote failure is surfaced instead of silently switching machines.
- `LOCAL`: only the laptop's Ollama is used.

The router is for the LLM layer only. Existing rule-based automation and XTTS remain separate.

## Network test

From the JARVIS laptop, verify the remote Ollama endpoint before running the full assistant. For example, use the remote machine's Ollama API endpoint from a browser or PowerShell request and confirm it responds.

Then run the project's LLM tests and the existing test suite in the JARVIS Python environment.

## Important separation

Do not install JARVIS on the dedicated LLM computer. It only needs Ollama and the selected model. Do not point the LLM router at the RTX 5050/XTTS machine.
