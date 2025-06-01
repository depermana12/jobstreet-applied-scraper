import argparse


def cli_scraper_parser():
    parser = argparse.ArgumentParser(
        prog="Jobstreet scraper",
        description="Scrape applied jobs from JobStreet and export it to json, csv, excell",
    )

    parser.add_argument("-e", "--email", type=str, help="Your jobstreet email address")

    parser.add_argument(
        "-m",
        "--max",
        type=str,
        default="1",
        help="Number of pages to scrap. use --all to scrape all the available page",
    )

    parser.add_argument(
        "-x",
        "--export",
        type=str,
        choices=["json", "csv", "excel"],
        default="json",
        help="Export format for the scraped data",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable logging to console",
    )

    return parser.parse_args()
