---
description: Start — consolidated: bootstrap + update + health + config + autostart + launch
---

# Start

Single command untuk semua. Jalankan setiap kali buka laptop atau setelah clone repo.

## Flow (7 Steps)

| Step | Aksi | Detail |
|------|------|--------|
| 1/7 | **Git Pull Self** | `git pull --ff-only` farewell-assistant — sync perubahan dari device lain. Kalau start.ps1 berubah, tampilkan "run again for new version". |
| 2/7 | **Initial Bootstrap** | Guard: hanya jalan sekali setelah fresh clone. Clone ECC + 9Router, build, panduan dashboard, validate key+combo, init state. |
| 3/7 | **Update ECC + 9Router** | `git pull` ECC + 9Router → rebuild kalau update. Cek npm 9router version vs local. Scan changelog untuk breaking changes (prompt [Y/n]). |
| 4/7 | **9Router Health** | Health check → start kalau tidak running (backoff ~45s). |
| 5/7 | **Load Configuration** | Parse api-key.txt → env vars + extract combos. Diff combo definitions vs cached → tampilkan perubahan. Generate `opencode.jsonc`. |
| 6/7 | **Autostart** | Cek Scheduled Task → register kalau belum. Hapus stale VBS. Silent. |
| 7/7 | **Launch** | Synch session state + task log → `opencode` |

## Cara Pakai

```powershell
.\start.ps1
```

Atau di dalam opencode: `/start`

Script aman dijalankan berkali-kali — guard skip langkah yang sudah selesai.
