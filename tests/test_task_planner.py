import unittest

from forge_agent.task_planner import (
    create_task_plan,
    format_task_plan,
    plan_to_dict,
    update_task_plan,
)


class TaskPlannerTests(unittest.TestCase):
    def test_creates_task_plan_for_complex_goal(self) -> None:
        plan = create_task_plan("fix failing login test")

        self.assertEqual(plan.goal, "fix failing login test")
        self.assertGreaterEqual(len(plan.steps), 5)
        self.assertEqual(plan.steps[0].id, "step_1")
        self.assertEqual(plan.steps[0].status, "pending")
        self.assertEqual(plan.risks, [])
        self.assertIsNotNone(plan.updated_at)
        self.assertIn("Retrieve relevant repository context", [step.description for step in plan.steps])

    def test_formats_task_plan(self) -> None:
        plan = create_task_plan("implement password reset")

        output = format_task_plan(plan)

        self.assertIn("Plan: implement password reset", output)
        self.assertIn("step_1. [pending]", output)

    def test_updates_task_plan_step_status_and_notes(self) -> None:
        plan = plan_to_dict(create_task_plan("fix login"))

        updated = update_task_plan(plan, "step_1", "in_progress", "Reading auth files")

        self.assertEqual(updated["steps"][0]["status"], "in_progress")
        self.assertEqual(updated["steps"][0]["notes"], "Reading auth files")

    def test_failed_task_plan_step_adds_risk_note(self) -> None:
        plan = plan_to_dict(create_task_plan("fix login"))

        updated = update_task_plan(plan, "step_2", "failed", "Could not find login tests")

        self.assertEqual(updated["steps"][1]["status"], "failed")
        self.assertIn("step_2 failed: Could not find login tests", updated["risks"])

    def test_rejects_invalid_task_plan_status(self) -> None:
        plan = plan_to_dict(create_task_plan("fix login"))

        with self.assertRaises(ValueError):
            update_task_plan(plan, "step_1", "started")

    def test_rejects_unknown_task_plan_step(self) -> None:
        plan = plan_to_dict(create_task_plan("fix login"))

        with self.assertRaises(ValueError):
            update_task_plan(plan, "step_99", "completed")


if __name__ == "__main__":
    unittest.main()
