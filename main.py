from scraper import JobStreetScraper
from exporter import export_to_json
from configs import configurations


def main():
    selected_profile = configurations[
        "profile_name"
    ]  # Get profile name from configurations
    scraper = JobStreetScraper(use_profile=selected_profile)

    try:
        jobs = scraper.scrape_all_jobs(max_pages=2)
        export_to_json(jobs, filename="jobstreet_jobs")
        print(f"Scraping completed. Total jobs scraped: {len(jobs)}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        scraper.driver.quit()
        print("Driver closed.")


if __name__ == "__main__":
    main()
