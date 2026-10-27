"""WCET/BCET estimator for a simple processor model. Python 3.10+."""
from dataclasses import dataclass
from pathlib import Path
import json
import argparse


@dataclass
class Operation:
    name: str
    op_type: str
    memory_accesses: int = 0
    branches: int = 0


@dataclass
class ProcessorModel:
    base_cost: int
    cache_miss_penalty: int
    branch_mispredict_penalty: int


def load_input(path: Path) -> tuple[list[Operation], ProcessorModel, int]:
    """Load processor model, operation fragment and deadline from JSON."""
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    model = ProcessorModel(**data["processor"])
    fragment = [Operation(**item) for item in data["operations"]]
    deadline = int(data["deadline"])
    if not fragment:
        raise ValueError("The operations list must not be empty.")
    if model.base_cost <= 0:
        raise ValueError("base_cost must be greater than zero.")
    if model.cache_miss_penalty < 0 or model.branch_mispredict_penalty < 0:
        raise ValueError("Penalty values cannot be negative.")
    for op in fragment:
        if op.memory_accesses < 0 or op.branches < 0:
            raise ValueError(f"Negative access/branch count in operation: {op.name}")
    if deadline < 0:
        raise ValueError("deadline cannot be negative.")
    return fragment, model, deadline


def best_case(op: Operation, model: ProcessorModel) -> int:
    """Best case: all memory accesses hit and all branches are predicted correctly."""
    return model.base_cost


def worst_case(op: Operation, model: ProcessorModel) -> int:
    """Worst case: each listed memory access misses and each branch is mispredicted."""
    return (
        model.base_cost
        + op.memory_accesses * model.cache_miss_penalty
        + op.branches * model.branch_mispredict_penalty
    )


def bcet(fragment: list[Operation], model: ProcessorModel) -> int:
    return sum(best_case(op, model) for op in fragment)


def wcet(fragment: list[Operation], model: ProcessorModel) -> int:
    return sum(worst_case(op, model) for op in fragment)


def nondeterminism_ratio(fragment: list[Operation], model: ProcessorModel) -> float:
    best = bcet(fragment, model)
    return wcet(fragment, model) / best if best else float("inf")


def source_breakdown(fragment: list[Operation], model: ProcessorModel) -> dict[str, int]:
    memory = sum(op.memory_accesses for op in fragment) * model.cache_miss_penalty
    branches = sum(op.branches for op in fragment) * model.branch_mispredict_penalty
    return {"base": bcet(fragment, model), "memory": memory, "branches": branches}


def print_report(fragment: list[Operation], model: ProcessorModel, deadline: int) -> None:
    print("\\nWCET — оценка времени выполнения (в тактах)")
    print("-" * 76)
    print(f"{'Операция':<24} {'Тип':<18} {'Память':>8} {'Ветвления':>10} {'Лучшее':>9} {'Худшее':>9}")
    print("-" * 76)
    for op in fragment:
        print(f"{op.name:<24} {op.op_type:<18} {op.memory_accesses:>8} {op.branches:>10} "
              f"{best_case(op, model):>9} {worst_case(op, model):>9}")

    best, worst = bcet(fragment, model), wcet(fragment, model)
    ratio = nondeterminism_ratio(fragment, model)
    breakdown = source_breakdown(fragment, model)
    print("-" * 76)
    print(f"BCET: {best} тактов")
    print(f"WCET: {worst} тактов")
    print(f"Коэффициент недетерминизма (WCET / BCET): {ratio:.2f}")
    print("Вклад в WCET:")
    print(f"  Базовая стоимость операций: {breakdown['base']} тактов")
    print(f"  Промахи кэша/память:         {breakdown['memory']} тактов")
    print(f"  Ошибки предсказания:         {breakdown['branches']} тактов")
    print(f"Дедлайн: {deadline} тактов")
    print("Результат: " + ("ФРАГМЕНТ УКЛАДЫВАЕТСЯ В ДЕДЛАЙН."
                        if worst <= deadline else "ФРАГМЕНТ НЕ УКЛАДЫВАЕТСЯ В ДЕДЛАЙН."))


def main() -> None:
    parser = argparse.ArgumentParser(description="Оценка BCET/WCET по JSON-файлу.")
    parser.add_argument("input", nargs="?", default="data/example.json",
                        help="путь к входному JSON (по умолчанию data/example.json)")
    args = parser.parse_args()
    try:
        fragment, model, deadline = load_input(Path(args.input))
        print_report(fragment, model, deadline)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        raise SystemExit(f"Ошибка входных данных: {error}")


if __name__ == "__main__":
    main()
