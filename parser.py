def parse_job(text):
    import re
    from datetime import datetime

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    data = {
        "scraped_at": datetime.now().isoformat(),
        "title": "n/a",
        "company": "n/a",
        "location": "n/a",
        "salary": "n/a",
        "status": "n/a",
        "date_applied": "n/a",
        "cv": "n/a",
        "cover_letter": "n/a",
        "people_applied": "n/a",
    }

    def find_idx(keyword):
        for i, line in enumerate(lines):
            if keyword in line:
                return i
        return None

    lamaran_idx = find_idx("Lamaran untuk")
    if lamaran_idx is not None:
        fields = ["title", "company", "location"]
        for offset, field in enumerate(fields, start=1):
            if lamaran_idx + offset < len(lines):
                data[field] = lines[lamaran_idx + offset]
        if lamaran_idx + 4 < len(lines) and "Rp" in lines[lamaran_idx + 4]:
            data["salary"] = lines[lamaran_idx + 4]

    status_idx = find_idx("Status lamaran")
    if status_idx is not None:
        if status_idx + 1 < len(lines):
            data["status"] = lines[status_idx + 1]
        if status_idx + 2 < len(lines):
            months = [
                "Januari",
                "Februari",
                "Maret",
                "April",
                "Mei",
                "Juni",
                "Juli",
                "Agustus",
                "September",
                "Oktober",
                "November",
                "Desember",
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ]
            if any(month in lines[status_idx + 2] for month in months):
                data["date_applied"] = lines[status_idx + 2]

    dokumen_idx = find_idx("Dokumen terkirim")
    if dokumen_idx is not None:
        # Look for the first .pdf after dokumen_idx
        for offset in range(1, 4):
            idx = dokumen_idx + offset
            if idx < len(lines) and lines[idx].lower().endswith(".pdf"):
                data["cv"] = lines[idx]
                # Try to get cover letter (next line, if not "Tidak ada surat lamaran terkirim")
                if idx + 1 < len(lines):
                    next_line = lines[idx + 1]
                    if "tidak ada surat lamaran" not in next_line.lower():
                        data["cover_letter"] = next_line
                break

    perbandingan_idx = find_idx("Perbandingan dengan kamu")
    if perbandingan_idx is not None and perbandingan_idx + 1 < len(lines):
        match = re.search(r"(\d+)", lines[perbandingan_idx + 1])
        if match:
            data["people_applied"] = match.group(1)

    return data
