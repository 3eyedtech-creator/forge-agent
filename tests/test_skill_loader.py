import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from forge_agent.skill_loader import (
    Skill,
    default_builtin_skills_dir,
    discover_skills,
    format_skill_list,
    format_skill_show,
    format_skill_system_prompt,
    load_skill_file,
)


class SkillLoaderTests(unittest.TestCase):
    def test_loads_skill_with_frontmatter(self) -> None:
        with TemporaryDirectory() as temp_dir:
            skill_file = Path(temp_dir) / "SKILL.md"
            skill_file.write_text(
                "---\n"
                "name: bugfix\n"
                "description: Use when fixing bugs.\n"
                "---\n"
                "\n"
                "# Bugfix\n"
                "\n"
                "Reproduce the issue first.\n",
                encoding="utf-8",
            )

            skill = load_skill_file(skill_file, source="project")

        self.assertEqual(skill.name, "bugfix")
        self.assertEqual(skill.description, "Use when fixing bugs.")
        self.assertEqual(skill.source, "project")
        self.assertIn("Reproduce the issue first.", skill.body)

    def test_loads_skill_without_frontmatter_using_directory_name(self) -> None:
        with TemporaryDirectory() as temp_dir:
            skill_dir = Path(temp_dir) / "explain-code"
            skill_dir.mkdir()
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text("# Explain Code\nExplain the code clearly.\n", encoding="utf-8")

            skill = load_skill_file(skill_file, source="project")

        self.assertEqual(skill.name, "explain-code")
        self.assertEqual(skill.description, "")
        self.assertIn("Explain the code clearly.", skill.body)

    def test_discovers_project_user_and_builtin_skills_with_project_precedence(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            builtin = root / "builtin"
            user = root / "user"
            project = root / "project"
            for base in (builtin, user, project):
                (base / "bugfix").mkdir(parents=True)
                (base / "bugfix" / "SKILL.md").write_text(
                    f"---\nname: bugfix\ndescription: {base.name} skill\n---\nBody",
                    encoding="utf-8",
                )

            skills = discover_skills(project_dir=project, user_dir=user, builtin_dir=builtin)

        self.assertEqual(skills["bugfix"].description, "project skill")
        self.assertEqual(skills["bugfix"].source, "project")

    def test_formats_skill_list_and_show(self) -> None:
        skills = {
            "bugfix": Skill(
                name="bugfix",
                description="Use when fixing bugs.",
                body="# Bugfix",
                path=Path("SKILL.md"),
                source="builtin",
            )
        }

        self.assertIn("bugfix [builtin] - Use when fixing bugs.", format_skill_list(skills))
        self.assertIn("Skill: bugfix", format_skill_show(skills["bugfix"]))

    def test_formats_skill_system_prompt(self) -> None:
        skill = Skill(
            name="bugfix",
            description="Use when fixing bugs.",
            body="# Bugfix\nReproduce first.",
            path=Path("SKILL.md"),
            source="builtin",
        )

        output = format_skill_system_prompt(skill)

        self.assertIn("Active skill: bugfix", output)
        self.assertIn("Reproduce first.", output)

    def test_discovers_default_builtin_skills(self) -> None:
        skills = discover_skills(
            project_dir=Path("missing-project-skills"),
            user_dir=Path("missing-user-skills"),
            builtin_dir=default_builtin_skills_dir(),
        )

        self.assertIn("bugfix", skills)
        self.assertIn("explain-code", skills)
        self.assertIn("git", skills)
        self.assertIn("github", skills)


if __name__ == "__main__":
    unittest.main()
