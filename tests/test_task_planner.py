import unittest

from forge_agent.task_planner import create_task_plan, format_task_plan


class TaskPlannerTests(unittest.TestCase):
    def test_creates_task_plan_for_complex_goal(self) -> None:
        plan = create_task_plan("fix failing login test")

        self.assertEqual(plan.goal, "fix failing login test")
        self.assertGreaterEqual(len(plan.steps), 5)
        self.assertEqual(plan.steps[0].status, "pending")
        self.assertIn("Retrieve relevant repository context", [step.description for step in plan.steps])

    def test_formats_task_plan(self) -> None:
        plan = create_task_plan("implement password reset")

        output = format_task_plan(plan)

        self.assertIn("Plan: implement password reset", output)
        self.assertIn("1. [pending]", output)


if __name__ == "__main__":
    unittest.main()
