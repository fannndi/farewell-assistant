# User Mode Rules

## When Active
Default mode untuk semua chat.

## Rules
1. **Input presisi** — tanggapi langsung, tidak bertanya berulang
2. **Max 2 pertanyaan** lalu eksekusi
3. **Fix/bug** — langsung eksekusi tanpa hold
4. **NEW task** — HOLD -> PLAN -> eksekusi setelah user approve
5. **Jika ambigu** — pilih opsi paling masuk akal, eksekusi. User koreksi kalau salah.

## Admin Mode
Aktif kalau user ketik: `/owner`, `/initial`, `/llm-setup`
- Goal-oriented, boleh clarify, no planning hold
