# Footer Format

Setelah setiap respons (kecuali Session Init), append 1 baris:

```
Profile: Gratis | Model: DeepSeek V4 Flash | Kategori: WEB - MOBILE - DATA - INFRA - AUTOMATION
```

## Fields

| Field | Sumber | Contoh |
|-------|--------|--------|
| Profile | Nama config (gratis/go) | `Gratis` |
| Model | Cloud model dari 9Router | `DeepSeek V4 Flash` |
| Kategori | projects/registry.json → active project → kategori values | `WEB - MOBILE - DATA - INFRA - AUTOMATION` |

## Kategori Format

Tampilkan semua kategori yang tersedia di project aktif, dipisahkan ` - `. Sorted by importance: WEB > MOBILE > AI_ML > DATA > INFRA > AUTOMATION.

Footer bersifat informatif, bukan enforcement.
