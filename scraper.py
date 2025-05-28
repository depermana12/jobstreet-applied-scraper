from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from configs import init_driver, configurations
from selenium.webdriver.common.by import By
from parser import parse_job
import time


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
            email_input.send_keys(Keys.ENTER)

        except Exception as e:
            print(f"Could not auto-fill email: {e}")

        print("Enter OTP manually — you have 30 seconds")  # manualy input otp
        time.sleep(50)

    def find_job_cards(self):
        """Find job cards on the current page"""
        elements = self.driver.find_elements(
            By.CSS_SELECTOR, "[data-automation^='job-item-']"
        )
        if elements:
            print(f"Found {len(elements)} job cards")
            return self._sort_job_cards(elements)

    def _sort_job_cards(self, elements):
        """Sort job cards by their index number"""

        def get_index(element):
            try:
                attr = element.get_attribute("data-automation")
                return int(attr.split("-")[-1])
            except (ValueError, AttributeError):
                return float("inf")

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
            next_btn = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Next']")
            if not next_btn:
                print("Next page button not found")
                return False

            current_url = self.driver.current_url

            try:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", next_btn
                )
            except Exception as e:
                print(f"Scroll into view failed: {e}")

            try:
                self.driver.execute_script("arguments[0].click();", next_btn)
            except Exception as e:
                print(f"JS click failed: {e}")
                return False

            # Wait for URL change or job cards to reload
            wait.until(lambda d: d.current_url != current_url)
            wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "[data-automation^='job-item-']")
                )
            )
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
                    job_info = {"page": page_num}
                    job_info["id"] = total_jobs + 1

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

                        job_info["job_link"] = drawer.find_element(
                            By.TAG_NAME, "a"
                        ).get_attribute("href")
                        job_info["cv_name"]

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

                self.driver.execute_script("window.scrollTo(0, 0);")

                print(f"Completed page {page_num}, total jobs: {total_jobs}")

                current_url = self.driver.current_url

                if max_pages and page_num >= max_pages:
                    print(f"Reached maximum pages: {max_pages}")
                    break

                if not self.go_to_next_page():
                    print("No more pages available")
                    break

                try:
                    WebDriverWait(self.driver, 10).until(
                        lambda d: d.current_url != current_url
                    )
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, "[data-automation^='job-item-']")
                        )
                    )
                    time.sleep(3)
                except Exception as e:
                    print(f"Page load wait failed: {e}")
                    break
            return self.jobs_data
        finally:
            print(f"Scraping completed. Total jobs collected: {total_jobs}")
            return self.jobs_data
