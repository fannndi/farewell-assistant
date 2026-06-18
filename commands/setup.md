---
description: Setup — set LLM mode (alias for llm-setup)
---

# Setup

Alias untuk `llm-setup`. Configure LLM mode untuk session saat ini.

## Usage

```
/setup eco              GPU off, no local LLM
/setup on               Default: qwen2.5-coder-1.5b
/setup hot              qwen3.5-0.8b (~600MB VRAM)
/setup balance          qwen3.5-2b (~1.4GB VRAM)
/setup performance      qwen3.5-4b (~2.5GB VRAM)
/setup list             Show all profiles + status
/setup auto             GPU-aware auto profile selection
/setup pull -Profile X  Download GGUF + import to Ollama
/setup status           GPU + Ollama + models + GGUF files
/setup remove           Wipe all models + GGUF
```

Redirect ke `scripts/llm-setup.ps1`. Lihat `/llm-setup` untuk detail.
