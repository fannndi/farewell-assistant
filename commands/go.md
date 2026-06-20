---
description: Universal task — goal-based execution
---

# Go

## Cara Pakai

Kirim task langsung sebagai argumen:

```
/go "bikin CRUD user dengan auth JWT dan FastAPI"
```

## Behavior

1. Input di-route ke intent router untuk klasifikasi
2. Rule check — PLAN mode akan block build/fix/deploy
3. Skill chain ditentukan berdasarkan intent + domain
4. AI execute dengan model route yang sesuai

## Contoh

| Perintah | Yang Dilakukan |
|----------|----------------|
| `/go fix bug auth token` | Fix intent → search-first → fix → verify |
| `/go bikin landing page` | Build intent → api-design → tdd → security |
| `/go deploy docker` | Deploy intent → audit → deploy → verify |
| `/go apa itu closure` | Ask intent → docs lookup |

## Task

$ARGUMENTS
