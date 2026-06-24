---
description: LLM Setup — configure LLM mode and models
---

# LLM Setup

Configure LLM mode and download models.

## Usage

| Command | Description |
|---------|-------------|
| /llm-setup auto | Auto-detect GPU + recommend model |
| /llm-setup eco | No LLM, zero GPU |
| /llm-setup on | Use default model |
| /llm-setup hot | qwen3.5-0.8b (~600MB) |
| /llm-setup balance | qwen3.5-2b (~1.4GB) |
| /llm-setup performance | qwen3.5-4b (~2.5GB) |
| /llm-setup list | Show all profiles + status |
| /llm-setup pull [profile] | Download GGUF model |
| /llm-setup status | Show GPU + Ollama status |
| /llm-setup remove | Remove all models |
