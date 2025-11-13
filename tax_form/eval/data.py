import json


def load_predicted_jsonl(path: str):
    """Process output logs from classification step."""
    with open(path, "r") as f:
        res = [json.loads(fline) for fline in f.readlines()]
    res = [x for x in res if "classified_form" in x]
    res = [x["classified_form"] for x in res]
    # to comply with the target format
    # it could have been done in the classification step, but whatever, it's too late
    for x in res:
        x["document_type"] = x["form_type"]
        del x["form_type"]
        x["start_page"] += 1  # to 1-indexed
        x["end_page"] += 1  # to 1-indexed
    return res


def load_ground_truth_json(path: str):
    """Load ground truth data from JSON file."""
    with open(path, "r") as f:
        res = json.load(f)
    return res
