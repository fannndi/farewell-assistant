# Simulasi Audit — farewell-ex (001)

> **Footer:** `Farewell: ON | Project: 001-farewell-ex | BUILD | Turn: 1 | Chain: 1 | 60% | Eco`
> **User:** optimize rust sysfs read performance
> **Stack detected:** rust
> **Role:** AI model auditing cross-language Rust + Android (Kotlin) app

---

## Pipeline Route (Real)

```
Input:          "optimize rust sysfs read performance"
Intent:         ask
Domain:         general
Complexity:     low
Confidence:     60%
Source:         quick
Stack:          [rust]
Model:          Free=Free / Emergency=Free
Skill Chain (1 step):
  1. documentation-lookup  — Look up relevant docs
```

### 🔍 Observation
Intent misclassification! "optimize" → tidak masuk pattern `fix/bug/error` atau `create/build`. Inference: kata "optimize" tidak ada di `_INTENT_PATTERNS`.

**Expected:** `fix` atau `build` (medium complexity)
**Actual:** `ask` (low complexity)

**Impact:** Skill chain hanya 1 step (lookup docs) → tidak akan produce code fix.

---

## Skenario 1: Rust Sysfs Performance

**Input AI:** `"optimize rust sysfs read performance"`

### Architecture Snapshot
```
Android App (Kotlin)
  ↓ JNI bridge
Rust library (farewell_native)  ← cdylib
  ↓ direct sysfs read
Kernel sysfs (/sys/devices/...)
```

40+ JNI functions across 17 modules: CPU, GPU, memory, thermal, power, I/O, network, display, boot.

### AI Model Perspective
Sebagai AI model, saya harus:

1. **Cek current pattern** — `lib.rs` baca sysfs via `std::fs::read_to_string()`?
2. **Cek JNI overhead** — berapa banyak JNI call per read?
3. **Cek caching** — sysfs values di-cache atau baca langsung tiap kali?
4. **Cek error handling** — sysfs file mungkin tidak ada di kernel tertentu
5. **Cek batch read** — bisa batch beberapa sysfs dalam satu JNI call?

### Checklist Item Spesifik

| # | Item | Cek | Severity |
|---|------|-----|----------|
| FE-1 | JNI call frequency | Berapa JNI call per second? | HIGH |
| FE-2 | Sysfs caching | Nilai di-cache atau baca setiap refresh? | HIGH |
| FE-3 | Error fallback | Sysfs file missing → fallback atau crash? | CRITICAL |
| FE-4 | Batch reads | Bisa batch sysfs dalam 1 JNI call? | MEDIUM |
| FE-5 | Use rustix | `rustix` crate untuk sysfs (lebih cepat)? | MEDIUM |
| FE-6 | Thread safety | `Mutex` atau channel untuk shared state? | HIGH |
| FE-7 | Logging overhead | `android_logger` terlalu verbose? | LOW |

### Code Fix Simulation

```rust
// Before: baca sysfs tiap JNI call (slow!)
#[no_mangle]
pub extern "C" fn Java_com_farewell_kernelmanager_kernel_NativeLib_readCpuFreq(
    env: JNIEnv, _class: JClass, path: JString,
) -> jstring {
    let path: String = env.get_string(&path).unwrap().into();
    let content = std::fs::read_to_string(&path).unwrap_or_default();
    env.new_string(content).unwrap().into_raw()
}

// After: cache + batch + error handling
use std::collections::HashMap;
use std::sync::Mutex;
use std::time::{Duration, Instant};

static CACHE: once_cell::sync::Lazy<Mutex<HashMap<String, (String, Instant)>>> =
    once_cell::sync::Lazy::new(|| Mutex::new(HashMap::new()));

const CACHE_TTL: Duration = Duration::from_millis(500);

fn read_sysfs_cached(path: &str) -> String {
    let mut cache = CACHE.lock().unwrap();
    if let Some((val, time)) = cache.get(path) {
        if time.elapsed() < CACHE_TTL {
            return val.clone();
        }
    }
    let val = rustix::fs::readlinkat(rustix::fs::CWD, path)  // use rustix
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    cache.insert(path.to_string(), (val.clone(), Instant::now()));
    val
}
```

**Performance gain estimasi:** ~60% (reduce syscall + JNI overhead)

---

## Skenario 2: Rust Build Verification — No Self-Heal

**Input AI:** `"fix rust build error in Cargo.toml"`

### Pipeline Prediction
| Intent | Domain | Chain |
|--------|--------|-------|
| fix | general | fix (3 steps) |

### Critical Finding: No Self-Heal for Rust
`self_heal.py` hanya check `.py`, `.ts/.tsx`, `.dart`. 
- `.rs` files → **no post-edit typecheck**
- `Cargo.toml` → **no validation**

**Impact:** Rust type error bisa terlewat sampai `cargo build` di CI.

### Checklist
| # | Item | Severity |
|---|------|----------|
| FE-8 | No rust-analyzer check post-edit | MEDIUM |
| FE-9 | JNI signature mismatch | HIGH |
| FE-10 | `cargo build` di CI? | MEDIUM |
| FE-11 | Cargo.lock version pinned? | LOW |

---

## Skenario 3: Android Gradle Build

**Input AI:** `"upgrade AGP from 8.7.3"`

### Pipeline Prediction
| Intent | Domain | Chain |
|--------|--------|-------|
| build | mobile | build_mobile (7 steps) |

### Checklist
| # | Item | Cek |
|---|------|-----|
| FE-12 | Gradle KTS versi | Compatible Kotlin 2.1.0? |
| FE-13 | AGP 8.7.3 → 8.x.x | Breaking changes? |
| FE-14 | JNI library path | `farewell_native.so` di `jniLibs/`? |

---

## Temuan Potensial

| # | Temuan | Severity | Rekomendasi |
|---|--------|----------|-------------|
| 1 | "optimize" tidak dikenali sebagai build/fix | MEDIUM | Tambah "optimize" ke `_INTENT_PATTERNS` |
| 2 | No self-heal untuk Rust | MEDIUM | Tambah `cargo check` ke `self_heal.py` |
| 3 | JNI overhead tinggi di high-frequency paths | HIGH | Batch via JSON atau protobuf |
| 4 | Sysfs read tanpa cache | HIGH | Implement cache dengan TTL |
| 5 | Thread safety di JNI global state | HIGH | Pakai `once_cell` + `Mutex` |

---

*Simulasi: 2026-06-22 | farewell-assistant v1.5.0 | Route: ask → general (misclassify)*
