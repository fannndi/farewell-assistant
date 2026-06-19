---
description: Training — self-improvement system for pipeline accuracy
---

# Training

Self-improvement mode — saya (AI Guru) melatih project ini (Siswa) menggunakan Ollama (Buku Latihan).

## Cara Kerja

1. **Generate** — LLM generate 200 test cases dari domain knowledge (mobile, flutter, kotlin, rust)
2. **Evaluate** — Pipeline di-run di setiap test case, score accuracy
3. **Auto-fix** — Kalau ada error, pipeline di-update otomatis
4. **Knowledge base** — Output ke `training/knowledge-base.md` (di-inject ke AI context)
5. **Report** — Accuracy metrics + error analysis

## Output Files

| File | Isi |
|------|-----|
| `training/knowledge-base.md` | Buku panduan kedua — di-inject ke instructions |
| `training/report.json` | Raw metrics |
| `training/fix-recommendations.json` | Auto-fix suggestions |
| `training/cases.json` | 200 test cases |

## Contoh

| Perintah | Yang Dilakukan |
|----------|----------------|
| `/training` | Generate + evaluate (200 cases) |
| `/training -AutoFix` | Generate + evaluate + auto-fix |
| `/training -Count 50` | Cepat (50 cases saja) |

## Task

$ARGUMENTS
