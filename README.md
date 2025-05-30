# JobStreet Applied Jobs Scraper

A Python tool to **scrape your applied jobs from JobStreet** and export the data to JSON, CSV, or Excel.  
This project uses Selenium to automate browser actions and pandas for data export.

---

## Get This Repo & Installation

1. **Requirements:**

   - Python 3.10 or higher
   - Firefox browser latest version
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

4. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

---

## Usage

Run the scraper from the project directory using the command line:

```sh
python main.py --email "your_email@example.com" --max 1 --export csv
```

**Arguments:**

- `--email` or `-e`: Your JobStreet email address (required)
- `--max` or `-m`: Number of pages to scrape (`1`, `2`, ..., or `all` for all available pages)
- `--export` or `-x`: Export format (`json`, `csv`, or `excel`)

If you omit `--email`, you will be prompted to enter it interactively.

---

## Scraping Flow

1. **Clean Firefox Profile:**

   The scraper launches Firefox with a clean profile to avoid session issues.  
   **You will need to log in to JobStreet** as if on a new browser, that is why you need to enter your email in cli arguments

2. **Login & OTP:**

   Jobstreet login requires an OTP sent to your email.

   - The script will open Firefox and navigate to the JobStreet login page.
   - The script will handle putting email automatically in the login form.
   - Enter OTP code manually when prompted in the terminal.

3. **Scraping:**

   - The script navigates to your "Applied Jobs" page.
   - It scrapes job details (title, company, location, salary, status, resume, cover letter, applicants, etc.) for each job card.
   - It continues to the next page until the specified max or all jobs are scraped.

4. **Export:**
   - The results are exported to the format you choose (`json`, `csv`, or `excel`) in the `exports/` directory with a timestamped filename.

---

## Project Structure

```
JobstreetScrapper/
│
├── main.py           # Entry point
├── scraper.py        # Scraper logic
├── exporter.py       # Export functions
├── configs.py        # Configuration and driver setup
├── cli.py            # CLI argument parsing
├── requirements.txt  # Python dependencies
└── exports/          # Output files (auto-created)
```

---

## Disclaimer

- This tool is for **personal use** and **learning purposes**. Do not use it for commercial scraping or violate JobStreet's terms of service.
- The scraper may break if JobStreet changes its website structure or login flow.
- If you encounter issues with browser automation, ensure your browser and GeckoDriver versions are compatible.

---
