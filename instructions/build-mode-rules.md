# Build Mode Rules

> WORK MODE: BUILD | Tools: ALL (read, write, edit, bash) | No block

## Behavior

Write/execute: implement, test, deploy, commit, generate, edit. Full access.

## Enforcement

### Open Access (271 skills)
ALL skills available — READ(169) + WRITE(79) + HYBRID(19):

| Category | Mode | Skills |
|----------|------|--------|
| orchestration | WRITE | orch-*, team-*, parallel-*, dmux-* |
| tdd_testing | WRITE | tdd-workflow, e2e-testing, cpp-testing, browser-qa |
| coding_write | WRITE | powershell-patterns, plankton, adr, hexagonal, motion |
| generate | WRITE | article-writing, content-engine, brand-*, video-*, media-* |
| agent_eng | WRITE | agent-harness-construction, agentic-os, gan-*, loop-* |
| infra | WRITE | homelab-*, dashboard-builder, flox, data-* |
| tools_config | WRITE | configure-ecc, hookify, customize-opencode |
| api_integration | WRITE | api-connector, x-api, nutrient, mcp-server |
| audit | READ | repo-scan, workspace-audit, codehealth-mcp |
| research | READ | research-ops, deep-research, documentation-lookup |
| planning | READ | blueprint, product-capability, intent-driven |
| review | READ | coding-standards, security-review, error-handling |
| reference | READ | semua *-patterns, *-testing, *-verification |
| explore | READ | codebase-onboarding, code-tour, inherit-legacy |

## Mandatory Gates

### 1. Logging Rule (`logging.md`)

Setiap WRITE action WAJIB dicatat:
```
[timestamp] STAGE: <stage> | ACTION: <action> | RESULT: <ok/fail> | FILES: <files>
```

### 2. Verification Loop

Sebelum commit, RUN verification:
```python
verification-loop (build → lint → test → typecheck)
```

### 3. TDD Gate

Setiap fitur baru WAJIB:
1. Tulis test dulu (failure)
2. Implementasi (pass)
3. Refactor (green)

### 4. Security Gate

Setiap endpoint/auth/input handling WAJIB:
```python
security-review → safety-guard
```

## HYBRID Skills in BUILD Mode

HYBRID skills di BUILD mode mendapat full execution access:

| Skill | PLAN (analyze only) | BUILD (full execution) |
|-------|---------------------|----------------------|
| `seo` | Audit SEO issues | Implement improvements, schema, sitemap |
| `email-ops` | Triage/draft | Send, manage mailbox |
| `knowledge-ops` | Search/retrieve | Ingest, sync, save |
| `mle-workflow` | Review pipeline | Build, deploy, monitor |
| `terminal-ops` | Analyze output | Execute commands, push fixes |
| `github-ops` | Read issues/PRs | Manage releases, CI/CD |
| `google-workspace-ops` | Find/summarize | Edit, create, migrate |
| `jira-integration` | Retrieve/analyze | Update status, add comments |
| `project-flow-ops` | Triage | Create tasks, link work |
| `design-system` | Audit consistency | Generate tokens, implement |
| `accessibility` | Audit WCAG | Implement ARIA/traits |
| `frontend-a11y` | Review a11y | Implement fixes |
| `agent-introspection-debugging` | Capture/diagnose | Execute recovery |
| `messages-ops` | Read/inspect | Send replies |
| `unified-notifications-ops` | Analyze routing | Configure dedup/escalation |
| `prompt-optimizer` | Analyze prompt | Generate optimized prompt |

## Recommended Flow

```
1. Planning (READ)  → blueprint, research, planning
2. TDD Gate (WRITE) → tdd-workflow, test dulu
3. Implement (WRITE) → orch-*, coding skills
4. Security (READ) → security-review
5. Verify (READ) → verification-loop
6. Commit (WRITE) → git-workflow
7. Deploy (build-only) → production-audit, deployment-patterns
```
