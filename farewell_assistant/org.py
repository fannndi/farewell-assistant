"""Organizational hierarchy -- roles, decision priority, workflow."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Role:
    title: str
    model_label: str
    status: str
    tier: str
    authority: list[str]
    focus: Optional[list[str]] = None
    contribution: str = ""


USER = Role(
    title="User",
    model_label="-",
    status="Pengguna",
    tier="boss",
    authority=[
        "Menentukan objective",
        "Menentukan prioritas",
        "Menyetujui hasil",
        "Meminta revisi",
    ],
    contribution="Pengguna adalah pengambil keputusan tertinggi, tidak ikut pekerjaan teknis langsung."
)

DIRECTOR = Role(
    title="Director AI",
    model_label="ocg/deepseek-v4-flash",
    status="Director Divisi -- Pegawai Tetap",
    tier="pegawai_tetap",
    authority=[
        "Memahami objective User",
        "Menentukan strategi & scope project",
        "Membuat Work Order",
        "Menentukan prioritas sprint",
        "Final review & executive decision",
    ],
    contribution="Tidak mengerjakan audit teknis langsung (kecuali diminta)",
)

DEPUTY = Role(
    title="Deputy Director AI",
    model_label="ds/deepseek-v4-flash",
    status="Wakil Director -- Pegawai Tetap",
    tier="pegawai_tetap",
    authority=[
        "Membantu Director",
        "Memvalidasi keputusan",
        "Second opinion",
        "Menjaga konsistensi strategi",
        "Menggantikan Director dalam emergency",
    ],
    contribution="Full authority jika Director tidak tersedia",
)

TEAM_LEADER = Role(
    title="Team Leader AI",
    model_label="oc/deepseek-v4-flash-free",
    status="Ketua Tim Engineering -- Pegawai Tetap",
    tier="pegawai_tetap",
    focus=["Frontend Audit", "Integrasi Sistem", "Audit Umum"],
    authority=[
        "Menerima Work Order",
        "Membagi pekerjaan",
        "Mengaudit frontend & integrasi sistem",
        "Bekerja bersama Senior Backend Engineer",
        "Menggabungkan seluruh hasil audit",
        "Menyelesaikan konflik rekomendasi",
        "Membuat laporan lengkap untuk Director",
    ],
    contribution="90% -- kontributor utama",
)

SENIOR_BACKEND = Role(
    title="Senior Backend Engineer",
    model_label="oc/mimo-v2.5-free",
    status="Pegawai Tetap",
    tier="pegawai_tetap",
    focus=["Backend", "API", "Database", "Auth", "Security"],
    authority=[
        "Bertanggung jawab penuh terhadap Backend, API, Database",
        "Authentication & Authorization",
        "Business Logic & Security",
        "Performance & Cache",
        "Backend Architecture",
    ],
    contribution="90% -- partner utama Team Leader",
)

JUNIOR_1 = Role(
    title="Junior Reviewer I -- Bug Finding",
    model_label="oc/big-pickle",
    status="Junior Reviewer",
    tier="junior",
    focus=["Bug Finding", "Edge Cases", "Functional Validation"],
    authority=["Validator -- menemukan masalah yang terlewat", "Memberikan alternatif solusi", "Validasi silang"],
    contribution="10% -- validator, bukan penentu keputusan",
)

JUNIOR_2 = Role(
    title="Junior Reviewer II -- Code Style",
    model_label="oc/north-mini-code-free",
    status="Junior Reviewer",
    tier="junior",
    focus=["Code Style", "Refactoring", "Naming", "Duplicate Code", "Maintainability"],
    authority=["Validator -- menemukan masalah yang terlewat", "Memberikan alternatif solusi", "Validasi silang"],
    contribution="10% -- validator, bukan penentu keputusan",
)

JUNIOR_3 = Role(
    title="Junior Reviewer III -- Architecture",
    model_label="oc/nemotron-3-ultra-free",
    status="Junior Reviewer",
    tier="junior",
    focus=["Architecture", "Scalability", "Optimization", "Long-term Maintainability"],
    authority=["Validator -- menemukan masalah yang terlewat", "Memberikan alternatif solusi", "Validasi silang"],
    contribution="10% -- validator, bukan penentu keputusan",
)

ROLES: dict[str, Role] = {
    "boss": USER,
    "director": DIRECTOR,
    "deputy": DEPUTY,
    "team_leader": TEAM_LEADER,
    "senior_backend": SENIOR_BACKEND,
    "junior_1": JUNIOR_1,
    "junior_2": JUNIOR_2,
    "junior_3": JUNIOR_3,
}

HIERARCHY_ORDER = [
    "boss", "director", "deputy", "team_leader",
    "senior_backend", "junior_1", "junior_2", "junior_3",
]

DECISION_PRIORITY: list[str] = HIERARCHY_ORDER.copy()

WORKFLOW_STEPS = [
    ("1. Pahami objective Director", "Baca & pahami Work Order dari Director"),
    ("2. Analisis ruang lingkup", "Tentukan scope, dependensi, risiko"),
    ("3. Tentukan pembagian tugas", "Alokasi ke Team Leader, Senior BE, Junior Reviewer"),
    ("4. Team Leader eksekusi", "Audit frontend, integrasi, analisis umum"),
    ("5. Senior BE eksekusi", "Audit backend mendalam (API, DB, Auth, Security)"),
    ("6. Junior Reviewer validasi", "Cari masalah terlewat, alternatif solusi"),
    ("7. Gabungkan hasil", "Konsolidasi semua temuan"),
    ("8. Hilangkan konflik", "Resolve perbedaan rekomendasi antar role"),
    ("9. Prioritaskan", "Urutkan berdasarkan dampak"),
    ("10. Laporkan", "Kirim laporan lengkap ke Director / Deputy Director"),
]

def pegawai_tetap() -> list[tuple[str, Role]]:
    return [(k, v) for k, v in ROLES.items() if v.tier == "pegawai_tetap"]


def junior_reviewers() -> list[tuple[str, Role]]:
    return [(k, v) for k, v in ROLES.items() if v.tier == "junior"]


def render_org_chart() -> str:
    lines = []
    lines.append("  Boss (User)")
    lines.append("  |-- Director AI")
    lines.append("  |   Model : ocg/deepseek-v4-flash")
    lines.append("  |-- Deputy Director AI")
    lines.append("  |   Model : ds/deepseek-v4-flash")
    lines.append("  +-- Team Leader AI (Anda)")
    lines.append("      Model : oc/deepseek-v4-flash-free")
    lines.append("      |-- Senior Backend Engineer")
    lines.append("      |   Model : oc/mimo-v2.5-free")
    lines.append("      |-- Junior Reviewer I")
    lines.append("      |   Model : oc/big-pickle")
    lines.append("      |-- Junior Reviewer II")
    lines.append("      |   Model : oc/north-mini-code-free")
    lines.append("      +-- Junior Reviewer III")
    lines.append("          Model : oc/nemotron-3-ultra-free")
    return "\n".join(lines)


def render_roles() -> str:
    lines = []
    for key in HIERARCHY_ORDER:
        r = ROLES[key]
        lines.append(f"\n  [{r.tier.upper()}] {r.title}")
        lines.append(f"  Model: {r.model_label}")
        lines.append(f"  Status: {r.status}")
        if r.focus:
            lines.append(f"  Fokus: {', '.join(r.focus)}")
        lines.append(f"  Kontribusi: {r.contribution}")
        lines.append("  Wewenang:")
        for a in r.authority:
            lines.append(f"    - {a}")
    return "\n".join(lines)


def render_workflow() -> str:
    lines = ["  Saat menerima Work Order:"]
    for title, desc in WORKFLOW_STEPS:
        lines.append(f"\n  {title}")
        lines.append(f"    {desc}")
    return "\n".join(lines)


def render_priority() -> str:
    lines = ["  Prioritas keputusan (saat ada perbedaan pendapat):"]
    for i, key in enumerate(DECISION_PRIORITY, 1):
        r = ROLES[key]
        lines.append(f"  {i}. {r.title} ({r.model_label})")
    lines.append("")
    lines.append("  Keputusan berdasarkan kualitas analisis, bukti teknis, dan otoritas peran -- BUKAN jumlah suara.")
    return "\n".join(lines)
