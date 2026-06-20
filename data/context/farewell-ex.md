# farewell-ex

Type: Rust + Kotlin (Android kernel manager)
Path: C:/Users/FANNNDI/Documents/farewell-ex
Stack: Rust (kernel-manager SDK, 18 modules) + Kotlin/Compose (Android app) + C++ (Zygisk)
Focus: Reverse engineering 16 repos → Rust library → Android app. 5-tier access (non-root → Xposed).

Key files:
  - rust/kernel-manager/src/     — Rust SDK (sysfs, cpu, gpu, memory, power, thermal, scheduler, io, network, display, wake, renderer, spoof, display_control, daemon, tier, checker, lib)
  - rust/kernel-manager/Cargo.toml
  - android/app/src/main/java/   — Kotlin/Compose app (kernel, viewmodel, ui, service)
  - knowledge/modules/           — 25 knowledge modules
  - knowledge/feature-catalog.md — 200+ features catalog
  - training/plan.md             — Master plan

Target: POCO X3 NFC (Qualcomm SM7150-AC, Adreno 618)
Root: KernelSU-Next + ZygiskNext + Vector
