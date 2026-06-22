# Execution Rules — Precision Input

## Aturan Presisi
1. **Langsung eksekusi** — tidak bertanya berulang
2. **Max 2 pertanyaan** klarifikasi, lalu eksekusi
3. **Jika ambigu** — pilih opsi paling masuk akal, eksekusi. User koreksi kalau salah
4. **YAGNI** — best code is code never written. Jangan buat yang tidak diminta
5. **Ultra terse** — jawaban maksimal 4 baris. Kode langsung tanpa preamble
6. **File editing** — prefer edit file existing. Jangan buat file baru jika tidak perlu
7. **Testing sebelum commit** — verifikasi dulu

## Bug Fix
Langsung eksekusi tanpa hold.

## NEW Task
HOLD → PLAN (ke user) → APPROVE → eksekusi.

## Commit Rules
- Hanya commit jika user minta
- Cek `git status` + `git diff` dulu
- Jangan commit secrets/api keys
