from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from configs import init_driver, configurations
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from rich.console import Console
from rich.status import Status
import logging
import time
import re


class JobStreetScraper:
    def __init__(self, email, browser="chrome", headless=False):
        self.email = email
        self.driver = None
        self.browser = browser
        self.headless = headless
        self._initialize_driver()
        self.base_url = configurations["base_url"]
        self.LONG_WAIT = configurations["default_wait"]
        self.SHORT_WAIT = configurations["short_wait"]
        self.logger = logging.getLogger(self.__class__.__name__)
        self.jobs_data = []

    def _initialize_driver(self):
        console = Console()
        try:
            self.driver = init_driver(self.browser, None, headless=self.headless)
            console.print(
                f"[bold green]WebDriver {self.driver.name} initialized successfully![/]"
            )
        except (Exception, WebDriverException) as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    def _click_element(self, element):
        """Click an element with scroll into view and fallback to JavaScript click"""
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
                element,
            )
            WebDriverWait(self.driver, self.SHORT_WAIT).until(
                EC.element_to_be_clickable(element)
            )
            element.click()
            # time.sleep(0.5)  # wait for any potential animations
            return True
        except (ElementClickInterceptedException, ElementNotInteractableException):
            self.logger.warning("Element not clickable, javaScript click fallback")
            try:
                self.driver.execute_script("arguments[0].click();", element)
                # time.sleep(0.5)  # wait for any potential animations
                return True
            except Exception as e:
                self.logger.error(f"Oh no JavaScript click also failed: {e}")
                return False
        except (StaleElementReferenceException, WebDriverException) as e:
            self.logger.error(f"Error clicking element: {e}")
            return False

    def _find_element(self, by, value, timeout=None):
        """Find an element wait for it to be located with optional timeout"""
        timeout = timeout or self.SHORT_WAIT
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            self.logger.warning(f"Element not found: {value}")
            return None
        except WebDriverException as e:
            self.logger.error(f"WebDriver exception while finding element: {e}")
            return None

    def _clean_text(self, text):
        if not text or text == "N/A":
            return text

        # remove invisible characters (zero-width space, word joiner, etc.)
        cleaned = re.sub(r"[\u2060\u200B-\u200F\uFEFF]", "", text)

        # Replace em dash and en dash with regular hyphen
        cleaned = cleaned.replace("–", "-").replace("—", "-")

        return cleaned

    def _parse_posted_date(self, date_text: str):
        if not date_text or date_text == "N/A" or "Posted" not in date_text:
            return "N/A"
        try:
            rm_posted = date_text.replace("Posted", "").strip()

            if "30+" in rm_posted:
                return "30+ days ago"

            get_num = re.search(r"\d+", rm_posted)
            if not get_num:
                return "N/A"

            days_ago = int(get_num[0])
            posted_date = datetime.now() - timedelta(days=days_ago)
            return posted_date.strftime("%d-%m-%Y")

        except ValueError:
            self.logger.error(f"Error parsing date text: {date_text}")
            return "N/A"

    def _login_and_navigate(self):
        """Navigate to applied jobs page and handle login"""
        try:
            self.driver.get(self.base_url)
        except WebDriverException as e:
            self.logger.error(f"Error navigating to {self.base_url}: {e}")
            return False

        wait = WebDriverWait(self.driver, self.LONG_WAIT)

        try:
            email_input = wait.until(
                EC.presence_of_element_located((By.ID, "emailAddress"))
            )
            email_input.clear()
            email_input.send_keys(self.email)
            time.sleep(0.3)
            email_input.send_keys(Keys.ENTER)

        except (TimeoutException, WebDriverException) as e:
            self.logger.error(f"Error during email input : {e}")

            if "applied-jobs" in self.driver.current_url.lower():
                self.logger.info("Already logged in, skipping OTP")
                return True
            return False

        return self._handle_otp()

    def _handle_otp(self):
        """Handle OTP input if required"""
        wait = WebDriverWait(self.driver, self.LONG_WAIT)
        console = Console()

        while True:
            if "applied-jobs" in self.driver.current_url.lower():
                try:
                    wait.until(
                        lambda d: d.find_element(
                            By.CSS_SELECTOR, "[data-automation^='job-item-']"
                        )
                    )
                    self.logger.info("Logged in from web page")
                    return True
                except TimeoutException:
                    self.logger.warning("Timeout while waiting for job cards to load")
                    return False

            try:
                self.logger.info("Please enter the OTP sent to your email")
                otp = console.input(
                    "[bold yellow]Enter the OTP sent to your email: [/]"
                ).strip()

                if len(otp) != 6 or not otp.isdigit():
                    self.logger.warning(
                        "Invalid OTP format. Please enter a 6-digit number."
                    )
                    console.print(
                        "[bold red]Invalid OTP format. Please enter a 6-digit number.[/]"
                    )
                    continue

                otp_field = wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "input[aria-label='verification input']")
                    )
                )

                otp_field.click()
                otp_field.clear()

                for digit in otp:
                    otp_field.send_keys(digit)
                    time.sleep(0.3)

                time.sleep(2)

                # check otp error message
                try:
                    error_alert = self.driver.find_element(
                        By.CSS_SELECTOR, "[aria-live='polite']"
                    )
                    if "invalid code" in error_alert.text.strip().lower():
                        self.logger.warning("Invalid OTP, try again...")
                        console.print("[bold red]Invalid OTP, please try again.[/]")
                        continue  # retry otp
                except NoSuchElementException:
                    pass

                # wait for the page to load after OTP
                try:
                    wait.until(
                        lambda d: d.find_elements(
                            By.CSS_SELECTOR, "[data-automation^='job-item-']"
                        )
                    )

                    self.logger.info("Successfully logged into applied jobs page")
                    return True

                except TimeoutException:
                    self.logger.warning(
                        "Timeout while waiting for job cards to load after OTP"
                    )
                    return False

            except (TimeoutException, WebDriverException) as e:
                self.logger.error(f"Exception during OTP input or field loading: {e}")
                return False

    def _find_job_cards(self):
        """Find job cards on the current page"""
        try:
            elements = WebDriverWait(self.driver, self.LONG_WAIT).until(
                lambda d: (
                    d.find_elements(By.CSS_SELECTOR, "[data-automation^='job-item-']")
                )
            )
            if elements:
                self.logger.info(f"Found {len(elements)} job cards")
                return self._sort_job_cards(elements)
            else:
                self.logger.warning("No job cards found on this page")
                return []

        except TimeoutException:
            self.logger.warning("No job cards found on this page")
            return []
        except WebDriverException as e:
            self.logger.error(f"WebDriver exception while finding job cards: {e}")
            return []

    def _sort_job_cards(self, elements):
        """Sort job cards by their index number"""

        def get_index(element):
            try:
                attr = element.get_attribute("data-automation")
                return int(attr.split("-")[-1])
            except (ValueError, AttributeError, StaleElementReferenceException) as e:
                self.logger.error(f"Error getting index from element: {e}")
            return 0

        return sorted(elements, key=get_index)

    def _is_on_applied_jobs_page(self):
        """Check if it's on applied jobs page by looking for job cards"""
        try:
            if "applied-jobs" not in self.driver.current_url.lower():
                self.logger.warning("URL does not contain 'applied-jobs'")
                return False

            wait = WebDriverWait(self.driver, self.SHORT_WAIT)
            wait.until(
                lambda d: d.find_element(
                    By.CSS_SELECTOR, "[data-automation^='job-item-']"
                )
            )
            return True
        except TimeoutException:
            self.logger.warning("Not on job applied jobs page, job cards not found")
            return False

    def _open_drawer(self, job_card):
        """Open drawer for each job card by clicking the header"""
        try:
            header_card = job_card.find_element(
                By.CSS_SELECTOR, "h4 span[role='button']"
            )

            if not self._click_element(header_card):
                self.logger.error("Failed to click job card header")
                return False

            drawer = WebDriverWait(self.driver, self.SHORT_WAIT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[role='dialog']"))
            )
            if drawer:
                return drawer
            else:
                self.logger.warning("Job card drawer not found after clicking header")
                return None

        except TimeoutException:
            self.logger.error("Timeout while waiting for job card header or drawer")
            return None

    def _extract_job_info_from_drawer(self, drawer):
        """Extract job information from the opened drawer"""
        results = {
            "job_title": "N/A",
            "company_name": "N/A",
            "job_location": "N/A",
            "job_salary": "N/A",
            "job_url": "N/A",
        }

        try:
            info_holder = WebDriverWait(drawer, self.LONG_WAIT).until(
                EC.presence_of_element_located(
                    (By.XPATH, ".//span[contains(text(), 'Lamaran untuk')]")
                )
            )
            siblings = info_holder.find_elements(By.XPATH, "./following-sibling::*")

            if len(siblings) >= 3:
                info_title = siblings[0]  # h3
                info_company = siblings[1]  # span
                info_location = siblings[2]  # span

                results.update(
                    {
                        "job_title": info_title.text.strip(),
                        "company_name": info_company.text.strip(),
                        "job_location": info_location.text.strip(),
                    }
                )

            # Handle salary and URL in one pass
            if len(siblings) >= 4:
                fourth_element = siblings[3]
                # Check if it contains salary or URL
                if fourth_element.find_elements(By.TAG_NAME, "a"):
                    # Has link, no salary
                    url_element = fourth_element.find_element(By.TAG_NAME, "a")
                    results["job_url"] = (
                        url_element.get_attribute("href").strip().split("?")[0]
                    )
                else:
                    # Has salary text
                    salary_text = fourth_element.text.strip()
                    if "per month" in salary_text.lower():
                        salary_raw = salary_text.split("per month")[0].strip()
                        cleaned_salary = self._clean_text(salary_raw)
                        results["job_salary"] = cleaned_salary

                    # Check next sibling for URL
                    if len(siblings) >= 5:
                        url_element = siblings[4].find_element(By.TAG_NAME, "a")
                        results["job_url"] = (
                            url_element.get_attribute("href").strip().split("?")[0]
                        )

        except (NoSuchElementException, TimeoutException, WebDriverException) as e:
            self.logger.error(f"Error extracting job info from drawer: {e}")
        return results

    def _extract_status_from_drawer(self, drawer):
        """Extract application status from the opened drawer"""
        application_status = []
        is_expired = False

        try:
            status_holder = WebDriverWait(drawer, self.LONG_WAIT).until(
                EC.presence_of_element_located(
                    (By.XPATH, ".//span[contains(text(), 'Status lamaran')]")
                )
            )
            wrapper = status_holder.find_element(
                By.XPATH, "./following-sibling::div[1]"
            )
            status_blocks = wrapper.find_elements(By.XPATH, "./div/div")

            for block in status_blocks:
                try:
                    status_wrapper = block.find_element(By.XPATH, "./div/div[2]/div")
                    status_elements = status_wrapper.find_elements(By.TAG_NAME, "span")[
                        :2
                    ]
                    if len(status_elements) >= 2:
                        status_text = status_elements[0].text.strip()
                        status_updated = status_elements[1].text.strip().split("\n")[0]
                        application_status.append(
                            {
                                "status": status_text,
                                "updated_at": status_updated,
                            }
                        )

                except NoSuchElementException:
                    # print("Missing status data in span, skipping...")
                    pass
            if not application_status:
                self.logger.warning("No valid status data found in any blocks")
            try:
                wrapper.find_element(
                    By.XPATH,
                    ".//following-sibling::div//span[contains(text(), 'Lowongan kerja ini telah kedaluwarsa')]",
                )
                is_expired = True

            except NoSuchElementException:
                is_expired = False

        except (NoSuchElementException, TimeoutException, WebDriverException) as e:
            self.logger.error(f"Error extracting application status from drawer: {e}")

        return {
            "application_status": application_status,
            "is_expired": is_expired,
        }

    def _extract_docs_name_from_drawer(self, drawer):
        """Extract resume and cover letter names from the opened drawer"""
        results = {
            "resume": "N/A",
            "cover_letter": "N/A",
        }

        try:
            cv_element = WebDriverWait(drawer, self.SHORT_WAIT).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "span[data-automation='job-item-resume']")
                )
            )
            cv_text = self._clean_text(cv_element.text.strip())
        except (TimeoutException, WebDriverException):
            self.logger.error("Resume element not found or timed out")
            cv_text = "N/A"
        try:
            cl_element = WebDriverWait(drawer, self.SHORT_WAIT).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "span[data-automation='job-item-cover-letter']")
                )
            )
            cl_text = self._clean_text(cl_element.text.strip())
        except (TimeoutException, WebDriverException):
            self.logger.error("Cover letter element not found or timed out")
            cl_text = "N/A"

        results.update({"resume": cv_text, "cover_letter": cl_text})
        return results

    def _extract_stats_from_drawer(self, drawer):
        """Extract total applicants from the opened drawer"""
        try:
            applicants_raw = (
                WebDriverWait(drawer, self.SHORT_WAIT)
                .until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//span[contains(text(), 'kandidat melamar untuk posisi ini')]",
                        )
                    )
                )
                .text
            )
            # regex to extract the number of applicants
            # it will match the first number in the string
            match = re.search(r"^(\d+)", applicants_raw)
            return int(match.group(1)) if match else None

        except (TimeoutException, WebDriverException):
            self.logger.error("Applicants element not found or timed out")
            return None

    def _open_info_url_in_new_tab(self, info_url):
        original_window = self.driver.current_window_handle
        try:
            self.driver.execute_script(f"window.open('{info_url}', '_blank');")
            WebDriverWait(self.driver, self.LONG_WAIT).until(
                lambda d: len(d.window_handles) > 1
            )

            new_windows = [
                w for w in self.driver.window_handles if w != original_window
            ]

            if not new_windows:
                self.logger.error("No new window opened after clicking job URL")
                return None

            self.driver.switch_to.window(new_windows[0])

            WebDriverWait(self.driver, self.LONG_WAIT).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            return original_window

        except TimeoutException:
            self.logger.error("New window did not open in time")
            return None
        except Exception as e:
            self.logger.error(f"Error opening job URL in new tab: {e}")
            return None

    def _extract_extra_info_from_new_tab(self):
        results = {
            "job_classification": "N/A",
            "job_type": "N/A",
            "job_posted_date": "N/A",
        }

        extractions = [
            (
                "job_classification",
                "span[data-automation='job-detail-classifications']",
                "a",
            ),
            ("job_type", "span[data-automation='job-detail-work-type']", "a"),
            ("job_posted_date", "//span[contains(text(), 'Posted')]", None),
        ]

        for field, selector, child_tag in extractions:
            try:
                if selector.startswith("//"):
                    element = self._find_element(
                        By.XPATH, selector, timeout=self.SHORT_WAIT
                    )
                else:
                    element = self._find_element(
                        By.CSS_SELECTOR, selector, timeout=self.SHORT_WAIT
                    )
                if element:
                    if child_tag:
                        text_element = element.find_element(By.TAG_NAME, child_tag)
                        raw_text = text_element.text.strip()
                    else:
                        raw_text = element.text.strip()

                    cleaned_text = self._clean_text(raw_text)

                    if field == "job_posted_date":
                        results[field] = self._parse_posted_date(cleaned_text)
                    else:
                        results[field] = cleaned_text

            except (TimeoutException, WebDriverException):
                self.logger.error(f"{field} element not found or timed out")
            except Exception as e:
                self.logger.error(f"Unexpected error extracting {field}: {e}")

        return results

    def _close_info_tab(self, original_window):
        try:
            if len(self.driver.window_handles) > 1:
                self.driver.close()
            if original_window and original_window in self.driver.window_handles:
                self.driver.switch_to.window(original_window)
            else:
                if self.driver.window_handles:
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    self.logger.warning("Switched to fallback window")

        except WebDriverException as e:
            self.logger.error(f"Error closing info tab or switching back: {e}")

    def _close_drawer(self):
        """Close the job details drawer"""
        try:
            close_btn = self._find_element(
                By.CSS_SELECTOR, "[aria-label='Close']", timeout=self.SHORT_WAIT
            )
            if close_btn and self._click_element(close_btn):
                time.sleep(0.3)  # wait for drawer to close, do not remove this
                return True
            self.logger.warning("Failed to close job drawer")
            return False
        except (TimeoutException, WebDriverException) as e:
            self.logger.error(f"Error closing job drawer: {e}")
            return False

    def _scrape_page(self, page_num, total_jobs_so_far, reverse_cards=False):
        console = Console()
        jobs_processed = 0

        console.print(f"[bold cyan]Processing page {page_num}...[/]")
        self.logger.info(f"Processing page {page_num}")

        job_cards = self._find_job_cards()
        if not job_cards:
            self.logger.warning("No job cards found on this page")
            console.print("[bold red]No job cards found on this page[/]")
            return jobs_processed

        console.print(
            f"[bold yellow]Found {len(job_cards)} job cards on page {page_num}[/]"
        )
        if reverse_cards:
            job_cards = list(reversed(job_cards))

        for i, card in enumerate(job_cards, 1):
            job_start = time.time()

            with Status(
                f"[yellow]Processing job {i}/{len(job_cards)} [/]",
                console=console,
                spinner="dots",
            ):
                self.logger.info(f"Processing job {i}/{len(job_cards)}")

                job_info = {
                    "id": total_jobs_so_far + jobs_processed + 1,
                    "job_platform": "JobStreet",
                }

                try:
                    drawer = self._open_drawer(card)
                    if not drawer:
                        self.logger.warning("Failed to open job drawer, skipping...")
                        continue

                    info = self._extract_job_info_from_drawer(drawer)

                    if info.get("job_url") != "N/A":
                        original_window = self._open_info_url_in_new_tab(
                            info["job_url"]
                        )
                        if original_window is None:
                            self.logger.error(
                                "Failed to open job URL in new tab, skipping..."
                            )
                            continue
                        try:
                            extra_info = self._extract_extra_info_from_new_tab()
                        finally:
                            self._close_info_tab(original_window)

                    status = self._extract_status_from_drawer(drawer)
                    docs = self._extract_docs_name_from_drawer(drawer)
                    applicants = self._extract_stats_from_drawer(drawer)

                    job_info.update(
                        {
                            "data_retrieved_at": time.strftime(
                                "%d-%m-%Y %H:%M:%S", time.localtime()
                            ),
                            "job_title": info["job_title"],
                            "company_name": info["company_name"],
                            "job_location": info["job_location"],
                            "job_classification": extra_info["job_classification"],
                            "job_type": extra_info["job_type"],
                            "job_posted_date": extra_info["job_posted_date"],
                            "salary_range": info["job_salary"],
                            "job_url": info["job_url"],
                            "resume": docs["resume"],
                            "cover_letter": docs["cover_letter"],
                            "total_applicants": (
                                applicants if applicants is not None else "N/A"
                            ),
                            "is_expired": status["is_expired"],
                            "application_status": status["application_status"],
                        }
                    )

                    self._close_drawer()

                except Exception as e:
                    self.logger.error(f"Error processing job card {i}: {e}")
                    continue

                self.jobs_data.append(job_info)
                jobs_processed += 1
                elapsed = time.time() - job_start
                console.print(
                    f"[green]✔ Finished job {i}/{len(job_cards)} in {elapsed:.2f}s[/]"
                )
        self.logger.info(f"Completed page {page_num}, jobs processed: {jobs_processed}")
        console.print(f"[bold green]✔ Completed page {page_num}[/]")
        return jobs_processed

    def scrape_all_jobs(self, reverse=False):
        """Main scraping method"""
        console = Console()
        start_time = time.time()
        total_jobs = 0

        self._login_and_navigate()
        console.print("[bold cyan]Starting JobStreet scraping[/]")
        self.logger.info("Starting job scraping")

        try:
            if reverse:
                console.print("[bold yellow] Analyzing pages in descending order...[/]")
                last_page_num = self._find_last_page()
                console.print(f"[bold yellow]Last page found: {last_page_num}[/]")
                self.logger.info(f"Last page found: {last_page_num}")

                for page_num in range(last_page_num, 0, -1):
                    total_jobs += self._scrape_page(
                        page_num, total_jobs, reverse_cards=True
                    )

                    if page_num > 1:
                        if not self._go_to_prev_page():
                            self.logger.warning(
                                "Failed to navigate to previous page..."
                            )
                            break
            else:
                page_num = 0
                while True:
                    page_num += 1
                    total_jobs += self._scrape_page(
                        page_num, total_jobs, reverse_cards=False
                    )

                    if not self._go_to_next_page():
                        self.logger.warning("No more pages available")
                        break
        finally:
            total_elapsed = time.time() - start_time
            self.logger.info(f"Scraping completed. Total jobs collected: {total_jobs}")
            return {
                "jobs_data": self.jobs_data,
                "total_jobs": total_jobs,
                "total_elapsed": total_elapsed,
                "scraping_completed_at": time.strftime(
                    "%d-%m-%Y %H:%M:%S", time.localtime()
                ),
            }

    def _go_to_next_page(self):
        """Navigate to the next page of applied jobs"""
        console = Console()

        try:
            next_btn = self._find_element(
                By.CSS_SELECTOR, "a[aria-label='Next']", self.SHORT_WAIT
            )
            if not next_btn:
                self.logger.warning("Next page button not found")
                return False

            current_url = self.driver.current_url

            if not self._click_element(next_btn):
                self.logger.error("Failed to click next page button")
                return False

            try:
                WebDriverWait(self.driver, self.SHORT_WAIT).until(
                    lambda d: d.current_url != current_url
                )
            except TimeoutException:
                self.logger.error(
                    "Redirecting error: page url did not change after clicking next"
                )
                return False

            WebDriverWait(self.driver, self.LONG_WAIT).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[data-automation^='job-item-1']")
                )
            )

            time.sleep(1)  # wait for the page to load
            # self.driver.execute_script("window.scrollTo(0, 0);")

            self.logger.info("Successfully navigated to next page")
            console.print("[bold green]Navigated to next page[/]")
            return True

        except WebDriverException as e:
            self.logger.error(f"Failed to go to next page: {e}")
            return False

    def _go_to_prev_page(self):

        try:
            prev_btn = self._find_element(
                By.CSS_SELECTOR, "a[aria-label='Previous']", self.SHORT_WAIT
            )
            if not prev_btn:
                self.logger.warning("Previous page button not found")
                return False
            current_url = self.driver.current_url

            if not self._click_element(prev_btn):
                self.logger.error("Failed to click previous page button")
                return False
            try:
                WebDriverWait(self.driver, self.SHORT_WAIT).until(
                    lambda d: d.current_url != current_url
                )
                WebDriverWait(self.driver, self.LONG_WAIT).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "[data-automation='job-item-1']")
                    )
                )
            except TimeoutException:
                self.logger.error(
                    "Redirecting error: page url did not change after clicking previous"
                )
                return False

            time.sleep(1)  # wait for the page to load
            self.logger.info("Successfully navigated to previous page")
            return True

        except Exception as e:
            self.logger.error(f"Failed to go to previous page: {e}")
            return False

    def _find_last_page(self):
        page_num = 1
        while True:
            # TODO: scroll to bottom maybe
            if not self._go_to_next_page():
                self.logger.info("No more pages available, stopping search")
                break
            page_num += 1

        return page_num

    def close_browser(self):
        """Close the browser"""
        if hasattr(self, "driver") and self.driver:
            try:
                self.driver.quit()
            except WebDriverException as e:
                self.logger.error(f"Error closing the browser: {e}")
