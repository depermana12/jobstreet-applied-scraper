from scraper import JobStreetScraper
from configs import init_logging
from cli import cli_scraper_parser
from helpers import max_validation, email_validation
from exporter import export_to


def main():
    args = cli_scraper_parser()
    email = args.email

    while not email or not email_validation(email):
        if email and not email_validation(email):
            print("Invalid email format. Please try again.")
        email = input("Enter your Jobstreet email: ").strip()
    max_pages = max_validation(args.max)
    export_type = args.export

    init_logging(log_console=args.verbose)

    scraper = JobStreetScraper(
        email=email,
    )

    try:
        jobs = scraper.scrape_all_jobs(max_pages=max_pages)
        export_to(export_type, jobs, filename="jobstreet_jobs")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        scraper.close_browser()
        print("Browser closed.")


if __name__ == "__main__":
    main()
