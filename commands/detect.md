---
description: Detect — identify project type from directory markers
---

# Detect

Detect project type (Flutter/Node/Go/Rust/PHP/Python/.NET/Ruby/...) dari file markers di working directory atau path yang diberikan.

## Usage

```
/detect                              Detect di current working directory
/detect -Path "C:\my-project"        Detect di path tertentu
/detect -Path "..." -EmitContext     Detect + emit context template ke projects/context/<slug>.md
```

## Markers yang Dikenali

| Marker | Type |
|--------|------|
| `pubspec.yaml` | Flutter |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `composer.json` | PHP/Laravel (refine: Laravel/Symfony) |
| `Gemfile` | Ruby |
| `requirements.txt` / `pyproject.toml` / `Pipfile` | Python |
| `package.json` | Node (refine: Next/Nuxt/Vue/React/Express/NestJS/Svelte) |
| `tsconfig.json` | TypeScript |
| `*.csproj` / `*.vbproj` | .NET |
| `build.gradle` / `build.gradle.kts` | Java/Kotlin |
| `pom.xml` | Java/Maven |
| `mix.exs` | Elixir |

## Output

- Type + Stack terdeteksi
- Dengan `-EmitContext`: template markdown di `projects/context/<slug>.md` siap diisi

## Integrasi Registry

Setelah context dibuat, daftarkan project di `projects/registry.json`:

```json
{
  "projects": {
    "my-project": {
      "type": "<detected type>",
      "last_used": "2026-06-18",
      "context_file": "context/my-project.md",
      "kategori": { "...": "..." },
      "path": "C:/path/to/my-project",
      "dominan": "..."
    }
  }
}
```
