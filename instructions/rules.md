# Footer (cek state di context.md — binding setiap turn)
Parameter dari footer dan implikasinya:
- **Project**: {code}-{name} — semua context/memory/skill untuk project ini
- **Mode**: BUILD=full write, PLAN=read-only. Tool permission mengikuti mode
- **Session**: #{N} — N = sesi ke berapa. Memory dari sesi sebelumnya tersedia
- **Team**: ON=reasoning untuk task berat, OFF=direct execution untuk task ringan. Kalau ragu ON
- **Skills**: {N} — jumlah skill terindex. Skill priority mengikuti daftar di bawah

# Execution
- YAGNI: best code is code never written
- Ultra terse: max 4 baris, kode langsung tanpa preamble
- Bug fix: langsung eksekusi tanpa hold
- NEW task: HOLD → PLAN → APPROVE → eksekusi
- Commit: hanya jika user minta. Cek git status + diff dulu

# Model Priority (Hemat Token)
1. **Free combo** — paling hemat. Prioritas utama.
2. **Deepseek-GO-Flash** — fallback kalau Free lambat/error/limit.
3. **Ping test**: sebelum pake Flash, cek dulu respon Free. Kalau Free responsif, pakai Free. Kalau timeout/error, pake Flash.
4. **Token conscious**: kalau task sederhana (1-2 edit, typo, explore) → pilih model termurah yang available. Task berat (arsitektur, security review) → baru pake Flash.

# Gates
- Logging: catat WRITE action ke logging.md [timestamp] STAGE | ACTION | RESULT | FILES
- Verification: sebelum commit → lint → test → typecheck
- Security: endpoint/auth/input wajib review
- TDD: fitur baru wajib tulis test dulu

# Skill Priority
Prioritas web: react, nextjs, vue, angular, django, fastapi, express, nestjs, css, html
Prioritas mobile: flutter, dart, kotlin, swift, compose, react-native, android
Skill lain tetap tersedia. Prioritaskan yang di atas untuk project terkait.

# Admin
/owner, /initial, /llm-setup → goal-oriented, no planning hold
