# Simulasi Audit — service-hub (002)

> **Footer:** `Farewell: ON | Project: 002-service-hub | BUILD | Turn: 1 | Chain: 8 | 80% | Eco`
> **User:** bikin CRUD user dengan auth JWT
> **Role:** AI model auditing backend NestJS + Prisma + PostgreSQL

---

## Pipeline Route (Real)

```
Intent:       build
Domain:       web
Complexity:   medium
Confidence:   80%
Source:       quick
Model:        Free=Free / Emergency=Free
Planning:     False
Skill Chain (8 steps):
  1. orch-add-feature    — Orchestrate end-to-end feature build
  2. api-design          — Design REST endpoints + schemas
  3. backend-patterns    — Service layer + repository patterns
  4. database-migrations — Schema creation + migrations
  5. tdd-workflow        — Write tests before implementation
  6. security-review     — Auth + input validation
  7. verification-loop   — Verify all passes green
  8. git-workflow        — Commit the feature
```

---

## Skenario 1: Backend Auth — CRUD User

**Input AI:** `"bikin CRUD user dengan auth JWT"`

### Real Pipeline Output
| Field | Value |
|-------|-------|
| Footer | Farewell: ON | Project: 002-service-hub | BUILD | Turn: 1 | Chain: 8 | 80% | Eco |
| Intent | build |
| Domain | web |
| Chain | build_web (8 steps) |
| Planning | no (medium complexity) |

### AI Model Perspective
Sebagai AI model, saya harus:

1. **Check existing auth** — `backend/` ada Passport JWT? Cek `package.json` + `auth module`
2. **Prisma schema** — cek `schema.prisma` untuk User model, tambah field jika perlu
3. **NestJS module pattern** — buat `users.controller.ts`, `users.service.ts`, `users.module.ts`
4. **Prisma migration** — jangan `prisma migrate dev` di CI, pakai `prisma migrate deploy`
5. **JWT guard** — reuse existing `@UseGuards(JwtAuthGuard)` pattern
6. **DTO validation** — pakai `class-validator` + `class-transformer` (NestJS native)
7. **Test** — e2e test dengan `@nestjs/testing` + `supertest`

### Checklist Item Spesifik

| # | Item | Cek | Severity |
|---|------|-----|----------|
| SH-1 | Prisma schema: User model | Ada relasi ke model lain? | HIGH |
| SH-2 | JWT guard reusable | `common/guards/jwt-auth.guard.ts` exist? | HIGH |
| SH-3 | Password hashing | bcrypt dengan salt rounds >= 10? | CRITICAL |
| SH-4 | Rate limiting | `@nestjs/throttler` terkonfigurasi? | MEDIUM |
| SH-5 | Prisma migration safety | `prisma migrate deploy` (bukan `dev`) di CI | HIGH |
| SH-6 | Docker compose app | service-hub di `docker-compose.yml`? | MEDIUM |
| SH-7 | Supabase fallback | `supabase/config.toml` — semua disabled | LOW |
| SH-8 | env template | `.env.example` sinkron dengan `.env`? | LOW |

### Simulasi Skill Chain Execution

```
Step 1/8: orch-add-feature
  → Research: NestJS version, Prisma version, existing auth patterns
  → Plan: users module, dto, prisma schema, migration, controller, service, guard
  → Gate: human review plan

Step 2/8: api-design
  → POST /api/users (register) — public
  → GET /api/users — JWT required, admin only
  → GET /api/users/:id — JWT required
  → PATCH /api/users/:id — JWT required, owner
  → DELETE /api/users/:id — JWT required, admin only

Step 3/8: backend-patterns
  → Service layer: UserService extends PrismaService
  → Repository: Prisma UserDelegate (NestJS PrismaModule)

Step 4/8: database-migrations
  → `npx prisma migrate dev --name add-users`
  → Verify migration SQL in `prisma/migrations/`
  → `npx prisma migrate deploy` untuk CI

Step 5/8: tdd-workflow
  → Unit test: UserService + hashing
  → E2E: POST /api/users → 201, GET /api/users → 401 tanpa JWT

Step 6/8: security-review
  → Input validation: email format, password strength
  → No plaintext password in response
  → JWT expiresIn, refresh token strategy

Step 7/8: verification-loop
  → `npm run lint && npm run test && npm run build`

Step 8/8: git-workflow
  → Commit: feat: add user CRUD with JWT auth
```

---

## Skenario 2: Review Security — Docker Config

**Input AI:** `"review security on docker config"`

### Real Pipeline Output
| Field | Value |
|-------|-------|
| Footer | Farewell: ON | Project: 002-service-hub | PLAN | Turn: 5 | Chain: 3 | 70% | Eco |
| Intent | review |
| Domain | infra |
| Chain | review (3 steps) |
| Planning | no |

### AI Model Perspective
Docker config audit checklist:

| # | Item | Status | Severity |
|---|------|--------|----------|
| SH-9 | `docker-compose.yml` — no `privileged: true` | ? | CRITICAL |
| SH-10 | PostgreSQL — env `POSTGRES_PASSWORD` from file | ? | MEDIUM |
| SH-11 | Redis — `--requirepass` di command | ? | MEDIUM |
| SH-12 | Healthcheck di semua service | ? | HIGH |
| SH-13 | No `:latest` tag — semua pinned version | ? | HIGH |
| SH-14 | Network mode — `internal` for DB service | ? | LOW |
| SH-15 | Volume permission — no 777 | ? | MEDIUM |

---

## Skenario 3: Database Migration — Schema Change

**Input AI:** `"change user model: add profile image field"`

### Pipeline Prediction
| Intent | Domain | Chain |
|--------|--------|-------|
| build | data | build_data (6 steps) |

### Checklist
| # | Item | Cek |
|---|------|-----|
| SH-16 | Migration reversible? | Ada `down`? |
| SH-17 | Nullable or default? | Backward compat? |
| SH-18 | S3 or local storage? | Service already has S3 config? |

---

## Temuan Potensial

| Temuan | Severity | Rekomendasi |
|--------|----------|-------------|
| Supabase disabled tapi masih ada config | LOW | Hapus `supabase/` atau clean up |
| No `.opencode/context.md` di project | MEDIUM | Junction `service-hub/.opencode/` → `farewell-assistant/.opencode/` |
| Docker compose healthcheck? | HIGH | Cek tiap service punya `healthcheck` |
| Prisma migration strategy? | HIGH | Pastikan CI pakai `migrate deploy` bukan `migrate dev` |
| Redis password di compose? | MEDIUM | Pindah ke `.env` |

---

*Simulasi: 2026-06-22 | farewell-assistant v1.5.0 | Route: build_web*
