"""
Evaluate RAG pipeline quality using RAGAS metrics.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

from datasets import Dataset
from dotenv import load_dotenv

load_dotenv()

RESULTS_DIR = Path("docs")


def _build_ragas_dataset(samples: list[dict]):
    """
    Convert our sample dicts into a RAGAS-compatible Dataset.

    Each sample dict must have:
        question          : str
        answer            : str
        contexts          : list[str]   (retrieved chunk texts)
        ground_truth      : str
    """
    from datasets import Dataset  

    return Dataset.from_list(samples)


def evaluate_rag(
    samples: list[dict],
    metrics: list[str] | None = None,
    save_results: bool = True,
) -> dict:
    """
    Run RAGAS evaluation over a list of QA samples.

    Parameters
    ----------
    samples : list of dicts, each with keys:
                question, answer, contexts (list[str]), ground_truth
    metrics : which RAGAS metrics to run — defaults to all four core metrics
    save_results : if True, persist scores to docs/evaluation_results.json

    Returns
    -------
    {
        "scores": { metric_name: float, … },
        "timestamp": "...",
        "num_samples": int
    }
    """
    try:
        from ragas import evaluate as ragas_evaluate           
        from ragas.metrics import (                            
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        )
    except ImportError:
        raise ImportError(
            "RAGAS is not installed. Run: pip install ragas datasets"
        )

    # ── Select metrics
    all_metrics = {
        "faithfulness":       faithfulness,
        "answer_relevancy":   answer_relevancy,
        "context_precision":  context_precision,
        "context_recall":     context_recall,
    }

    selected_names   = metrics or list(all_metrics.keys())
    selected_metrics = [all_metrics[m] for m in selected_names if m in all_metrics]

    if not selected_metrics:
        raise ValueError(f"No valid metrics selected. Choose from: {list(all_metrics)}")

    # ── Build dataset
    print(f"🔬 Running RAGAS evaluation on {len(samples)} samples …")
    dataset = _build_ragas_dataset(samples)

    # ── Evaluate
    result = ragas_evaluate(dataset, metrics=selected_metrics)

    scores: dict[str, float] = {}
    for metric_name in selected_names:
        val = result.get(metric_name)
        if val is not None:
            scores[metric_name] = round(float(val), 4)

    output = {
        "scores":      scores,
        "timestamp":   datetime.utcnow().isoformat() + "Z",
        "num_samples": len(samples),
        "metrics_run": selected_names,
    }

    
    if save_results:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        results_file = RESULTS_DIR / "evaluation_results.json"

        # Append to existing results if file exists
        history: list[dict] = []
        if results_file.exists():
            try:
                history = json.loads(results_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                history = []

        history.append(output)
        results_file.write_text(
            json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"✅ Results saved → {results_file.resolve()}")

    _print_scores(scores)
    return output


def _print_scores(scores: dict[str, float]) -> None:
    print("\n── RAGAS Evaluation Results ──────────────────")
    for metric, score in scores.items():
        bar   = "█" * int(score * 20)
        space = "░" * (20 - int(score * 20))
        print(f"  {metric:<22} {bar}{space}  {score:.4f}")
    print("──────────────────────────────────────────────\n")


def load_evaluation_history() -> list[dict]:
    """Return all previously saved evaluation runs."""
    results_file = RESULTS_DIR / "evaluation_results.json"
    if not results_file.exists():
        return []
    return json.loads(results_file.read_text(encoding="utf-8"))


if __name__ == "__main__":
    dummy_samples = [
        {
            "question":    "What is the patient's chief complaint?",
            "answer":      "The patient presents with shortness of breath.",
            "contexts":    [
                "Patient presented with shortness of breath and mild chest pain.",
                "Vitals: BP 140/90, HR 88, RR 18.",
            ],
            "ground_truth": "Shortness of breath and chest pain.",
        },
        {
            "question":    "What medication was prescribed?",
            "answer":      "Loratadine 10 mg daily was prescribed.",
            "contexts":    [
                "Assessment: Seasonal allergic rhinitis. Plan: Loratadine 10 mg daily.",
            ],
            "ground_truth": "Loratadine 10 mg daily.",
        },
    ]

    print(" Running with dummy samples — requires OPENAI_API_KEY in .env")
    print(" Running with dummy samples — requires OPENAI_API_KEY in .env")

    result = evaluate_rag(dummy_samples)
    print("Output dict:", result)