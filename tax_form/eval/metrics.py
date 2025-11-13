"""Below everything is AI generated

I didn't want to write NER (as we have start, end, label, that's basically ner) metrics from scratch.

Well, as you can see below, there are no overlaps so it could have been just f1 with tuples (start, end, label) and only exact match.

Regarding prompting, I just asked to write f1 scorer for NER-like input and after that asked for micro/macro averaging to get more insights.
"""

from typing import List, Dict
from collections import defaultdict


def compute_ner_f1(
    predicted: List[Dict], ground_truth: List[Dict], match_type: str = "exact"
) -> Dict[str, float]:
    """
    Compute F1 score for NER with start, end, and label.

    Args:
        predicted: List of predictions with 'document_type', 'start_page', 'end_page'
        ground_truth: List of ground truth with 'document_type', 'start_page', 'end_page'
        match_type: 'exact' for exact boundary match, 'overlap' for any overlap

    Returns:
        Dict with precision, recall, f1, and per-label metrics
    """

    def entities_match(pred, true, match_type):
        """Check if two entities match based on match_type."""
        if pred["document_type"] != true["document_type"]:
            return False

        if match_type == "exact":
            return (
                pred["start_page"] == true["start_page"]
                and pred["end_page"] == true["end_page"]
            )
        elif match_type == "overlap":
            # Check if there's any overlap in page ranges
            return not (
                pred["end_page"] < true["start_page"]
                or pred["start_page"] > true["end_page"]
            )
        else:
            raise ValueError(f"Unknown match_type: {match_type}")

    # Track matches
    true_positives = 0
    matched_true = set()
    matched_pred = set()

    # For each prediction, find if there's a matching ground truth
    for pred_idx, pred in enumerate(predicted):
        for true_idx, true in enumerate(ground_truth):
            if true_idx not in matched_true and entities_match(pred, true, match_type):
                true_positives += 1
                matched_true.add(true_idx)
                matched_pred.add(pred_idx)
                break

    false_positives = len(predicted) - true_positives
    false_negatives = len(ground_truth) - true_positives

    # Compute metrics
    precision = true_positives / len(predicted) if predicted else 0.0
    recall = true_positives / len(ground_truth) if ground_truth else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "num_predicted": len(predicted),
        "num_ground_truth": len(ground_truth),
    }


def compute_per_label_metrics(
    predicted: List[Dict], ground_truth: List[Dict], match_type: str = "exact"
) -> Dict[str, Dict[str, float]]:
    """
    Compute per-label F1 scores.

    Returns:
        Dict mapping document_type to its metrics
    """
    # Group by document type
    pred_by_type = defaultdict(list)
    true_by_type = defaultdict(list)

    for pred in predicted:
        pred_by_type[pred["document_type"]].append(pred)

    for true in ground_truth:
        true_by_type[true["document_type"]].append(true)

    # Get all unique labels
    all_labels = set(pred_by_type.keys()) | set(true_by_type.keys())

    per_label_metrics = {}
    for label in all_labels:
        metrics = compute_ner_f1(
            pred_by_type[label], true_by_type[label], match_type=match_type
        )
        per_label_metrics[label] = metrics

    return per_label_metrics


def aggregate_metrics_across_documents(
    pred_dict: Dict[str, List[Dict]],
    gt_dict: Dict[str, List[Dict]],
    match_type: str = "exact",
    aggregation: str = "micro",
) -> Dict[str, float]:
    """
    Aggregate metrics across all documents.

    Args:
        pred_dict: Dict mapping document name to predictions
        gt_dict: Dict mapping document name to ground truth
        match_type: 'exact' or 'overlap'
        aggregation: 'micro' for overall (sum all TP/FP/FN),
                     'macro' for mean of per-document scores

    Returns:
        Aggregated metrics
    """
    if aggregation == "micro":
        # Micro-averaging: sum all TP/FP/FN across documents, then compute metrics
        total_tp = 0
        total_fp = 0
        total_fn = 0

        for doc_name in gt_dict.keys():
            pred = pred_dict.get(doc_name, [])
            true = gt_dict[doc_name]

            metrics = compute_ner_f1(pred, true, match_type=match_type)
            total_tp += metrics["true_positives"]
            total_fp += metrics["false_positives"]
            total_fn += metrics["false_negatives"]

        precision = (
            total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
        )
        recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "true_positives": total_tp,
            "false_positives": total_fp,
            "false_negatives": total_fn,
            "aggregation": "micro",
        }

    elif aggregation == "macro":
        # Macro-averaging: compute metrics per document, then average
        precisions = []
        recalls = []
        f1s = []

        for doc_name in gt_dict.keys():
            pred = pred_dict.get(doc_name, [])
            true = gt_dict[doc_name]

            metrics = compute_ner_f1(pred, true, match_type=match_type)
            precisions.append(metrics["precision"])
            recalls.append(metrics["recall"])
            f1s.append(metrics["f1"])

        return {
            "precision": sum(precisions) / len(precisions) if precisions else 0.0,
            "recall": sum(recalls) / len(recalls) if recalls else 0.0,
            "f1": sum(f1s) / len(f1s) if f1s else 0.0,
            "num_documents": len(gt_dict),
            "aggregation": "macro",
        }

    else:
        raise ValueError(
            f"Unknown aggregation type: {aggregation}. Use 'micro' or 'macro'."
        )
