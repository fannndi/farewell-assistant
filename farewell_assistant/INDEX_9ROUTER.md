# 9Router Feature Index

> Complete feature & capability index for AI-assisted lookup.
> Version: 0.5.6 | Stack: Next.js + open-sse | Port: 20128

---

## Quick Reference

| Category | Count | Key Endpoint |
|----------|-------|-------------|
| Providers | 95+ | `/v1/models` |
| API Endpoints | 150+ | `/v1/chat/completions` |
| Dashboard Pages | 20+ | `/dashboard` |
| OAuth Flows | 17 | `/api/oauth/[provider]/*` |
| Media Kinds | 9 | `/v1/embeddings`, `/v1/images/*` |
| MITM Targets | 4 IDEs | `/dashboard/mitm` |
| Executors | 21 | `open-sse/executors/` |
| Translators | 22 routes | `open-sse/translator/` |
| DB Repos | 10 | `src/lib/db/repos/` |

---

## 1. API Endpoints

### V1 Compatibility (OpenAI-compatible surface)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/models` | GET | List all available models |
| `/v1/models/{kind}` | GET | Models filtered by kind (chat/image/audio/etc) |
| `/v1/models/info` | GET | Model metadata |
| `/v1/chat/completions` | POST | **Primary** — Chat completions (SSE streaming) |
| `/v1/messages` | POST | Claude Messages API compat |
| `/v1/messages/count_tokens` | POST | Token counting (Claude format) |
| `/v1/responses` | POST | OpenAI Responses API compat |
| `/v1/responses/compact` | POST | Compact Responses API |
| `/v1/embeddings` | POST | Text embeddings |
| `/v1/images/generations` | POST | Image generation |
| `/v1/audio/speech` | POST | Text-to-speech |
| `/v1/audio/transcriptions` | POST | Speech-to-text |
| `/v1/audio/voices` | GET | List TTS voices |
| `/v1/search` | POST | Web search |
| `/v1/web/fetch` | POST | URL fetch/scrape |

### Auth

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login` | POST | Dashboard login (password/OIDC) |
| `/api/auth/logout` | POST | Dashboard logout |
| `/api/auth/status` | GET | Auth status |
| `/api/auth/reset-password` | POST | Reset password |
| `/api/auth/oidc` | GET/POST | OIDC initiate/callback |

### Providers

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/providers` | GET, POST | List/create provider connections |
| `/api/providers/[id]` | GET, PATCH, DELETE | CRUD provider |
| `/api/providers/[id]/test` | POST | Test connection |
| `/api/providers/suggested-models` | GET | Suggested models |
| `/api/providers/test-batch` | POST | Batch test connections |

### Provider Nodes (Custom Compatible)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/provider-nodes` | GET, POST | List/create compatible nodes |
| `/api/provider-nodes/[id]` | GET, PATCH, DELETE | CRUD node |
| `/api/provider-nodes/validate` | POST | Validate node config |

Node types: `openai-compatible-*`, `anthropic-compatible-*`, `custom-embedding-*`

### Models

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/models` | GET, PUT | List/update models |
| `/api/models/alias` | GET, PUT, DELETE | Model alias management |
| `/api/models/custom` | GET, POST, DELETE | Custom model management |
| `/api/models/disabled` | GET, POST, DELETE | Enable/disable models |
| `/api/models/availability` | GET | Model availability check |
| `/api/models/test` | POST | Test a model |

### Combos

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/combos` | GET, POST | List/create model combos |
| `/api/combos/[id]` | GET, PATCH, DELETE | CRUD combo |

### API Keys

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/keys` | GET, POST | List/create API keys |
| `/api/keys/[id]` | GET, PATCH, DELETE | CRUD API key |

### Usage & Monitoring

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/usage` | GET | Usage overview |
| `/api/usage/chart` | GET | Usage chart data |
| `/api/usage/history` | GET | Usage history |
| `/api/usage/logs` | GET | Request logs |
| `/api/usage/stats` | GET | Usage statistics |
| `/api/usage/providers` | GET | Per-provider usage |
| `/api/usage/request-logs` | GET | Detailed request logs |
| `/api/usage/request-details` | GET | Full request/response details |
| `/api/usage/stream` | GET | SSE stream of real-time usage events |
| `/api/usage/[connectionId]` | GET | Per-connection usage |

### Headroom

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/headroom/start` | POST | Start headroom proxy |
| `/api/headroom/stop` | POST | Stop headroom proxy |
| `/api/headroom/status` | GET | Headroom status |

### Tunnel (Public Exposure)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tunnel/enable` | POST | Enable Cloudflare Tunnel |
| `/api/tunnel/disable` | POST | Disable Cloudflare Tunnel |
| `/api/tunnel/status` | GET | Tunnel status |
| `/api/tunnel/tailscale-check` | GET | Check Tailscale availability |
| `/api/tunnel/tailscale-enable` | POST | Enable Tailscale Funnel |
| `/api/tunnel/tailscale-disable` | POST | Disable Tailscale Funnel |
| `/api/tunnel/tailscale-install` | POST | Install Tailscale |

### Proxy Pools

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/proxy-pools` | GET, POST | List/create proxy pools |
| `/api/proxy-pools/[id]` | GET, PATCH, DELETE | CRUD pool |
| `/api/proxy-pools/cloudflare-deploy` | POST | Deploy to Cloudflare Workers |
| `/api/proxy-pools/deno-deploy` | POST | Deploy to Deno Deploy |
| `/api/proxy-pools/vercel-deploy` | POST | Deploy to Vercel |

### Settings

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/settings` | GET, PATCH | Get/update global settings |
| `/api/settings/database` | GET, POST, DELETE | Database export/import/backup |
| `/api/settings/proxy-test` | POST | Test outbound proxy |

### CLI Tool Config Generators

| Endpoint | Description |
|----------|-------------|
| `/api/cli-tools/all-statuses` | All CLI tool status |
| `/api/cli-tools/claude-settings` | Claude Code settings |
| `/api/cli-tools/codex-settings` | Codex CLI config |
| `/api/cli-tools/copilot-settings` | GitHub Copilot settings |
| `/api/cli-tools/opencode-settings` | OpenCode config |
| `/api/cli-tools/cowork-settings` | CoWork config |

### System

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/version` | GET | Version + latest from npm |
| `/api/version/update` | POST | Trigger app update |
| `/api/shutdown` | POST | Shutdown server (dev) |
| `/api/init` | GET | Initialization probe |
| `/api/tags` | GET | Ollama-compatible model tags |

### OAuth Flows

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/oauth/[provider]/authorize` | GET | Start OAuth flow |
| `/api/oauth/[provider]/exchange` | POST | Exchange auth code |
| `/api/oauth/[provider]/device-code` | POST | Request device code |
| `/api/oauth/[provider]/poll` | POST | Poll for token |
| `/api/oauth/codex/*` | GET/POST | Codex-specific OAuth |
| `/api/oauth/cursor/*` | GET/POST | Cursor token import |
| `/api/oauth/gitlab/*` | GET/POST | GitLab OAuth |

### Translator

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/translator/translate` | POST | Translate text |
| `/api/translator/load` | GET | Load translation data |
| `/api/translator/save` | POST | Save translation data |

---

## 2. Providers (95+)

### Chat / LLM Providers

| Provider ID | Auth | Category | Models |
|-------------|------|----------|--------|
| `anthropic` | API Key | apikey | Claude models |
| `openai` | API Key | apikey | GPT / o1 / o3 |
| `gemini` | API Key | apikey | Google AI Studio |
| `gemini-cli` | OAuth | oauth | Google Gemini CLI |
| `claude` | OAuth | oauth | Claude.ai browser |
| `codex` | OAuth | oauth | OpenAI Codex (ChatGPT) |
| `deepseek` | API Key | apikey | DeepSeek |
| `mistral` | API Key | apikey | Mistral AI |
| `cohere` | API Key | apikey | Cohere |
| `groq` | API Key | apikey | Groq |
| `qwen` | Device Code | oauth | Alibaba Qwen |
| `xai` | OAuth PKCE | oauth | xAI (Grok API) |
| `azure` | API Key | apikey | Azure OpenAI |
| `vertex` | Service Account | apikey | Google Vertex AI |
| `openrouter` | API Key | apikey | OpenRouter |
| `together` | API Key | apikey | Together AI |
| `fireworks` | API Key | apikey | Fireworks AI |
| `nvidia` | API Key | apikey | NVIDIA NIM |
| `huggingface` | API Key | apikey | Hugging Face |
| `siliconflow` | API Key | apikey | SiliconFlow |
| `cerebras` | API Key | apikey | Cerebras |
| `github` | Device Code | oauth | GitHub Copilot |
| `kiro` | AWS SSO OIDC | oauth | AWS Kiro IDE |
| `cursor` | Import Token | import | Cursor IDE |
| `antigravity` | OAuth | oauth | Google Antigravity |
| `kimi-coding` | Device Code | oauth | Moonshot Kimi |
| `kimi` | API Key | apikey | Moonshot Kimi API |
| `kilocode` | Device Code | oauth | KiloCode |
| `cline` | OAuth | oauth | Cline extension |
| `gitlab` | OAuth PKCE | oauth | GitLab Duo |
| `glm` | API Key | apikey | Zhipu GLM |
| `minimax` | API Key | apikey | MiniMax |
| `xiaomi-mimo` | API Key | apikey | Xiaomi MiMo |
| `cloudflare-ai` | API Key | apikey | Cloudflare AI |
| `vercel-ai-gateway` | API Key | apikey | Vercel AI Gateway |

### Free Providers (No Auth Required)

| Provider ID | Description |
|-------------|-------------|
| `ollama` | Ollama Cloud |
| `ollama-local` | Local Ollama |
| `opencode` / `opencode-go` | OpenCode |
| `mimo-free` / `mmf` | Xiaomi MiMo Free |
| `openclaw` | OpenClaw |
| `local-device` | Local Device |
| `xiaomi-tokenplan` | Xiaomi TokenPlan (free tier) |

### Media Providers

| Provider ID | Kind | Description |
|-------------|------|-------------|
| `elevenlabs` | TTS | ElevenLabs text-to-speech |
| `deepgram` | STT | Deepgram speech-to-text |
| `assemblyai` | STT | AssemblyAI speech-to-text |
| `playht` | TTS | PlayHT text-to-speech |
| `cartesia` | TTS | Cartesia text-to-speech |
| `edge-tts` | TTS | Edge TTS (free) |
| `google-tts` | TTS | Google TTS |
| `aws-polly` | TTS | AWS Polly TTS |
| `stability-ai` | Image | Stability AI image generation |
| `fal-ai` | Image/Video/Music | fal.ai media generation |
| `black-forest-labs` | Image | BFL / Flux |
| `recraft` | Image | Recraft |
| `runwayml` | Video | RunwayML |
| `comfyui` | Image | ComfyUI (local) |
| `sdwebui` | Image | Stable Diffusion WebUI |

### Search Providers

| Provider ID | Description |
|-------------|-------------|
| `brave-search` | Brave Search |
| `serper` | Serper |
| `searchapi` | SearchAPI |
| `searxng` | SearXNG (free) |
| `tavily` | Tavily |
| `exa` | Exa neural search |
| `linkup` | LinkUp |
| `youcom` | You.com |
| `google-pse` | Google PSE |

### Web / Utility Providers

| Provider ID | Description |
|-------------|-------------|
| `grok-web` | xAI Grok web (cookie) |
| `perplexity-web` | Perplexity web (cookie) |
| `firecrawl` | Firecrawl web scraping |
| `jina-ai` | Jina AI |
| `jina-reader` | Jina Reader |
| `voyage-ai` | Voyage AI embeddings |

---

## 3. Combo & Strategy System

### Combo Kinds

| Kind | Behavior |
|------|----------|
| Default (null) | **Fallback** — tries models in order, falls to next on error |
| `fusion` | **Fusion** — fans out to all models in parallel, judge synthesizes one answer |

### Strategies

| Strategy | Description |
|----------|-------------|
| `fallback` | Sequential try-next on failure |
| `round-robin` | Rotate models across requests |

### Strategy Config

| Setting | Description |
|---------|-------------|
| `comboStrategy` | `"fallback"` or `"round-robin"` |
| `comboStickyRoundRobinLimit` | Requests per model before rotating |
| `comboStrategies` | Per-combo strategy overrides |

### Fusion Tuning

| Parameter | Default | Description |
|-----------|---------|-------------|
| `minPanel` | 2 | Minimum responses before quorum |
| `stragglerGraceMs` | 8000 | Wait for laggards after quorum |
| `panelHardTimeoutMs` | 90000 | Absolute timeout |
| `judgeModel` | panel[0] | Model used for synthesis |

### Capability-Auto-Switch

When request contains images/PDFs, combo models auto-reorder:
- **Tier 0:** Satisfies all capabilities
- **Tier 1:** Hard capabilities only
- **Tier 2:** Doesn't satisfy hard capabilities

---

## 4. Executors (21)

| Executor | Provider | Protocol |
|----------|----------|----------|
| `AntigravityExecutor` | antigravity | Cloud Code protobuf |
| `AzureExecutor` | azure | Azure OpenAI |
| `GeminiCLIExecutor` | gemini-cli | Gemini CLI SSE |
| `GithubExecutor` | github | GitHub Copilot SSE |
| `IFlowExecutor` | iflow | Tencent iFlow |
| `QoderExecutor` | qoder | Qoder NDJSON |
| `KiroExecutor` | kiro | AWS Kiro EventStream |
| `CodexExecutor` | codex | OpenAI Codex Responses |
| `CursorExecutor` | cursor | Cursor protobuf |
| `VertexExecutor` | vertex | Google Vertex AI |
| `QwenExecutor` | qwen | Alibaba Qwen |
| `OpenCodeExecutor` | opencode | OpenCode |
| `GrokWebExecutor` | grok-web | xAI Grok web |
| `PerplexityWebExecutor` | perplexity-web | Perplexity web |
| `OllamaLocalExecutor` | ollama-local | Local Ollama |
| `CommandCodeExecutor` | commandcode | CommandCode NDJSON |
| `XiaomiTokenplanExecutor` | xiaomi-tokenplan | Xiaomi multi-region |
| `MimoFreeExecutor` | mimo-free, mmf | MiMo Free |
| `CodeBuddyExecutor` | codebuddy-cn | Tencent CodeBuddy |
| `DefaultExecutor` | all others | OpenAI-compatible REST |

---

## 5. Format Translation (22 routes)

### Source Formats Detected

| Format | Identifier |
|--------|-----------|
| OpenAI Chat Completions | `openai` |
| OpenAI Responses API | `openai-responses` |
| Claude Messages API | `claude` |
| Gemini API | `gemini` |
| Antigravity | `antigravity` |
| Kiro | `kiro` |
| Cursor | `cursor` |
| Ollama | `ollama` |
| CommandCode | `commandcode` |
| Vertex AI | `vertex` |

### Translation Routes

| From | To | File |
|------|----|------|
| claude | openai | `openai` |
| openai | claude | `claude` |
| gemini | openai | `openai` |
| openai | gemini | `gemini` |
| openai | vertex | `vertex` |
| antigravity | openai | `openai` |
| openai | kiro | `kiro` |
| openai | cursor | `cursor` |
| openai | ollama | `ollama` |
| openai | commandcode | `commandcode` |
| kiro | claude | `claude` (direct) |

---

## 6. MITM Proxy (IDE Interception)

### Supported IDEs

| IDE | Intercepted Host |
|-----|------------------|
| Antigravity | `daily-cloudcode-pa.googleapis.com` |
| GitHub Copilot | `api.individual.githubcopilot.com` |
| Kiro | `q.us-east-1.amazonaws.com` |
| Cursor | `api2.cursor.sh` |

### Configuration

| Feature | Description |
|---------|-------------|
| `mitmEnabled` | Global on/off |
| Model alias mapping | Per-IDE model remapping |
| `MODEL_NO_MAP` | Models that must never be remapped |
| Host entry management | Auto-edits hosts file |
| DNS spoofing | Local DNS resolution |

---

## 7. Headroom (Context Compression)

| Feature | Description |
|---------|-------------|
| Binary detection | `which headroom` via extended PATH |
| Python detection | 3.13 → 3.12 → 3.11 → 3.10 → python3 → python |
| Start proxy | `headroom proxy --port 8787` |
| Health check | `GET http://localhost:8787/health` |
| Compress | `POST /v1/compress` with model field |
| Fail-open | If down, requests pass unmodified |
| PID management | `{DATA_DIR}/headroom/proxy.pid` |
| Log | `{DATA_DIR}/headroom/proxy.log` |

---

## 8. RTK (Request Token Killer)

| Module | Description |
|--------|-------------|
| `rtk/caveman.js` | System prompt injection (caveman mode) |
| `rtk/headroom.js` | Headroom proxy integration |
| `rtk/systemInject.js` | System message injection |
| `rtk/ponytail.js` | Ponytail compression |
| `rtk/filters/` | Per-tool compressors |

---

## 9. Tunnel (Public Exposure)

### Cloudflare Tunnel
- Auto-download `cloudflared`
- PID management + health check
- Auto-reconnect on network change

### Tailscale Funnel
- Install Tailscale
- Login + daemon management
- Health check

---

## 10. Proxy Pools

| Type | Description |
|------|-------------|
| `http` | Standard HTTP/SOCKS proxy |
| `vercel` | Vercel edge proxy pool |
| `cloudflare` | Cloudflare Workers proxy |
| `deno` | Deno Deploy proxy |

---

## 11. OAuth System (17 providers)

| Provider | Flow | Notes |
|----------|------|-------|
| claude | PKCE | Claude.ai browser login |
| codex | PKCE | ChatGPT/Codex |
| xai | PKCE | xAI Grok |
| gemini-cli | auth_code | Google Gemini CLI |
| antigravity | auth_code | Google Antigravity |
| iflow | auth_code | Tencent iFlow |
| qoder | device_code | Qoder |
| qwen | device_code | Alibaba Qwen |
| github | device_code | GitHub Copilot |
| kiro | device_code (AWS SSO OIDC) | AWS Kiro |
| cursor | import_token | Cursor (SQLite import) |
| kimi-coding | device_code | Moonshot Kimi |
| kilocode | device_code | KiloCode |
| cline | auth_code | Cline extension |
| gitlab | PKCE | GitLab Duo |
| codebuddy-cn | device_code | Tencent CodeBuddy |

---

## 12. Dashboard Pages

| Path | Feature |
|------|---------|
| `/dashboard` | Main landing |
| `/dashboard/providers` | Provider connections |
| `/dashboard/combos` | Model combo editor |
| `/dashboard/proxy-pools` | Proxy pool management |
| `/dashboard/usage` | Usage charts, stats, logs |
| `/dashboard/quota` | Quota management |
| `/dashboard/endpoint` | Endpoint configuration |
| `/dashboard/cli-tools` | CLI tool settings generator |
| `/dashboard/console-log` | Live server console log |
| `/dashboard/profile` | User profile & settings |
| `/dashboard/media-providers` | Media provider config |
| `/dashboard/mitm` | MITM proxy config |
| `/dashboard/translator` | Translation management |
| `/dashboard/skills` | Skills/marketplace |
| `/dashboard/basic-chat` | Basic chat UI (testing) |

---

## 13. CLI Commands

### Flags

| Flag | Description |
|------|-------------|
| `-p, --port <port>` | Server port (default: 20128) |
| `-H, --host <host>` | Bind host (default: 0.0.0.0) |
| `-n, --no-browser` | Don't auto-open browser |
| `-l, --log` | Show server logs |
| `-t, --tray` | System tray mode |
| `--skip-update` | Skip auto-update check |

### TUI Menu

1. Update to latest
2. Web UI (opens dashboard)
3. Terminal UI (interactive management)
4. Hide to Tray (background)
5. Exit

---

## 14. Settings

### Core

| Setting | Type | Description |
|---------|------|-------------|
| `requireLogin` | boolean | Require dashboard login |
| `password` | string | bcrypt-hashed password |
| `authMode` | string | `"password"`, `"oidc"`, or `"both"` |
| `comboStrategy` | string | `"fallback"` or `"round-robin"` |
| `outboundProxyEnabled` | boolean | Enable outbound proxy |
| `outboundProxyUrl` | string | HTTP/SOCKS proxy URL |
| `headroomEnabled` | boolean | Enable headroom compression |
| `headroomUrl` | string | Headroom proxy URL |
| `headroomCompressUserMessages` | boolean | Compress user messages |
| `mitmEnabled` | boolean | Enable MITM proxy |
| `cavemanEnabled` | boolean | Enable caveman mode |
| `requireApiKey` | boolean | Require API key auth |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `PORT` | Server port |
| `DATA_DIR` | Data directory path |
| `JWT_SECRET` | JWT signing secret |
| `INITIAL_PASSWORD` | Initial password |
| `ENABLE_REQUEST_LOGS` | Enable request logging |
| `ENABLE_TRANSLATOR` | Enable translator |
| `STREAM_STALL_TIMEOUT_MS` | Stall timeout (default: 360s) |
| `HTTP_PROXY` / `HTTPS_PROXY` | Outbound proxy |

---

## 15. Database

### Storage Files

| File | Content |
|------|---------|
| `{DATA_DIR}/db/data.sqlite` | Main state (settings, connections, combos, keys) |
| `{DATA_DIR}/jwt-secret` | JWT secret |
| `{DATA_DIR}/machine-id` | Machine ID |
| `{DATA_DIR}/auth/cli-secret` | CLI auth secret |
| `{DATA_DIR}/headroom/proxy.pid` | Headroom PID |
| `{DATA_DIR}/headroom/proxy.log` | Headroom log |
| `{DATA_DIR}/tunnel/*.pid` | Tunnel PIDs |

### DB Repositories

| Repo | Entity |
|------|--------|
| `settingsRepo` | Global settings |
| `connectionsRepo` | Provider connections |
| `nodesRepo` | Provider nodes |
| `combosRepo` | Model combos |
| `apiKeysRepo` | API keys |
| `aliasRepo` | Model aliases + MITM aliases |
| `pricingRepo` | Pricing overrides |
| `proxyPoolsRepo` | Proxy pools |
| `usageRepo` | Usage history, stats, logs |
| `disabledModelsRepo` | Disabled models |

---

## 16. Error Handling & Retry

| Error Type | Behavior |
|------------|----------|
| No credentials | 2-min cooldown |
| Rate limit | Exponential backoff (2s base, 5min max) |
| 401/402/403/404 | 2-min cooldown |
| 502 | 3 retries, 3s delay |
| 503 | 3 retries, 2s delay |
| 504 | 2 retries, 3s delay |
| 429 | No auto-retry (cooldown only) |

Account fallback: next account → next model in combo → track rateLimitedUntil.

---

*Generated: 2026-06-20 | 9Router v0.5.6*
