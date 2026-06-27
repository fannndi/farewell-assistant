"""Awesome Opencode indexers and project stack matching."""

import yaml
from pathlib import Path

from . import config


def _load_yaml(path: Path) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def load_all_entries() -> tuple[list, list, list, list, list]:
    plugins = []; themes = []; agents = []; projects = []; resources = []
    plugins_dir = config.AWESOME_DIR / "data" / "plugins"
    themes_dir = config.AWESOME_DIR / "data" / "themes"
    agents_dir = config.AWESOME_DIR / "data" / "agents"
    projects_dir = config.AWESOME_DIR / "data" / "projects"
    resources_dir = config.AWESOME_DIR / "data" / "resources"

    for f in plugins_dir.glob("*.yaml"):
        plugins.append(_load_yaml(f))
    for f in themes_dir.glob("*.yaml"):
        themes.append(_load_yaml(f))
    for f in agents_dir.glob("*.yaml"):
        agents.append(_load_yaml(f))
    for f in projects_dir.glob("*.yaml"):
        projects.append(_load_yaml(f))
    for f in resources_dir.glob("*.yaml"):
        resources.append(_load_yaml(f))

    return plugins, themes, agents, projects, resources


def get_recommended_projects_for_stack(stack: list[str]) -> list:
    _, _, _, projects, _ = load_all_entries()
    lower_stack = [s.lower() for s in stack]
    scored = []

    for p in projects:
        score = 0
        tags = p.get("tags", [])
        for t in tags:
            if t.lower() in lower_stack:
                score += 3
            if p.get("name", "").lower() in t.lower() or t.lower() in p.get("name", "").lower():
                score += 2
        if score > 0:
            p["_score"] = score
            scored.append(p)

    return sorted(scored, key=lambda x: x["_score"], reverse=True)[:20]


