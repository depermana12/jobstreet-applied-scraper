import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import os

EXPORT_DIR = "exports"


def _get_timestamp_filename(prefix: str, extension: str) -> str:
    """Generate timestamped filename"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.{extension}"

    os.makedirs(EXPORT_DIR, exist_ok=True)
    return os.path.join(EXPORT_DIR, filename)


def _clean_data_for_export(jobs_data):
    """Remove non-serializable elements from jobs data"""
    clean_data = []
    for job in jobs_data:
        # Remove WebElement and other non-serializable objects
        clean_job = {k: v for k, v in job.items() if k != "clickable_element"}
        clean_data.append(clean_job)
    return clean_data


def export_to_csv(jobs_data, filename="jobstreedt_jobs"):
    """Export jobs data to CSV file"""

    filename = _get_timestamp_filename(filename, "csv")
    clean_data = _clean_data_for_export(jobs_data)

    df = pd.DataFrame(clean_data)
    df.to_csv(filename, index=False, encoding="utf-8")

    print(f"CSV exported to: {filename}")
    return filename


def export_to_json(jobs_data, filename="jobstreedt_jobs"):
    """Export jobs data to JSON file"""

    filename = _get_timestamp_filename(filename, "json")
    clean_data = _clean_data_for_export(jobs_data)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, indent=2, ensure_ascii=False)

    print(f"JSON exported to: {filename}")


def export_to_excel(jobs_data, filename="jobstreedt_jobs"):
    """Export jobs data to Excel file"""

    filename = _get_timestamp_filename(filename, "xlsx")
    clean_data = _clean_data_for_export(jobs_data)

    df = pd.DataFrame(clean_data)
    df.to_excel(filename, index=False, engine="openpyxl")

    print(f"Excel exported to: {filename}")
    return filename
