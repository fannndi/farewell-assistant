# Mode Enforcement — PLAN vs BUILD

## Aturan Utama
AI **TIDAK BOLEH auto-switch** work mode. Hanya user yang bisa via `/workmode`.

## PLAN Mode
- **Tools:** read, bash (read-only)
- **DILARANG:** write, edit, commit, push, install packages, `git add`
- Jika user minta eksekusi → **WAJIB tolak**:
  ```
  Anda dalam PLAN mode. Untuk eksekusi, gunakan /workmode build terlebih dahulu.
  ```

## BUILD Mode
- **Tools:** ALL (read, write, edit, bash)
- Full access: implementasi, test, deploy, commit

## Refusal Pattern (WAJIB)
Setiap kali user minta write/edit/commit di PLAN mode:
```
Anda dalam PLAN mode. Untuk eksekusi, gunakan /workmode build terlebih dahulu.
```

## Mode Mismatch Detection
| User Request | PLAN | BUILD |
|-------------|------|-------|
| /go bikin fitur | REFUSE | EKSEKUSI |
| /go review code | EKSEKUSI | EKSEKUSI |
| /go deploy | REFUSE | EKSEKUSI |
