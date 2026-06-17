# Changelog

Semua perubahan penting di farewell-assistant.

---

## [1.0.0] — 2026-06-17 — Initial Release

### Architecture
- Built from scratch on OpenCode + 9Router + ECC
- 3-step pipeline: Project Detect → Enrich → Execute
- Multi-project support via registry + context files
- Smart enrichment: auto-skip untuk input sederhana

### Scripts (7)
- **setup.ps1** — First install: clone ECC, 9Router, apply profile
- **start.ps1** — Daily startup: health check, apply profile
- **llm-adapter.ps1** — Ollama API wrapper + smart enrichment
- **llm-mode.ps1** — Mode switch: eco / on / status
- **admin.ps1** — Maintenance: pull repos, doctor check
- **detect-project.ps1** — Auto-detect project type (Flutter, Node, Go, PHP, Python, Rust, .NET, Ruby)
- **hooks/check-enrich.ps1** — Enrichment verification
- **hooks/self-heal.ps1** — Post-edit typecheck

### Profiles (2)
- **gratis** — Free models via 9Router
- **go** — Paid models via 9Router

### Instructions (3 files, ~800 tokens)
- **user-rules.md** — Core rules (presisi, max 2 tanya)
- **preprocess.md** — Enrichment pipeline (smart-skip)
- **footer.md** — Footer format (1 baris)

### Commands (14)
- Custom (5): setup, start-free, start-go, admin, go, llm, detect
- ECC (9): plan, tdd, code-review, security-scan, build-fix, verify, update-docs

### Agents (7)
- build, planner, code-reviewer, security-reviewer, tdd-guide, build-error-resolver, doc-updater

### Multi-Project
- `projects/registry.json` — project index
- `projects/context/<slug>.md` — per-project context files
- `detect-project.ps1` — auto-detect project type

### Design Principles
- Every file must justify its existence
- Token-efficient: ~800 tokens instruction (vs ~5000+ in old system)
- GPU-smart: enrichment only when it adds value
- Simple: 3-step pipeline (vs 8+ steps)
- Modular: each component independent
