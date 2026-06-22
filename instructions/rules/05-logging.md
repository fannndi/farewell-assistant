# Logging Rules

## Setiap Stage WAJIB Log
Format:
```
[timestamp] STAGE: <stage> | ACTION: <action> | RESULT: <ok/fail> | FILES: <files>
```

## Stage yang Wajib di-Log
| Stage | Saat | Contoh |
|-------|------|--------|
| ENRICH | Enrichment selesai | Intent: build, domain: web, confidence: 0.85 |
| RULE_CHECK | Mode check | Mode: BUILD, allowed: true |
| MODEL_SELECT | Model routing | Complexity: low → combo: Free |
| EXECUTE | Eksekusi selesai | Files: src/main.py, tests/test_main.py |
| COMMIT | Commit | Hash: abc123, files: 3 |

## File Log
- **logging.md** — semua task log (gitignored)
- **session-log.md** — session harian
