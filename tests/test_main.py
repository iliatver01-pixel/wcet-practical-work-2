
import unittest

from src.main import (
    Operation,
    ProcessorModel,
    best_case,
    worst_case,
    bcet,
    wcet,
    nondeterminism_ratio,
    source_breakdown,
)


class TestWCET(unittest.TestCase):
    def setUp(self):
        self.model = ProcessorModel(
            base_cost=1,
            cache_miss_penalty=20,
            branch_mispredict_penalty=10,
        )
        self.fragment = [
            Operation("Read", "read", 1, 0),
            Operation("Check", "check", 0, 1),
            Operation("Filter", "compute", 1, 0),
            Operation("CheckResult", "check", 0, 1),
            Operation("Write", "write", 1, 0),
            Operation("Prepare", "compute", 0, 0),
            Operation("Update", "compute", 0, 0),
            Operation("Finish", "control", 0, 0),
        ]

    def test_best_case(self):
        self.assertEqual(bcet(self.fragment, self.model), 8)

    def test_worst_case(self):
        self.assertEqual(wcet(self.fragment, self.model), 88)

    def test_nondeterminism_ratio(self):
        self.assertEqual(
            nondeterminism_ratio(self.fragment, self.model), 11
        )

    def test_source_breakdown(self):
        self.assertEqual(
            source_breakdown(self.fragment, self.model),
            {"base": 8, "memory": 60, "branches": 20},
        )

    def test_individual_operation(self):
        op = self.fragment[0]
        self.assertEqual(best_case(op, self.model), 1)
        self.assertEqual(worst_case(op, self.model), 21)


if __name__ == "__main__":
    unittest.main()
