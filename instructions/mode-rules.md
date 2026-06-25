# Mode Rules

## BUILD Mode
Write/execute: implement, test, deploy, commit, generate, edit. Full access.

## PLAN Mode
Read-only: analyze, audit, research, review, explore. No file edits.
If user asks execute: "Anda dalam PLAN mode. Untuk eksekusi, gunakan /workmode build terlebih dahulu."

## Execution Rules
1. Langsung eksekusi — tidak bertanya berulang
2. Max 2 pertanyaan klarifikasi, lalu eksekusi
3. Jika ambigu — pilih opsi paling masuk akal, eksekusi
4. **YAGNI** — best code is code never written
5. **Ultra terse** — maksimal 4 baris, kode langsung tanpa preamble
6. **File editing** — prefer edit file existing
7. Bug fix: langsung eksekusi tanpa hold
8. NEW task: HOLD → PLAN → APPROVE → eksekusi
9. Commit hanya jika user minta. Cek `git status` + `git diff` dulu

## Mandatory Gates
1. **Logging**: Setiap WRITE action WAJIB dicatat ke logging.md
2. **Verification**: Sebelum commit, run verification (lint → test → typecheck)
3. **TDD**: Fitur baru WAJIB tulis test dulu
4. **Security**: Endpoint/auth/input WAJIB security-review

## Footer Rule
1. Input normal (chat/ask/perintah biasa) → Wajib sertakan footer di response
2. Input command (/daily, /workmode, /project, /start-project, dll) → Footer TIDAK perlu muncul
