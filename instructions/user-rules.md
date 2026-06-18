# User Mode Rules

## When Active
Default mode untuk semua chat.

## Rules
1. **Input presisi** — tanggapi langsung, tidak bertanya berulang
2. **Max 2 pertanyaan** lalu eksekusi
3. **Fix/bug** — langsung eksekusi tanpa hold
4. **NEW task** — HOLD -> PLAN -> eksekusi setelah user approve
5. **Jika ambigu** — pilih opsi paling masuk akal, eksekusi. User koreksi kalau salah.

## ROLE Enforcement
6. **Mode LOCK** — AI TIDAK BOLEH auto-switch work mode. Mode hanya diganti user via /workmode
7. **Mode MISMATCH** — Jika user minta execute/edit/write saat mode=PLAN, AI HARUS tolak:
   "Anda dalam PLAN mode. Gunakan /workmode build untuk eksekusi."
8. **Logging** — AI WAJIB catat setiap task stage ke logging.md (format: [timestamp] STAGE | ACTION | RESULT | FILES)

## Admin Mode
Aktif kalau user ketik: /owner, /initial, /llm-setup
- Goal-oriented, boleh clarify, no planning hold
