from datetime import datetime
from typing import List, Dict
import pandas as pd
import json
import os

EXPORT_DIR = "exports"


def _get_timestamp_filename(prefix: str, extension: str) -> str:
    """Generate timestamped filename"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.{extension}"

    os.makedirs(EXPORT_DIR, exist_ok=True)
    return os.path.join(EXPORT_DIR, filename)


def _export_to_csv(jobs_data: List[Dict], filename="jobstreedt_jobs") -> str:
    """Export jobs data to CSV file"""
    filename = _get_timestamp_filename(filename, "csv")

    df = pd.DataFrame(jobs_data)
    df.to_csv(filename, index=False, encoding="utf-8")

    return filename


def _export_to_json(jobs_data: List[Dict], filename="jobstreedt_jobs") -> str:
    """Export jobs data to JSON file"""
    filename = _get_timestamp_filename(filename, "json")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(jobs_data, f, indent=2, ensure_ascii=False)

    return filename


def export_to(types: str, jobs_data: List[Dict], filename="jobstreet_jobs") -> str:

    match types.lower():
        case "json":
            return _export_to_json(jobs_data, filename)
        case "csv":
            return _export_to_csv(jobs_data, filename)
        case _:
            print("No types selected, default to json")
            return _export_to_json(jobs_data, filename)
