"""Skill chain builder - Maps intent+domain to skill execution chains."""

from . import config
from .helpers import _c

# ---------------------------------------------------------------------------
# Core Skill Chains
# ---------------------------------------------------------------------------

SKILL_CHAINS: dict[str, list[dict[str, str]]] = {
    # BUILD CHAINS (comprehensive)
    "build_web": [
        {"name": "orch-add-feature",      "desc": "Orchestrate end-to-end feature build"},
        {"name": "api-design",            "desc": "Design REST endpoints + schemas"},
        {"name": "backend-patterns",      "desc": "Service layer + repository patterns"},
        {"name": "database-migrations",   "desc": "Schema creation + migrations"},
        {"name": "tdd-workflow",          "desc": "Write tests before implementation"},
        {"name": "security-review",       "desc": "Auth + input validation"},
        {"name": "verification-loop",     "desc": "Verify all passes green"},
        {"name": "git-workflow",          "desc": "Commit the feature"},
    ],
    "build_mobile": [
        {"name": "orch-add-feature",      "desc": "Orchestrate end-to-end feature build"},
        {"name": "dart-flutter-patterns", "desc": "Flutter/Dart framework patterns"},
        {"name": "database-migrations",   "desc": "Local DB schema + migrations"},
        {"name": "tdd-workflow",          "desc": "Write widget tests before implementation"},
        {"name": "security-review",       "desc": "Auth + storage security"},
        {"name": "verification-loop",     "desc": "Verify all passes"},
        {"name": "git-workflow",          "desc": "Commit the feature"},
    ],
    "build_infra": [
        {"name": "orch-add-feature",      "desc": "Orchestrate infrastructure change"},
        {"name": "deployment-patterns",   "desc": "CI/CD + blue-green / canary"},
        {"name": "docker-patterns",       "desc": "Container configuration"},
        {"name": "kubernetes-patterns",   "desc": "K8s manifests if applicable"},
        {"name": "database-migrations",   "desc": "Schema changes"},
        {"name": "verification-loop",     "desc": "Verify deploy readiness"},
        {"name": "git-workflow",          "desc": "Commit the infrastructure"},
    ],
    "build_data": [
        {"name": "orch-add-feature",      "desc": "Orchestrate data pipeline"},
        {"name": "postgres-patterns",     "desc": "PostgreSQL patterns + optimization"},
        {"name": "database-migrations",   "desc": "Schema + data migrations"},
        {"name": "tdd-workflow",          "desc": "Write data validation tests"},
        {"name": "verification-loop",     "desc": "Verify data integrity"},
        {"name": "git-workflow",          "desc": "Commit the pipeline"},
    ],
    "build_automation": [
        {"name": "orch-add-feature",      "desc": "Orchestrate automation feature"},
        {"name": "powershell-patterns",   "desc": "PowerShell patterns + best practices"},
        {"name": "tdd-workflow",          "desc": "Write tests for automation"},
        {"name": "verification-loop",     "desc": "Verify automation works"},
        {"name": "git-workflow",          "desc": "Commit the automation"},
    ],
    "build_ai_ml": [
        {"name": "orch-add-feature",      "desc": "Orchestrate ML feature"},
        {"name": "pytorch-patterns",      "desc": "PyTorch model patterns"},
        {"name": "mle-workflow",          "desc": "Production ML pipeline"},
        {"name": "tdd-workflow",          "desc": "Write model validation tests"},
        {"name": "verification-loop",     "desc": "Verify model performance"},
        {"name": "git-workflow",          "desc": "Commit the ML pipeline"},
    ],
    "build": [
        {"name": "orch-add-feature",      "desc": "Orchestrate feature build"},
        {"name": "tdd-workflow",          "desc": "Write tests first"},
        {"name": "security-review",       "desc": "Security validation"},
        {"name": "verification-loop",     "desc": "Verify all passes"},
        {"name": "git-workflow",          "desc": "Commit the feature"},
    ],
    # FIX CHAINS
    "fix_bug": [
        {"name": "search-first",          "desc": "Check if bug is known"},
        {"name": "orch-fix-defect",       "desc": "Reproduce -> fix -> verify"},
        {"name": "ai-regression-testing", "desc": "Write regression test"},
        {"name": "verification-loop",     "desc": "Verify fix doesn't break others"},
        {"name": "git-workflow",          "desc": "Commit the fix"},
    ],
    "fix_security": [
        {"name": "repo-scan",             "desc": "Full codebase scan"},
        {"name": "security-review",       "desc": "Comprehensive security checklist"},
        {"name": "safety-guard",          "desc": "Prevent destructive fixes"},
        {"name": "verification-loop",     "desc": "Verify security fix"},
        {"name": "git-workflow",          "desc": "Commit security fix"},
    ],
    "fix": [
        {"name": "search-first",          "desc": "Check known issues"},
        {"name": "orch-fix-defect",       "desc": "Fix the defect"},
        {"name": "verification-loop",     "desc": "Verify fix"},
    ],
    # REVIEW CHAINS
    "review_code": [
        {"name": "coding-standards",      "desc": "Baseline conventions check"},
        {"name": "error-handling",        "desc": "Error handling audit"},
        {"name": "security-review",       "desc": "Vulnerability check"},
        {"name": "codehealth-mcp",        "desc": "Structural health score"},
        {"name": "verification-loop",     "desc": "Final verification"},
    ],
    "review_security": [
        {"name": "repo-scan",             "desc": "Full codebase scan"},
        {"name": "security-bounty-hunter","desc": "Hunt exploitable vulns"},
        {"name": "security-scan",         "desc": "Config security audit"},
        {"name": "verification-loop",     "desc": "Verify findings"},
    ],
    "review": [
        {"name": "coding-standards",      "desc": "Check conventions"},
        {"name": "security-review",       "desc": "Security check"},
        {"name": "verification-loop",     "desc": "Verify"},
    ],
    # DEPLOY CHAINS
    "deploy": [
        {"name": "production-audit",      "desc": "Pre-deploy readiness"},
        {"name": "deployment-patterns",   "desc": "Deploy strategy"},
        {"name": "canary-watch",          "desc": "Post-deploy monitoring"},
        {"name": "git-workflow",          "desc": "Release tagging"},
    ],
    # RESEARCH CHAINS
    "research": [
        {"name": "research-ops",          "desc": "Evidence-first research"},
        {"name": "documentation-lookup",  "desc": "Live docs lookup"},
    ],
    "research_deep": [
        {"name": "research-ops",          "desc": "Evidence-first research"},
        {"name": "deep-research",         "desc": "Multi-source research"},
        {"name": "documentation-lookup",  "desc": "Live docs"},
        {"name": "competitive-platform-analysis", "desc": "Competitive analysis"},
    ],
    # DOCS CHAINS
    "docs": [
        {"name": "codebase-onboarding",   "desc": "Analyze codebase structure"},
        {"name": "article-writing",       "desc": "Write documentation"},
        {"name": "knowledge-ops",         "desc": "Store in knowledge base"},
    ],
    "docs_code": [
        {"name": "codebase-onboarding",   "desc": "Analyze codebase"},
        {"name": "code-tour",             "desc": "Create interactive walkthrough"},
        {"name": "architecture-decision-records", "desc": "Capture ADRs"},
        {"name": "article-writing",       "desc": "Write docs"},
    ],
    # ASK CHAINS
    "ask": [
        {"name": "documentation-lookup",  "desc": "Look up relevant docs"},
    ],
}


def get_skill_chain(intent: str, domain: str) -> list[dict[str, str]]:
    """Get skill chain by intent + domain, with fallback."""
    key = f"{intent}_{domain}"
    chain = SKILL_CHAINS.get(key)
    if chain:
        return chain
    chain = SKILL_CHAINS.get(intent)
    if chain:
        return chain
    return SKILL_CHAINS["ask"]


def test_skill_chain(chain: list[dict[str, str]]) -> dict:
    """Check if skills in chain exist on disk. Checks ecc/ and data/ skills dirs."""
    search_dirs = [
        config.ECC_DIR / "skills",
        config.PROJECT_SKILLS_DIR,
    ]
    valid = []
    missing = []
    for step in chain:
        found = any((d / step["name"] / "SKILL.md").exists() for d in search_dirs)
        if found:
            valid.append(step["name"])
        else:
            missing.append(step["name"])
    return {
        "valid": valid,
        "missing": missing,
        "valid_count": len(valid),
        "total_count": len(chain),
    }


def show_skill_chain(chain: list[dict[str, str]], label: str = "Skill Chain"):
    """Display skill chain to stdout."""
    print(f"\n  {label} ({len(chain)} steps):")
    for i, step in enumerate(chain, 1):
        print(f"    {i}. {_c(step['name'], 'cyan')}")
        print(f"       {step['desc']}")
    print()
