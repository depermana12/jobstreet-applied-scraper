import argparse


def cli_scraper_parser():
    parser = argparse.ArgumentParser(
        prog="Jobstreet scraper",
        description="Scrape applied jobs from JobStreet and export it to json or csv",
    )

    parser.add_argument("-e", "--email", type=str, help="Your jobstreet email address")

    browser_group = parser.add_mutually_exclusive_group()
    browser_group.add_argument(
        "--chrome",
        action="store_const",
        dest="browser",
        const="chrome",
        help="Use Chrome browser",
    )
    browser_group.add_argument(
        "--firefox",
        action="store_const",
        dest="browser",
        const="firefox",
        help="Use Firefox browser",
    )
    parser.set_defaults(browser="firefox")

    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser without a GUI (background mode)",
    )

    sorting_group = parser.add_mutually_exclusive_group()
    sorting_group.add_argument(
        "--asc",
        action="store_const",
        dest="sort",
        const="asc",
        help="Scrape jobs in ascending order, chronologically (newest first)",
    )
    sorting_group.add_argument(
        "--desc",
        action="store_const",
        dest="sort",
        const="desc",
        help="Scrape jobs in descending order, chronologically (oldest first)",
    )
    parser.set_defaults(sort="asc")

    parser.add_argument(
        "-f",
        "--format",
        type=str,
        choices=["json", "csv"],
        default="json",
        help="Export format for the scraped data (default: %(default)s)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable logging to console",
    )

    return parser.parse_args()
