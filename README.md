# JobStreet Applied Jobs Scraper

A Python tool to **scrape your applied jobs from JobStreet** and export the data to `json` or `csv`.  
This project uses Selenium to automate browser actions.

---

## Get This Repo & Installation

### **Requirements:**

- Python 3.11 or higher
- [Poetry](https://python-poetry.org/docs/#installation) package manager
- browsers:
  - Firefox (latest version)
  - Chrome (latest version)
- Windows, macOS, or Linux

## **Installation Methods:**

1. **Install Poetry** (if not already installed):

   ```sh
   # Windows (PowerShell)
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

   # macOS/Linux
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Clone this repository:**

   ```sh
   git clone https://github.com/depermana12/jobstreet-applied-scraper.git
   cd jobstreet-applied-scraper
   ```

3. **Install dependencies with Poetry:**

   ```sh
   # Install all dependencies
   poetry install
   ```

---

## Usage

### **Poetry Usage:**

```sh
# Run with Poetry
poetry run python main.py -e your_email@example.com
```

### **Command Line Arguments:**

#### **Required:**

- `-e, --email`: Your JobStreet email address

#### **Browser Selection:**

- `--chrome`: Use Chrome browser
- `--firefox`: Use Firefox browser
- **Default:** Firefox

#### **Browser Mode:**

- `--headless`: Run browser without GUI (background mode)
- **Default:** GUI mode (browser window visible)

#### **Scraping Order:**

- `--asc`: Scrape jobs in ascending order (newest first) -
- `--desc`: Scrape jobs in descending order (oldest first, chronological)
- **Default:** `--desc` (oldest first)

#### **Export Format:**

- `-f, --format`: Export format - choices: `json`, `csv`, `all`
  - `json`: Export to JSON file
  - `csv`: Export to CSV file
  - `all`: Export both JSON and CSV files
- **Default:** `all`

#### **Logging:**

- `-v, --verbose`: Enable detailed logging to console
- **Default:** disabled (just look the log file)

### **Example Commands:**

```sh
# only put required email argument
# the rest options are default to firefox, gui, descending order, and all export json and csv
poetry run python main.py -e "user@example.com"

# Chrome browser, newest first, headless mode, CSV export
poetry run python main.py -e "user@example.com" --chrome --headless --asc -f csv

# Firefox browser, newest first, headless mode, JSON export
poetry run python main.py -e "user@example.com" --firefox --asc --headless -f json
```

---

## Important Notes

- Jobstreet limits to only show 90 applied jobs history, so the scraper will only retrieve up to that limit. 5 Pages, each page 1-4 is 20 cards and page 5 is 10 cards.
- "N/A" in the output means "Not Available" for fields that are optional like salary
- `job_posted_date` that is "30+ days ago" means expired, also indicating in the `is_expired` field
- Application status on csv format already normalized to show only latest update
- If you encounter Chrome errors in the terminal, just ignore them - they're often just warnings
- Headless mode is faster but may have issues with OTP sometimes

---

## Example Output Data

Here's an example of the JSON output:

```json
[
  {
    "id": 1,
    "job_platform": "JobStreet",
    "data_retrieved_at": "02-06-2025 15:07:38",
    "job_title": "Senior Software Engineer (TypeScript/React)",
    "company_name": "PT Tech Pojok Cafe",
    "job_location": "Jakarta Selatan, Jakarta Raya",
    "job_classification": "Teknologi Informasi & Komunikasi",
    "job_type": "Full time",
    "job_posted_date": "30+ days ago",
    "salary_range": "Rp 15.000.000 - Rp 20.000.000",
    "job_url": "https://example.com/job/82532982",
    "resume": "bismillah-my-cv-ver3.1-final-bgt.pdf",
    "cover_letter": "Tidak ada surat lamaran terkirim",
    "total_applicants": 163,
    "is_expired": true,
    "application_status": [
      {
        "status": "Dilamar di JobStreet",
        "updated_at": "5 Mar 2025"
      },
      {
        "status": "Dilihat oleh perusahaan",
        "updated_at": "5 Mar 2025"
      },
      {
        "status": "Kemungkinan tidak dilanjutkan",
        "updated_at": "7 Mar 2025"
      }
    ]
  }
]
```

## Scraping Flow

1. **Browser Launch:**

   The scraper launches your chosen browser (Chrome/Firefox) with optimized settings to avoid detection issues.  
   **You will need to log in to JobStreet** as the scraper uses a clean browser session.

2. **Login & OTP:**

   JobStreet login requires an OTP sent to your email.

   - The script opens the browser and navigates to the JobStreet login page
   - The script automatically fills in your email address
   - **Enter OTP code manually** when prompted in the terminal
   - The script will wait for you to complete the login process

3. **Scraping:**

   - Automatically navigates to your "Applied Jobs" page
   - Scrapes all available job details:
     - Job title, company name, location
     - Salary range, job classification, job type
     - Application status, posting date
     - Resume and cover letter used
     - Total applicants count
   - **Processes ALL pages automatically** (JobStreet shows max ~90 jobs)

4. **Export:**
   - Results are exported to your chosen format (`json` or `csv`)
   - Files are saved in the `exports/` directory with timestamped filenames

---

## Project Structure

```
JobstreetScrapper/
│
├── pyproject.toml       # Poetry configuration & dependencies
├── poetry.lock          # Locked dependency versions
├── main.py              # Entry point with CLI integration
├── scraper.py           # Core scraping logic
├── exporter.py          # Export functions (JSON/CSV)
├── configs.py           # Browser configuration and driver setup
├── cli.py               # Command line argument parsing
├── helpers.py           # Utility functions (email validation, etc.)
├── exports/             # Output files (auto-created)
├── logs/                # Log files (auto-created)
└── README.md            # This file
```

---

## Tech Stack

- **Python 3.11+**
- **Firefox/Chrome**
- **Poetry**: Dependency management and packaging
- **Selenium**: Web browser automation
- **Rich**: Beautiful terminal output and progress bars

---

## Disclaimer

- This tool is for **personal use** and **learning purposes** only
- Do not use for commercial scraping or violate JobStreet's terms of service
- The scraper may break if JobStreet changes its website structure
- Ensure your browser drivers are up to date for compatibility
- Use responsibly and respect rate limits
