from scraper import JobStreetScraper
from helpers import email_validation
from cli import cli_scraper_parser
from rich.console import Console
from configs import init_logging
from exporter import export_to
from rich.panel import Panel


def main():
    console = Console()
    args = cli_scraper_parser()
    email = args.email

    total_jobs = 0
    total_elapsed = 0
    completed_at = "N/A"
    export_data = "N/A"

    while not email or not email_validation(email):
        if email and not email_validation(email):
            console.print("Invalid email format. Please try again.")
        email = console.input("Enter your Jobstreet email: ").strip()

    sort_by = args.sort == "desc"
    init_logging(log_console=args.verbose)

    scraper = JobStreetScraper(
        email=email,
        browser=args.browser,
        headless=args.headless,
    )

    try:
        jobs = scraper.scrape_all_jobs(reverse=sort_by)
        jobs_data = jobs["jobs_data"]
        total_jobs = jobs["total_jobs"]
        total_elapsed = jobs["total_elapsed"]
        completed_at = jobs["scraping_completed_at"]

        export_data = export_to(args.format, jobs_data, filename="jobstreet_jobs")

        console.print(
            Panel.fit(
                f"[bold green]🎉 JobStreet Scraping Summary[/]\n\n"
                f"[cyan]📊 Jobs collected:[/] {total_jobs}\n"
                f"[magenta]⏱️ Total time:[/] {total_elapsed:.2f} seconds\n"
                f"[blue]📝 Export format:[/] {args.format}\n"
                f"[yellow]📁 Exported to:[/] {export_data}\n"
                f"[green]✅ Status:[/] Completed successfully\n"
                f"[green]📅 Completed at:[/] {completed_at}\n",
                title="[bold blue]JobStreet Scraper Results[/]",
                border_style="green",
            )
        )

    except Exception as e:
        console.print(f"[bold red]An error occurred:[/] {e}")
        console.print(
            Panel.fit(
                f"[bold red]❌ Scraping Failed[/]\n\n"
                f"[yellow]📊 Jobs collected:[/] {total_jobs}\n"
                f"[red]💥 Error:[/] {str(e)}\n"
                f"[dim]Check logs for more details[/]",
                title="[bold red]Error Summary[/]",
                border_style="red",
            )
        )
    finally:
        scraper.close_browser()
        console.print("[dim]Browser closed.[/]")


if __name__ == "__main__":
    main()
