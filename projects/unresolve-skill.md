# Unresolved Gaps

> File: projects/unresolve-skill.md
> Updated: 2026-06-18
> Status: DEFERRED — not urgent, revisit after core gaps resolved

---

## Resolved

| # | Gap | Resolved In | Date |
|---|-----|-------------|------|
| G1 | Tidak ada PowerShell-specific skill | `projects/skills/powershell-patterns/SKILL.md` | 2026-06-17 |
| G2 | `self-heal.ps1` tidak auto-trigger | `scripts/hooks/hook-registry.json` (enabled: true) | 2026-06-17 |

---

## Gap 3 — Hooks Wiring (ECC → OpenCode)

**Deskripsi:** ECC memiliki 20+ hooks lifecycle yang didefinisikan di `ecc/hooks/hooks.json`. Tapi hooks ini dirancang untuk **Claude Code CLI**, bukan OpenCode. Format dan eksekusinya berbeda.

**Masalah:**
- OpenCode tidak memiliki native hook system seperti Claude Code
- Format hooks.json ECC tidak kompatibel dengan OpenCode
- Porting 20+ hooks akan memakan waktu dan rawan error

**Saran Saat Revisit:**
1. Baca ECC hooks.json → identifikasi hooks yang paling berguna
2. Buat adapter layer: JSON → OpenCode instruction
3. Prioritaskan hooks: post:quality-gate, session:start, stop:cost-tracker
4. Test dengan workload nyata

**Trigger revisit:** Saat migrasi infrastructure atau ada kebutuhan hook otomatis yang mendesak.

---

## Gap 6 — Local LLM Ops (Ollama Management)

**Deskripsi:** Tidak ada skill khusus untuk mengelola Ollama — local LLM engine yang jalan di GPU.

**Yang Hilang:**
- Start/stop Ollama secara otomatis
- Model switching (qwen2.5:1.5b → model lain)
- VRAM monitoring + threshold alert
- Enrichment pipeline management
- Model health check

**Saran Saat Revisit:**
1. Bikin `ecc/skills/local-llm-ops/SKILL.md`
2. Isi: Ollama API wrapper patterns (`/api/tags`, `/api/chat`, `/api/show`)
3. Tambah: GPU monitoring + auto start/stop
4. Integrasi: enrichment pipeline di `llm-adapter.ps1`

**Trigger revisit:** Saat mode `on` dipakai rutin dan perlu enrichment yang stabil.

---

## Gap 7 — 9Router Ops (AI Gateway Management)

**Deskripsi:** Tidak ada skill untuk mengelola 9Router — AI gateway proxy di `localhost:20128`.

**Yang Hilang:**
- Health check endpoint (`/health`)
- Model registry management
- API key rotation automation
- Routing rules management
- Load balancing / failover

**Saran Saat Revisit:**
1. Bikin `ecc/skills/ninerouter-ops/SKILL.md`
2. Isi: 9Router REST API patterns, health check, model listing
3. Tambah: auto-restart, log monitoring
4. Integrasi: dengan `detect-project.ps1` untuk gateway health validation

**Trigger revisit:** Saat production deployment service-hub atau saat 9Router sering down secara tidak terduga.

---

## Ringkasan

| Gap | Skill | Status | Trigger |
|-----|-------|--------|---------|
| G1 | powershell-patterns | RESOLVED | — |
| G2 | self-heal trigger | RESOLVED | — |
| G3 | hooks-wiring | DEFERRED | Infrastructure upgrade |
| G6 | local-llm-ops | DEFERRED | Mode ON dipakai rutin |
| G7 | ninerouter-ops | DEFERRED | Production deployment |
