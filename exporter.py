from datetime import datetime
from typing import List, Dict
import json
import csv
import os

EXPORT_DIR = "exports"


def _get_timestamp_filename(prefix: str, extension: str) -> str:
    """Generate timestamped filename"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.{extension}"

    os.makedirs(EXPORT_DIR, exist_ok=True)
    return os.path.join(EXPORT_DIR, filename)


def _normalize_application_status(job_data: List[Dict]) -> List[Dict]:
    normalize_data = []

    for job in job_data:
        job_copy = job.copy()
        results = {
            "status": "N/A",
            "updated_at": "N/A",
            "job_applied_at": "N/A",
        }

        if "application_status" in job_copy:
            status_data = job_copy["application_status"]

            if isinstance(status_data, list) and len(status_data) > 0:
                first_status = status_data[0]
                if isinstance(first_status, dict):
                    results["job_applied_at"] = first_status.get("updated_at", "N/A")
                else:
                    results["job_applied_at"] = "N/A"

                latest_status = status_data[-1]
                if isinstance(latest_status, dict):
                    results["status"] = latest_status.get("status", "N/A")
                    results["updated_at"] = latest_status.get("updated_at", "N/A")
                else:
                    results["status"] = str(latest_status)

            del job_copy["application_status"]

        normalize_data.append({**job_copy, **results})

    return normalize_data


def _export_to_csv(jobs_data: List[Dict], filename="jobstreet_jobs") -> str:
    """Export jobs data to CSV file"""
    filename = _get_timestamp_filename(filename, "csv")

    if not jobs_data:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["No Data. Check log for details."])
        return filename

    normalized_jobs = _normalize_application_status(jobs_data)

    fieldnames = set()
    for job in normalized_jobs:
        fieldnames.update(job.keys())
    fieldnames = sorted(list(fieldnames))

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(normalized_jobs)

    return filename


def _export_to_json(jobs_data: List[Dict], filename="jobstreet_jobs") -> str:
    """Export jobs data to JSON file"""
    filename = _get_timestamp_filename(filename, "json")

    if not jobs_data:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(
                {"message": "No Data. Check log for details."},
                f,
                indent=2,
                ensure_ascii=False,
            )
        return filename

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(jobs_data, f, indent=2, ensure_ascii=False)

    return filename


def export_to(types: str, jobs_data: List[Dict], filename="jobstreet_jobs") -> str:

    match types.lower():
        case "json":
            return _export_to_json(jobs_data, filename)
        case "csv":
            return _export_to_csv(jobs_data, filename)
        case "all":
            csv_file = _export_to_csv(jobs_data, filename)
            json_file = _export_to_json(jobs_data, filename)
            return f"CSV: {csv_file}\nJSON: {json_file}"
        case _:
            print("No types selected, default to json")
            return _export_to_json(jobs_data, filename)
