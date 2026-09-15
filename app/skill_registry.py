"""Controlled skill snapshot registry.

Commercial skills and engineering security skills are intentionally separate. The
registry exposes metadata and trusted local documents; it never treats security
skills as commercial reasoning skills.
"""
from pathlib import Path
import re

ROOT = Path(__file__).parent / "skills"
SOURCES = {
    "commercial": {"source": "Pharma-commercial-skills", "version": "cf61ede8a0c11fa9b9f6e8f98205b8c4048cac57", "url": "https://github.com/alifathallaali/Pharma-commercial-skills"},
    "security": {"source": "AI-Agent-security-skills", "version": "cba5d66e6fda6123247e2b4baa5fd6c65c7a3bd6", "url": "https://github.com/alifathallaali/AI-Agent-security-skills"},
}


def list_skills(layer: str) -> list[dict]:
    if layer not in SOURCES:
        raise ValueError("Unknown skill layer")
    base = ROOT / layer / "skills" if layer == "commercial" else ROOT / layer
    result = []
    if layer == "security":
        names = ["security-review", "authentication-review", "authorization-review", "input-validation", "api-security", "data-security", "ai-agent-security", "file-upload-security", "secrets-management", "dependency-security", "security-testing"]
        return [{"name": name, "layer": layer, "skill_source": SOURCES[layer]["source"], "skill_version": SOURCES[layer]["version"], "path": str(ROOT / layer)} for name in names]
    for path in sorted(base.glob("*/SKILL.md")) if base.exists() else []:
        name = path.parent.name
        result.append({"name": name, "layer": layer, "skill_source": SOURCES[layer]["source"], "skill_version": SOURCES[layer]["version"], "path": str(path)})
    return result


def select_commercial_skills(objective: str, limit: int = 3) -> list[dict]:
    text = objective.lower()
    aliases = {
        "market": "01-market-analysis", "segment": "02-pharma-segmentation", "hcp": "03-hcp-segmentation",
        "position": "04-brand-positioning", "compet": "05-competitive-intelligence", "brand": "06-brand-strategy",
        "campaign": "07-campaign-planning", "launch": "08-launch-strategy", "sfe": "09-sales-force-effectiveness",
        "force": "09-sales-force-effectiveness", "plan": "10-brand-plan", "target": "15-target-setting",
        "portfolio": "17-portfolio-strategy", "commercial": "20-commercial-analytics", "pricing": "14-pricing-strategy",
    }
    names = []
    for keyword, name in aliases.items():
        if keyword in text and name not in names: names.append(name)
    available = {item["name"]: item for item in list_skills("commercial")}
    return [available[name] for name in names if name in available][:limit]


def read_skill(skill: dict, max_chars: int = 8000) -> str:
    path = Path(skill["path"])
    if not path.is_file(): return ""
    return path.read_text(encoding="utf-8")[:max_chars]


def catalog() -> dict:
    return {
        "domain_skills": {"commercial": [{k: v for k, v in item.items() if k != "path"} for item in list_skills("commercial")]},
        "engineering_skills": {"security": [{k: v for k, v in item.items() if k != "path"} for item in list_skills("security")]},
    }
