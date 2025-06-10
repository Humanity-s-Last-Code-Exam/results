import json
import os
import numpy as np
from typing import Any, Dict, List, Tuple

MODEL_URLS = {
    "chatgpt-4o-latest": "https://platform.openai.com/docs/models/gpt-4o",
    "gpt-4o-2024-05-13": "https://platform.openai.com/docs/models/gpt-4o",
    "gpt-4o-mini": "https://openai.com/index/gpt-4o-mini-advancing-cost-efficient-intelligence/",
    "o1-mini": "https://openai.com/index/openai-o1-mini-advancing-cost-efficient-reasoning/",
    "o3-mini": "https://platform.openai.com/docs/models/o3-mini",
    "o4-mini": "https://platform.openai.com/docs/models/o4-mini",
    "claude-3.5-sonnet": "https://www.anthropic.com/news/claude-3-5-sonnet",
    "claude-3.7-sonnet": "https://www.anthropic.com/news/claude-3-7-sonnet",
    "claude-3.7-sonnet-thinking": "https://www.anthropic.com/news/claude-3-7-sonnet",
    "deepseek-r1": "https://api-docs.deepseek.com/news/news250120",
    "deepseek-v3": "https://api-docs.deepseek.com/news/news250325",
    "gemini-2.5-pro": "https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-pro",
}


def get_model_url(model_name: str) -> str:
    key = model_name.lower()
    if key in MODEL_URLS:
        return MODEL_URLS[key]
    for kw in (
        "gpt-4o-mini", "gpt-4o",
        "claude-3.5", "claude-3.7",
        "deepseek-r1", "deepseek-v3",
        "gemini-2.5-pro",
        "o1-mini", "o3-mini", "o4-mini"
    ):
        if kw in key:
            return next(v for k, v in MODEL_URLS.items() if kw in k)
    return ""


def pass_at_k(n: int, c: int, k: int) -> float:
    if c == 0:
        return 0.0
    if n - c < k:
        return 1.0
    return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))


def compute_pass_metrics(
    data: List[Dict[str, Any]], k: int = 5
) -> Tuple[float, float]:
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
    base_dir = "../results"
    k = 5
    summary_results: List[Dict[str, Any]] = []
    for model_name in os.listdir(base_dir):
        model_dir = os.path.join(base_dir, model_name)
        icpc_dir = os.path.join(model_dir, "ICPC")
        if not os.path.isdir(icpc_dir):
            continue
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
                        "Model": model_name,
                        "Pass@1": pass1,
                        f"Pass@{k}": passk,
                        "URL": get_model_url(model_name),
                    }
                )
            except Exception as exc:
                print(f"Failed to process {file_path}: {exc}")
    output_path = "ICPC_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary_results, f, indent=2, ensure_ascii=False)
    print(f"ICPC summary saved to {output_path}")


if __name__ == "__main__":
    main()
