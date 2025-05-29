from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from configs import init_driver, configurations
from selenium.webdriver.common.by import By
from parser import parse_job
import time
import re


class JobStreetScraper:
    def __init__(self, use_profile="default"):
        self.driver = init_driver(use_profile=use_profile)
        self.base_url = configurations["base_url"]
        self.email = configurations["email"]
        self.jobs_data = []

    def login_and_navigate(self):
        """Navigate to applied jobs page and handle login"""

        self.driver.get(self.base_url)
        wait = WebDriverWait(self.driver, 15)

        try:
            email_input = wait.until(
                EC.presence_of_element_located((By.ID, "emailAddress"))
            )
            email_input.send_keys(self.email)
            time.sleep(0.5)
            email_input.send_keys(Keys.ENTER)

        except TimeoutException:
            if "applied-jobs" in self.driver.current_url.lower():
                return True
            raise

        try:
            print("please enter the OTP sent to your email")

            otp = input("Enter the OTP: ").strip()

            if len(otp) != 6 or not otp.isdigit():
                print("Invalid OTP format. Please enter a 6-digit number.")
                return False

            otp_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[aria-label='verification input']")
                )
            )

            otp_field.click()
            for digit in otp:
                otp_field.send_keys(digit)
                time.sleep(0.5)

            try:
                WebDriverWait(self.driver, 20).until(
                    lambda d: "applied" in d.current_url.lower()
                    and d.find_elements(
                        By.CSS_SELECTOR, "[data-automation^='job-item-']"
                    )
                )
                print("Successfully logged in and navigated to applied jobs page")
                return True
            except TimeoutException:
                print("Failed to navigate to applied jobs page after OTP input")
                return False

        except TimeoutException:
            print("OTP not input within timeout")
            return False

    def find_job_cards(self):
        """Find job cards on the current page"""
        try:
            elements = WebDriverWait(self.driver, 20).until(
                lambda d: (
                    d.find_elements(By.CSS_SELECTOR, "[data-automation^='job-item-']")
                )
            )

            if elements:
                print(f"Found {len(elements)} job cards")
                return self._sort_job_cards(elements)

        except NoSuchElementException:
            print("No job cards found on this page")
            return []

    def _sort_job_cards(self, elements):
        """Sort job cards by their index number"""

        def get_index(element):
            try:
                attr = element.get_attribute("data-automation")
                return int(attr.split("-")[-1])
            except (ValueError, AttributeError):
                return 0

        return sorted(elements, key=get_index)

    def _close_drawer(self):
        """Close the job details drawer"""

        close_btn = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Close']")
        close_btn.click()
        time.sleep(1)  # do not remove this
        return True

    def go_to_next_page(self):
        """Navigate to the next page if available"""
        try:
            wait = WebDriverWait(self.driver, 10)
            next_btn = self.driver.find_element(By.CSS_SELECTOR, "a[aria-label='Next']")
            current_url = self.driver.current_url
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
                next_btn,
            )
            wait.until(EC.element_to_be_clickable(next_btn))
            self.driver.execute_script("arguments[0].click();", next_btn)
            wait.until(lambda d: d.current_url != current_url)
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[data-automation^='job-item-']")
                )
            )
            time.sleep(3)
            self.driver.execute_script("window.scrollTo(0, 0);")

            print("Successfully navigated to next page")
            return True

        except Exception as e:
            print(f"Failed to go to next page: {e}")
            return False

    def close(self):
        """Close the browser"""
        if hasattr(self, "driver") and self.driver:
            self.driver.quit()
            print("Browser closed")

    def scrape_all_jobs(self, max_pages=None):
        """Main scraping method"""

        print("Starting job scraping")
        self.login_and_navigate()

        page_num = 0
        total_jobs = 0

        try:
            while True:
                page_num += 1
                print(f"\nProcessing page {page_num}")

                job_cards = self.find_job_cards()
                if not job_cards:
                    print("No more job cards found")
                    break

                for i, card in enumerate(job_cards, 1):
                    print(f"Processing job {i}/{len(job_cards)}")

                    job_info = {
                        "job_platform": "JobStreet",
                        "id": total_jobs + 1,
                    }

                    try:
                        header_card = card.find_element(
                            By.CSS_SELECTOR, "h4 span[role='button']"
                        )
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView(true);", header_card
                        )
                        wait = WebDriverWait(self.driver, 10)
                        wait.until(EC.element_to_be_clickable(header_card))
                        header_card.click()

                        drawer = wait.until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, "[role='dialog']")
                            )
                        )
                        raw_details_data = drawer.text.strip()

                        url_text = drawer.find_element(By.TAG_NAME, "a").get_attribute(
                            "href"
                        )

                        # ---------------------------------------------------------

                        try:
                            wait = WebDriverWait(drawer, 10)
                            details_elem = wait.until(
                                EC.presence_of_element_located(
                                    (
                                        By.XPATH,
                                        ".//span[contains(text(), 'Status lamaran')]",
                                    )
                                )
                            )
                            # get sibling div after the status header
                            status_wrapper = details_elem.find_element(
                                By.XPATH, "./following-sibling::div[1]"
                            )

                            # get all div children of the status wrapper
                            status_blocks = status_wrapper.find_elements(
                                By.XPATH, "./div/div"
                            )

                            application_status = []

                            for block in status_blocks:
                                try:
                                    # get to the second div inside the block (container for status and date)
                                    second_div = block.find_element(
                                        By.XPATH, "./div/div[2]"
                                    )
                                    # get all the spans (containing the data)
                                    spans = second_div.find_elements(
                                        By.TAG_NAME, "span"
                                    )
                                    # just get the first two spans (third is message, too long)
                                    if len(spans) >= 2:
                                        status_text = spans[0].text.strip()
                                        status_date = (
                                            spans[1].text.strip().split("\n")[0]
                                        )

                                        application_status.append(
                                            {"status": status_text, "date": status_date}
                                        )

                                        print(application_status)
                                except NoSuchElementException:
                                    print("Missing blocks of status, skipping...")

                            cv_elem = WebDriverWait(drawer, 3).until(
                                EC.presence_of_element_located(
                                    (
                                        By.CSS_SELECTOR,
                                        "span[data-automation='job-item-resume']",
                                    )
                                )
                            )
                            cv_text = cv_elem.get_attribute("textContent").strip()

                            cl_elem = WebDriverWait(drawer, 3).until(
                                EC.presence_of_element_located(
                                    (
                                        By.CSS_SELECTOR,
                                        "span[data-automation='job-item-cover-letter']",
                                    )
                                )
                            )

                            cl_text = cl_elem.get_attribute("textContent").strip()

                            applicants_raw = self.driver.find_element(
                                By.XPATH,
                                "//span[contains(text(), 'kandidat melamar untuk posisi ini')]",
                            ).text

                            match = re.search(r"^(\d+)", applicants_raw)
                            applicants_text = (
                                int(match.group(1)) if match else "Not specified"
                            )

                            # ---------------------------------------------------------

                            job_info["job_url"] = url_text
                            job_info["resume_filename"] = cv_text
                            job_info["cover_letter_filename"] = cl_text
                            job_info["application_status"] = application_status
                            job_info["total_applicants"] = applicants_text

                            # ---------------------------------------------------------

                        except NoSuchElementException:
                            print("Could not find application status section.")

                            job_info["resume_filename"] = "Not specified"
                            job_info["cover_letter_filename"] = "Not specified"
                            job_info["application_status"] = []
                            job_info["total_applicants"] = "Not specified"

                            # ---------------------------------------------------------

                        parsed_details = parse_job(raw_details_data)
                        job_info.update(parsed_details)
                        self._close_drawer()

                    except (
                        NoSuchElementException,
                        StaleElementReferenceException,
                    ) as e:
                        print(f"Error getting job details: {e}")
                        continue

                    self.jobs_data.append(job_info)
                    total_jobs += 1

                print(f"Completed page {page_num}, total jobs: {total_jobs}")

                if max_pages and page_num >= max_pages:
                    print(f"Reached maximum pages: {max_pages}")
                    break

                if not self.go_to_next_page():
                    print("No more pages available")
                    break

        finally:
            print(f"Scraping completed. Total jobs collected: {total_jobs}")
            return self.jobs_data
