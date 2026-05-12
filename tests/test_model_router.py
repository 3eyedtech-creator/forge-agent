import unittest

from forge_agent.model_router import route_model


class ModelRouterTests(unittest.TestCase):
    def test_routes_simple_query_to_fast_model(self) -> None:
        selection = route_model(
            "what can you do?",
            fast_model="fast-model",
            reasoning_model="reasoning-model",
        )

        self.assertEqual(selection.model, "fast-model")
        self.assertEqual(selection.task_complexity, "simple")
        self.assertFalse(selection.should_plan)

    def test_routes_complex_query_to_reasoning_model(self) -> None:
        selection = route_model(
            "implement password reset across multiple files",
            fast_model="fast-model",
            reasoning_model="reasoning-model",
        )

        self.assertEqual(selection.model, "reasoning-model")
        self.assertEqual(selection.task_complexity, "complex")
        self.assertTrue(selection.should_plan)
        self.assertIn("complex", selection.reason.lower())

    def test_routes_refactor_and_debug_queries_to_reasoning_model(self) -> None:
        for query in ["refactor billing service", "debug failing login test"]:
            selection = route_model(
                query,
                fast_model="fast-model",
                reasoning_model="reasoning-model",
            )

            self.assertEqual(selection.model, "reasoning-model")
            self.assertTrue(selection.should_plan)


if __name__ == "__main__":
    unittest.main()
