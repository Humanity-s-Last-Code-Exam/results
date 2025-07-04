import os
import json
import numpy as np
from collections import defaultdict


def pass_at_k(n, c, k):
    if c == 0:
        return 0.0
    if n - c < k:
        return 1.0
    return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))


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


def analyze_submissions(data):
    composite_problems = {
        "A. Crayfish scrivener (IOI 2012 day 1)": ['A1', 'A2', 'A3', 'A4', 'A5']
    }
    submissions_by_problem = defaultdict(list)
    for submission in data:
        problem_title = submission['problem_title']
        date = submission['date']
        problem_index = submission['problem_index']
        if date == "IOI 2012 day 1" and problem_index.startswith('A'):
            problem_key = "A. Crayfish scrivener (IOI 2012 day 1)"
        else:
            problem_key = f"{problem_title} ({date})"
        submissions_by_problem[problem_key].append(submission)
    overall_stats = {
        "pass_at_1_sum": 0.0,
        "pass_at_5_sum": 0.0,
        "avg_points_sum": 0.0,
        "problem_count": 0,
        "solved_problems": 0
    }
    for problem_key, submissions in submissions_by_problem.items():
        overall_stats["problem_count"] += 1
        if problem_key in composite_problems:
            sub_tasks = composite_problems[problem_key]
            sorted_submissions = sorted(submissions, key=lambda x: x.get('original_record_id', 0))
            attempts = []
            current_attempt = defaultdict(float)
            required_sub_tasks = set(sub_tasks)
            for sub in sorted_submissions:
                subtask = sub['problem_index']
                if subtask not in sub_tasks:
                    continue
                points = float(sub['points']) if sub.get('points') is not None else 0.0
                current_attempt[subtask] = points
                if set(current_attempt.keys()) == required_sub_tasks:
                    total_points = sum(current_attempt.values())
                    attempts.append(total_points)
                    current_attempt = defaultdict(float)
            n = len(attempts)
            c = sum(1 for total in attempts if total == 100.0)
        else:
            valid_submissions = [float(sub['points']) if sub.get('points') is not None else 0.0
                                 for sub in submissions]
            n = len(valid_submissions)
            c = sum(1 for points in valid_submissions if points == 100.0)
        pass_at_1 = pass_at_k(n, c, 1) if n > 0 else 0.0
        pass_at_5 = pass_at_k(n, c, 5) if n > 0 else 0.0
        avg_points = sum(attempts if problem_key in composite_problems else valid_submissions) / n if n > 0 else 0.0
        overall_stats["pass_at_1_sum"] += pass_at_1
        overall_stats["pass_at_5_sum"] += pass_at_5
        overall_stats["avg_points_sum"] += avg_points
        if c > 0:
            overall_stats["solved_problems"] += 1
    problem_count = overall_stats["problem_count"]
    return {
        "pass@1": overall_stats["pass_at_1_sum"] / problem_count if problem_count > 0 else 0.0,
        "pass@5": overall_stats["pass_at_5_sum"] / problem_count if problem_count > 0 else 0.0,
        "avg_points": overall_stats["avg_points_sum"] / problem_count if problem_count > 0 else 0.0,
    }


def main():
    base_dir = '../results'
    output_summary = []
    for model_dir in os.listdir(base_dir):
        model_path = os.path.join(base_dir, model_dir)
        ioi_file_path = os.path.join(model_path, 'IOI')
        if not os.path.isdir(ioi_file_path):
            continue
        for file in os.listdir(ioi_file_path):
            if file.endswith(('.json', '.jsonl')):
                full_path = os.path.join(ioi_file_path, file)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    stats = analyze_submissions(data)
                    output_summary.append({
                        "Model": model_dir,
                        "Pass@1": stats["pass@1"],
                        "Pass@5": stats["pass@5"],
                        "Average Points": stats["avg_points"],
                        "URL": get_model_url(model_dir)
                    })
                except Exception as e:
                    print(f"Failed to process {full_path}: {e}")
    with open('IOI_results.json', 'w', encoding='utf-8') as f:
        json.dump(output_summary, f, indent=2, ensure_ascii=False)
    print("Summary saved to IOI_results.json")


if __name__ == "__main__":
    main()
