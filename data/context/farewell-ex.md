# farewell-ex

Type: Rust + Kotlin (Android kernel manager)
Path: C:/Users/FANNNDI/AppData/Local/Temp/farewell-ex
Stack: Rust (kernel-manager SDK) + Kotlin/Compose (Android app) + C++
Focus: 5-tier kernel manager (non-root → Xposed). GPU/DCI-P3/thermal profile for POCO X3 NFC.

Key files:
  - rust/kernel-manager/src/     — Rust SDK (sysfs, cpu, gpu, memory, power, thermal, scheduler, io, network, display, wake, renderer, spoof, daemon, tier, checker, lib)
  - rust/kernel-manager/Cargo.toml
  - android/app/src/main/java/   — Kotlin/Compose app
  - knowledge/modules/           — Knowledge modules
  - training/plan.md             — Development plan
