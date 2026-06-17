# Footer Format

Setelah setiap respons (kecuali Session Init), append 1 baris:

```
Session: farewell-assistant | Kategori: AUTOMATION | Mode: eco | GPU: off | Work: BUILD | Skills: ON - 23
```

## Dynamic Rendering

Footer **harus** di-render secara dinamis berdasarkan registry + mode state:

1. Baca `projects/registry.json` → ambil field `active`
2. Baca `projects/<active>/kategori` → ambil semua unique values
3. Sorted by importance: `WEB > MOBILE > AI_ML > DATA > INFRA > AUTOMATION`
4. Baca `.opencode/llm-mode.json` → ambil field `mode`
5. Infer GPU: mode == "on" → `GPU: on`, mode == "eco" → `GPU: off`
6. Baca `.opencode/work-mode.json` → ambil field `mode`
7. Baca `projects/skill-mode-index.json` → hitung total skill sesuai work mode
8. Render: `Session: <active> | Kategori: <sorted kategori> | Mode: <mode> | GPU: <gpu> | Work: <work mode> | Skills: ON - <count>`

## Fields

| Field | Sumber | Contoh |
|-------|--------|--------|
| Session | Nama project aktif dari registry | `farewell-assistant` |
| Kategori | registry → active → kategori (unique, sorted) | `AUTOMATION` |
| Mode | .opencode/llm-mode.json → mode | `eco` / `on` |
| GPU | Dari mode (eco=off, on=on) | `off` / `on` |
| Work | .opencode/work-mode.json → mode | `PLAN` / `BUILD` |
| Skills | skill-mode-index.json → total skills | `ON - 23` / `OFF - 0` |

## Skills Count Logic

```
Baca skill-mode-index.json → ambil skills[work_mode]
Hitung total = sum semua skill di semua group
Status = ON jika count > 0, OFF jika count = 0
```

| Work Mode | Group Breakdown | Total |
|-----------|----------------|-------|
| BUILD | orch(6) + tdd(3) + code(4) + sec(3) + deploy(4) + agent(3) | 23 |
| PLAN | audit(6) + research(6) + explore(4) + planning(4) | 20 |
| Error | file not found | 0 → OFF |

## Behavioral Impact

Footer ini bukan sekadar display — mempengaruhi behavior AI:

| Mode | GPU | Work | Skills | AI Behavior |
|------|-----|------|--------|-------------|
| eco | off | BUILD | ON - 23 | Self-reliant, 23 skill aktif, execute mode |
| eco | off | PLAN | ON - 20 | Read-only, 20 skill aktif, audit mode |
| on | on | BUILD | ON - 23 | Local LLM + 23 skill, full power |
| on | on | PLAN | ON - 20 | Local LLM + 20 skill, analyze mode |

Footer bersifat informatif, sekaligus behavioral switch.
