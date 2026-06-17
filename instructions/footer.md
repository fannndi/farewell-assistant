# Footer Format

Setelah setiap respons (kecuali Session Init), append 1 baris:

```
Profile: Gratis | Session: farewell-assistant | Kategori: AUTOMATION
```

## Dynamic Rendering

Footer **harus** di-render secara dinamis berdasarkan registry:

1. Baca `projects/registry.json` → ambil field `active`
2. Baca `projects/<active>/kategori` → ambil semua unique values
3. Sorted by importance: `WEB > MOBILE > AI_ML > DATA > INFRA > AUTOMATION`
4. Join dengan ` - `
5. Hanya tampilkan kategori yang BENAR-BENAR ADA di project aktif

## Contoh Output

| Project | Kategori |
|---------|----------|
| farewell-assistant | `AUTOMATION` |
| service-hub | `AUTOMATION - DATA - INFRA - MOBILE - WEB` |
| my-webapp | `WEB` |

## Fields

| Field | Sumber | Contoh |
|-------|--------|--------|
| Profile | Nama config (gratis/go) | `Gratis` |
| Session | Nama project aktif dari registry | `farewell-assistant` |
| Kategori | registry → active → kategori (unique, sorted) | `AUTOMATION` |

Footer bersifat informatif, bukan enforcement.
