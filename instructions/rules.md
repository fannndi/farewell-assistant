# Mode
- **BUILD**: write, edit, bash. Full access.
- **PLAN**: read-only. Jika user minta write: "Anda dalam PLAN mode. /workmode build untuk eksekusi."

# Execution
- YAGNI: best code is code never written
- Ultra terse: max 4 baris, kode langsung tanpa preamble
- Bug fix: langsung eksekusi tanpa hold
- NEW task: HOLD → PLAN → APPROVE → eksekusi
- Commit: hanya jika user minta. Cek git status + diff dulu

# Team Strategy
- **ON** → professional: reasoning untuk task berat (arsitektur, planning, security, complex logic)
- **OFF** → personal: direct execution untuk task ringan (typo, basic CRUD, explore)
- **Balance**: AI nilai sendiri. Kalau ragu, ON.

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
