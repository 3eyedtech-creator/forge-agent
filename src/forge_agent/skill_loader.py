from dataclasses import dataclass
from pathlib import Path


@dataclass
class Skill:
    name: str
    description: str
    body: str
    path: Path
    source: str


def default_builtin_skills_dir() -> Path:
    return Path(__file__).resolve().parent / "builtin_skills"


def load_skill_file(path: Path, source: str) -> Skill:
    text = path.read_text(encoding="utf-8")
    metadata, body = parse_skill_markdown(text)
    name = metadata.get("name") or path.parent.name
    description = metadata.get("description", "")

    return Skill(
        name=name,
        description=description,
        body=body.strip(),
        path=path,
        source=source,
    )


def parse_skill_markdown(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text

    parts = text.split("---\n", maxsplit=2)
    if len(parts) < 3:
        return {}, text

    metadata_text = parts[1]
    body = parts[2]
    metadata = {}
    for line in metadata_text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", maxsplit=1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")

    return metadata, body


def discover_skills(project_dir: Path, user_dir: Path, builtin_dir: Path) -> dict[str, Skill]:
    skills = {}

    for source, directory in (
        ("builtin", builtin_dir),
        ("user", user_dir),
        ("project", project_dir),
    ):
        for skill in discover_skills_in_dir(directory, source):
            skills[skill.name] = skill

    return dict(sorted(skills.items()))


def discover_skills_in_dir(directory: Path, source: str) -> list[Skill]:
    if not directory.exists():
        return []

    skills = []
    for skill_file in sorted(directory.glob("*/SKILL.md")):
        skills.append(load_skill_file(skill_file, source))

    return skills


def format_skill_list(skills: dict[str, Skill]) -> str:
    if not skills:
        return "No skills found."

    return "\n".join(
        f"{skill.name} [{skill.source}] - {skill.description}"
        for skill in skills.values()
    )


def format_skill_show(skill: Skill) -> str:
    return (
        f"Skill: {skill.name}\n"
        f"Source: {skill.source}\n"
        f"Path: {skill.path}\n"
        f"Description: {skill.description}\n\n"
        f"{skill.body}"
    )


def format_skill_system_prompt(skill: Skill) -> str:
    return (
        f"Active skill: {skill.name}\n"
        "Follow these skill instructions when they are relevant to the user's request.\n\n"
        f"{skill.body}"
    )
