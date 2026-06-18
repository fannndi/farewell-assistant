---
description: Autostart — manage 9Router Windows auto-start via Scheduled Task
---

# Autostart

Manage Windows Scheduled Task yang start 9Router otomatis pas user logon.

## Usage

```
/autostart enable     Register scheduled task (AtLogon + restart-on-failure 3x)
/autostart disable    Unregister scheduled task
/autostart status     Show current state + 9Router health
/autostart run        Manually trigger the task (test the action)
```

## Cara Kerja

1. **Scheduled Task** `FarewellAssistant-9Router` dibuat di user context (no admin)
2. **Trigger**: `AtLogon` untuk user saat ini
3. **Action**: jalankan `scripts/common/start-9router-bg.ps1` via pwsh hidden
4. **Restart policy**: 3x retry dengan interval 5 menit kalau exit code non-zero
5. **Wrapper**: load config + api-key.txt, health-check, `Start-9Router` robust, log ke `.opencode/logs/autostart.log`

## File Terkait

| File | Fungsi |
|------|--------|
| `scripts/autostart.ps1` | CLI: enable/disable/status/run |
| `scripts/common/start-9router-bg.ps1` | Hidden wrapper untuk Task Scheduler |
| `scripts/common/helpers.ps1` `Start-9Router` | Robust start: PID file, log redirect, backoff |
| `.opencode/logs/autostart.log` | Log autostart runs |
| `.opencode/logs/9router.log` | 9Router stdout |
| `.opencode/logs/9router-error.log` | 9Router stderr |
| `.opencode/9router.pid` | PID tracking untuk precision kill |

## Troubleshooting

- **Task registered tapi 9Router not running**: `/autostart run` lalu cek `autostart.log`
- **Stale VBS di Startup folder**: auto-dihapus pas `enable`. Manual: hapus `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\9router.vbs`
- **Start lambat**: Next.js cold-start butuh ~20s untuk `/api/health` pertama (lazy route compile). Backoff sampai 45s.
- **Ganti Node path**: kalau upgrade Node, re-run `/autostart enable` (action path di-resolve saat register)

## Catatan

- Tidak start Ollama (biar terpisah, Ollama punya `.lnk` sendiri di Startup)
- No admin required (AtLogon user trigger)
- Untuk pre-logon (boot), butuh admin + `AtStartup` — belum didukung
