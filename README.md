# JobStreet Applied Jobs Scraper

A Python tool to **scrape your applied jobs from JobStreet** and export the data to `json` or `csv`.  
This project uses Selenium to automate browser actions and pandas for data export.

---

## Get This Repo & Installation

1. **Requirements:**

   - Python 3.10 or higher
   - browsers:
     - Firefox (latest version)
     - Chrome (latest version)
   - Windows, macOS, or Linux

2. **Clone this repository:**

   ```sh
   git clone https://github.com/depermana12/jobstreet-applied-scraper.git

   cd jobstreet-applied-scraper
   ```

3. **Install and activate a virtual environment:**

   ```sh
   python -m venv venv # create a virtual environment

   venv\Scripts\activate # activate venv on windows cmd

   venv\Scripts\activate.ps1 # activate venv on windows powershell

   source venv/bin/activate # activate venv on macOS/Linux
   ```

   if you are using vscode, you can create venv by pressing `Ctrl + Shift + P` and type `Python: Create Environment` then select `venv` as the environment type.

4. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

---

## Usage

Run the scraper from the project directory using the command line:

```sh
python main.py -e your_email@example.com --chrome --desc -f json
```

### **Command Line Arguments:**

#### **Required:**

- `-e, --email`: Your JobStreet email address

#### **Browser Selection:**

- `--chrome`: Use Chrome browser
- `--firefox`: Use Firefox browser
- **Default:** Firefox if neither specified

#### **Browser Mode:**

- `--headless`: Run browser without GUI (background mode)
- **Default:** GUI mode (browser window visible)

#### **Scraping Order:**

- `--asc`: Scrape jobs in ascending order (newest first) - **Default**
- `--desc`: Scrape jobs in descending order (oldest first, chronological)

#### **Export Format:**

- `-f, --format`: Export format - choices: `json`, `csv`
- **Default:** `json`

#### **Logging:**

- `-v, --verbose`: Enable detailed logging to console
- **Default:** disabled (just look the log file)

### **Example Commands:**

```sh
# Basic usage with defaults (Firefox, newest first, JSON)
python main.py -e "user@example.com"

# Chrome browser, oldest first, CSV export
python main.py -e "user@example.com" --chrome --desc -f csv

# Chrome browser, newest first, headless mode, oldest first, CSV export
python main.py -e "user@example.com" --chrome --headless --desc -f csv

# Firefox headless mode, newest first order, JSON export
python main.py -e "user@example.com" --firefox --headless
```

If you omit `--email`, you will be prompted to enter it interactively.

### Important Notes

If you encounter chrome error in the terminal, just ignore it, it is just a warning from selenium about the browser version, you can ignore it, because the scraper will still work.

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
  },
  ...
  ...
  ...
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
   - Respects rate limiting to avoid being blocked

4. **Export:**
   - Results are exported to your chosen format (`json` or `csv`)
   - Files are saved in the `exports/` directory with timestamped filenames

---

## Troubleshooting

### **Common Issues:**

1. **OTP not received in headless mode:**

   ```sh
   # Use non-headless mode for login
   python main.py -e "user@example.com" --chrome
   ```

---

## Project Structure

```
JobstreetScrapper/
│
├── main.py           # Entry point with CLI integration
├── scraper.py        # Core scraping logic
├── exporter.py       # Export functions (JSON/CSV)
├── configs.py        # Browser configuration and driver setup
├── cli.py            # Command line argument parsing
├── helpers.py        # Utility functions (email validation, etc.)
├── requirements.txt  # Python dependencies
└── exports/          # Output files (auto-created)
```

---

## Disclaimer

- This tool is for **personal use** and **learning purposes** only
- Do not use for commercial scraping or violate JobStreet's terms of service
- The scraper may break if JobStreet changes its website structure
- Ensure your browser drivers are up to date for compatibility
- Use responsibly and respect rate limits

---
