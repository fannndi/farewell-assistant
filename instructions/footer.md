# Footer Format

Setelah setiap respons (kecuali Session Init), append 1 baris:

```
Session: farewell-assistant | Kategori: AUTOMATION | Mode: eco | GPU: off | Work: BUILD
```

## Dynamic Rendering

Footer **harus** di-render secara dinamis berdasarkan registry + mode state:

1. Baca `projects/registry.json` → ambil field `active`
2. Baca `projects/<active>/kategori` → ambil semua unique values
3. Sorted by importance: `WEB > MOBILE > AI_ML > DATA > INFRA > AUTOMATION`
4. Baca `.opencode/llm-mode.json` → ambil field `mode`
5. Infer GPU: mode == "on" → `GPU: on`, mode == "eco" → `GPU: off`
6. Baca `.opencode/work-mode.json` → ambil field `mode`
7. Render: `Session: <active> | Kategori: <sorted kategori> | Mode: <mode> | GPU: <gpu> | Work: <work mode>`

## Fields

| Field | Sumber | Contoh |
|-------|--------|--------|
| Session | Nama project aktif dari registry | `farewell-assistant` |
| Kategori | registry → active → kategori (unique, sorted) | `AUTOMATION` |
| Mode | .opencode/llm-mode.json → mode | `eco` / `on` |
| GPU | Dari mode (eco=off, on=on) | `off` / `on` |
| Work | .opencode/work-mode.json → mode | `PLAN` / `BUILD` |

## Behavioral Impact

Footer ini bukan sekadar display — mempengaruhi behavior AI:

| Mode | GPU | Work | AI Behavior |
|------|-----|------|-------------|
| eco | off | BUILD | Self-reliant, respon ringkas, skip enrichment |
| eco | off | PLAN | Read-only, audit/research, jangan edit file |
| on | on | BUILD | Local LLM available, boleh enrichment |
| on | on | PLAN | Read-only + enrichment untuk analisa |

Footer bersifat informatif, sekaligus behavioral switch.
