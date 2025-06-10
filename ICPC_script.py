import json
import os
import numpy as np
from typing import Any, Dict, List, Tuple

def pass_at_k(n, c, k):
    if c == 0:
        return 0.0
    if n - c < k:
        return 1.0
    return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))

def compute_pass_metrics(
    data: List[Dict[str, Any]], k: int = 5
) -> Tuple[float, float]:
    """
    Compute pass@1 and pass@k for a list of graded items.

    Each element in *data* is expected to have a key ``graded_list`` whose value
    is a list of booleans, where ``True`` means the answer is correct.

    Parameters
    ----------
    data : list[dict]
        The dataset loaded from a JSON/JSONL file.
    k : int, default=5
        The cut-off for pass@k.

    Returns
    -------
    tuple[float, float]
        (overall_pass@1, overall_pass@k)
    """
    per_question: List[Dict[str, float]] = []

    for item in data:
        grades: List[bool] = item.get("graded_list", [])
        pass_at_1 = item.get("pass@1")
        c = sum(grades)
        n = len(grades)
        pass_k = pass_at_k(n, c, k)
        per_question.append({"pass@1": pass_at_1, f"pass@{k}": pass_k})

    total = len(per_question)
    if total == 0:
        return 0.0, 0.0

    overall_pass1 = sum(q["pass@1"] for q in per_question) / total
    overall_passk = sum(q[f"pass@{k}"] for q in per_question) / total
    return overall_pass1, overall_passk


def main() -> None:
    base_dir = "../results"  # Root directory containing model result folders
    k = 5
    summary_results: List[Dict[str, Any]] = []

    for model_name in os.listdir(base_dir):
        model_dir = os.path.join(base_dir, model_name)
        icpc_dir = os.path.join(model_dir, "ICPC")
        if not os.path.isdir(icpc_dir):
            continue

        # Search for JSON / JSONL files inside each model’s ICPC directory
        for filename in os.listdir(icpc_dir):
            if not filename.endswith((".json", ".jsonl")):
                continue

            file_path = os.path.join(icpc_dir, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                pass1, passk = compute_pass_metrics(data, k)
                summary_results.append(
                    {
                        "model": model_name,
                        "pass@1": pass1,
                        f"pass@{k}": passk,
                    }
                )
            except Exception as exc:  # pylint: disable=broad-except
                print(f"❌ Failed to process {file_path}: {exc}")

    # Write aggregated results to a JSON file
    output_path = "ICPC_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary_results, f, indent=2)

    print(f"✅ ICPC summary saved to {output_path}")


if __name__ == "__main__":
    main()
