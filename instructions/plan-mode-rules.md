# Plan Mode Rules

> WORK MODE: PLAN | Tools: READ only | Write/Edit: BLOCKED

## Behavior

Read-only: analyze, audit, research, review, explore. Tidak boleh mengubah file apapun.

## Enforcement

### Allowed Skills (169)
Semua skill di `skill-mode-index.json.plan` section. Contoh:
- audit: `repo-scan`, `workspace-surface-audit`, `codehealth-mcp`, `production-audit`
- research: `research-ops`, `deep-research`, `documentation-lookup`, `exa-search`
- planning: `blueprint`, `product-capability`, `intent-driven-development`, `plan-orchestrate`
- review: `coding-standards`, `security-review`, `error-handling`
- reference: semua `*-patterns`, `*-testing`, `*-verification`, framework docs
- security: `safety-guard`, `gateguard`, compliance checkers
- explore: `codebase-onboarding`, `code-tour`, `iterative-retrieval`
- business: all domain expertise skills
- healthcare: all healthcare patterns

### Blocked Skills (79)
Semua skill di `skill-mode-index.json.build` section:
- orch-* (orchestration)
- tdd-workflow, e2e-testing, cpp-testing
- semua `*-patterns` yang butuh implementasi
- semua content creation, media generation, deployment
- semua agent engineering skills
- semua infra config skills

### HYBRID Skills (19)
Skill di `skill-mode-index.json.hybrid` section:
- **PLAN mode:** hanya boleh sub-usage analisis/rekomendasi
- **BUILD mode:** full execution

Contoh HYBRID di PLAN:
- `seo` → boleh audit SEO, TIDAK BOLEH implementasi
- `email-ops` → boleh triage/draft, TIDAK BOLEH send
- `knowledge-ops` → boleh search/retrieve, TIDAK BOLEH ingest/sync
- `mle-workflow` → boleh review pipeline, TIDAK BOLEH build/deploy
- `terminal-ops` → boleh analisis output, TIDAK BOLEH execute commands

## Refusal Pattern

```
User: /go bikin CRUD user
AI:   "Anda dalam PLAN mode. Untuk eksekusi, gunakan /workmode build terlebih dahulu."
```

```
User: (minta deploy)
AI:   "Deploy membutuhkan BUILD mode. Gunakan /workmode build untuk melanjutkan."
```

```
User: (skill WRITE di PLAN mode)
AI:   "[skill-name] membutuhkan WRITE access. Mode: PLAN | Ganti: /workmode build"
```

## Output Format

Output di PLAN mode:
- **Analisis** — temuan, findings, rekomendasi
- **Rekomendasi** — saran langkah berikutnya (tanpa eksekusi)
- **Ringkasan** — summary hasil riset/audit

Output TIDAK BOLEH:
- File baru
- Edit file yang ada
- Script execution yang mengubah state
- Commit/push
- Install/uninstall packages

## Exception: Safe Bash Commands

Beberapa bash commands aman di PLAN mode:
- `git status`, `git log`, `git diff` (read-only)
- `py -m pytest tests/` (test only, no deploy)
- `ls`, `dir`, `find`, `grep`
- `cat`, `type` (read file)
- `python -c "import ...; print(...)"` (dry-run, no side effects)

Commands yang TIDAK aman:
- `pip install`, `npm install`
- `git add`, `git commit`, `git push`
- `docker run`, `docker-compose up`
- `python -m farewell_assistant start`
- Any write/edit operation
