# Footer (cek state di .opencode/CONTEXT.md)

# Mode Enforcement
- **PLAN mode**: Agent jadi read-only (tools terbatas). Hanya Read/Glob/Grep/GrepTool.
  Bash commands STRICTLY forbidden.
  Gunakan `/workmode build` untuk switching ke full tools.
- **BUILD mode**: Full write access via edit/write tools. Agent = orchestrator (team).

# Execution
- YAGNI: best code is code never written
- Ultra terse: max 4 baris, kode langsung tanpa preamble
- Bug fix: langsung eksekusi tanpa hold
- NEW task: HOLD --> PLAN --> APPROVE --> eksekusi
- Commit: hanya jika user minta

# Team Hierarchy
Semua dalam eksekusi via **Team mode**:
- **Divisi** (team=ON): `ocg/deepseek-v4-flash` sebagai leader
- **Tim** (team=OFF): `oc/deepseek-v4-flash-free` sebagai leader
- Sub-agents selalu pake Free combo (4 worker models, round-robin)
- Leader orchestrator — delegasi ke sub-agents specialist

# Skill Priority
Skill dari ECC. Load via indexer per project.
