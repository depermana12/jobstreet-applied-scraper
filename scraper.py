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
import time
import re


class JobStreetScraper:
    def __init__(self, email):
        self.email = email
        self.driver = init_driver("default")
        self.base_url = configurations["base_url"]
        self.LONG_WAIT = configurations["default_wait"]
        self.SHORT_WAIT = configurations["short_wait"]
        self.jobs_data = []

    def _login_and_navigate(self):
        """Navigate to applied jobs page and handle login"""
        try:
            self.driver.get(self.base_url)
        except WebDriverException as e:
            print(f"Error navigating to {self.base_url}: {e}")
            return False

        wait = WebDriverWait(self.driver, self.LONG_WAIT)

        try:
            email_input = wait.until(
                EC.presence_of_element_located((By.ID, "emailAddress"))
            )
            email_input.clear()
            email_input.send_keys(self.email)
            time.sleep(0.5)
            email_input.send_keys(Keys.ENTER)

        except (TimeoutException, WebDriverException) as e:
            print(f"Error during email input : {e}")

            if "applied-jobs" in self.driver.current_url.lower():
                print("Already logged in, skipping OTP")
                return True
            return False

        return self._handle_otp()

    def _handle_otp(self):
        """Handle OTP input if required"""
        wait = WebDriverWait(self.driver, self.LONG_WAIT)

        while True:
            if "applied-jobs" in self.driver.current_url.lower():
                try:
                    wait.until(
                        lambda d: d.find_element(
                            By.CSS_SELECTOR, "[data-automation^='job-item-']"
                        )
                    )
                    print("Logged in from web page")
                    return True
                except TimeoutException:
                    print("Timeout while waiting for job cards to load")
                    return False

            try:
                print("Please enter the OTP sent to your email")
                otp = input("Enter the OTP: ").strip()

                if len(otp) != 6 or not otp.isdigit():
                    print("Invalid OTP format. Please enter a 6-digit number.")
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
                        print("Invalid OTP, try again...")
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

                    print("Successfully logged in and navigated to applied jobs page")
                    return True

                except TimeoutException:
                    print("Timeout while waiting for job cards to load after OTP")
                    return False

            except (TimeoutException, WebDriverException) as e:
                print(f"Exception during OTP input or field loading: {e}")
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
                print(f"Found {len(elements)} job cards")
                return self._sort_job_cards(elements)
            else:
                return []

        except TimeoutException:
            print("No job cards found on this page")
            return []
        except WebDriverException as e:
            print(f"WebDriver exception while finding job cards: {e}")
            return []

    def _sort_job_cards(self, elements):
        """Sort job cards by their index number"""

        def get_index(element):
            try:
                attr = element.get_attribute("data-automation")
                return int(attr.split("-")[-1])
            except (ValueError, AttributeError, StaleElementReferenceException) as e:
                print(f"Error getting index from element: {e}")
            return 0

        return sorted(elements, key=get_index)

    def _has_job_cards(self):
        """Check if it's on applied jobs page by looking for job cards"""
        try:
            if "applied-jobs" not in self.driver.current_url.lower():
                print("URL does not contain 'applied-jobs'")
                return False

            wait = WebDriverWait(self.driver, self.SHORT_WAIT)
            wait.until(
                lambda d: d.find_element(
                    By.CSS_SELECTOR, "[data-automation^='job-item-']"
                )
            )
            return True
        except TimeoutException:
            print("Not on job applied jobs page, job cards not found")
            return False

    def _close_drawer(self):
        """Close the job details drawer"""
        close_btn = self._find_element(
            By.CSS_SELECTOR, "[aria-label='Close']", timeout=self.SHORT_WAIT
        )
        if close_btn and self._click_element(close_btn):
            time.sleep(1)  # wait for drawer to close, do not remove this
            return True
        return False

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
            time.sleep(0.5)  # wait for any potential animations
            return True
        except (ElementClickInterceptedException, ElementNotInteractableException):
            print("Element not clickable, javaScript click fallback")
            try:
                self.driver.execute_script("arguments[0].click();", element)
                time.sleep(0.5)  # wait for any potential animations
                return True
            except Exception as e:
                print(f"Oh no JavaScript click also failed: {e}")
                return False
        except (StaleElementReferenceException, WebDriverException) as e:
            print(f"Error clicking element: {e}")
            return False

    def _find_element(self, by, value, timeout=None):
        """Find an element with optional timeout"""
        timeout = timeout or self.SHORT_WAIT
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            print(f"Element not found: {value}")
            return None
        except WebDriverException as e:
            print(f"WebDriver exception while finding element: {e}")
            return None

    def _go_to_next_page(self):
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

    def close_browser(self):
        """Close the browser"""
        if hasattr(self, "driver") and self.driver:
            try:
                self.driver.quit()
                print("Browser closed")
            except WebDriverException as e:
                print(f"Error closing the browser: {e}")

    def scrape_all_jobs(self, max_pages=None):
        """Main scraping method"""

        self._login_and_navigate()
        print("Starting job scraping")

        page_num = 0
        total_jobs = 0

        try:
            while True:
                page_num += 1
                print(f"\nProcessing page {page_num}")

                job_cards = self._find_job_cards()
                if not job_cards:
                    print("No more job cards found")
                    break

                for i, card in enumerate(job_cards, 1):
                    print(f"Processing job {i}/{len(job_cards)}")

                    job_info = {
                        "id": total_jobs + 1,
                        "job_platform": "JobStreet",
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

                        # ------- INFO SECTION -------
                        try:
                            info_holder = WebDriverWait(drawer, 10).until(
                                EC.presence_of_element_located(
                                    (
                                        By.XPATH,
                                        ".//span[contains(text(), 'Lamaran untuk')]",
                                    )
                                )
                            )
                            info_title = info_holder.find_element(
                                By.XPATH, "./following-sibling::h3[1]"
                            )
                            info_company = info_title.find_element(
                                By.XPATH, "./following-sibling::span[1]"
                            )
                            info_location = info_company.find_element(
                                By.XPATH, "./following-sibling::span[1]"
                            )

                            try:
                                info_salary = info_location.find_element(
                                    By.XPATH, "./following-sibling::span[1]"
                                )
                                salary_text = info_salary.text.strip()
                                has_salary = "per month" in salary_text.lower()

                            except NoSuchElementException:
                                info_salary = None
                                salary_text = "N/A"
                                has_salary = False

                            try:
                                if has_salary:
                                    info_url = info_salary.find_element(
                                        By.XPATH, "./following-sibling::span[1]/a"
                                    )
                                else:
                                    info_url = info_location.find_element(
                                        By.XPATH, "./following-sibling::span[1]/a"
                                    )
                                url_text = (
                                    info_url.get_attribute("href").strip().split("?")[0]
                                )
                            except NoSuchElementException:
                                url_text = "N/A"

                        except Exception as e:
                            print(f"Error extracting job info section: {e}")
                            continue  # skip this card if basic info fails

                        # ------- STATUS SECTION -------
                        try:
                            details_elem = wait.until(
                                EC.presence_of_element_located(
                                    (
                                        By.XPATH,
                                        ".//span[contains(text(), 'Status lamaran')]",
                                    )
                                )
                            )
                            status_wrapper = details_elem.find_element(
                                By.XPATH, "./following-sibling::div[1]"
                            )
                            status_blocks = status_wrapper.find_element(
                                By.XPATH, ".//div/div/div/div[2]/div"
                            )
                            try:
                                span_elements = status_blocks.find_elements(
                                    By.TAG_NAME, "span"
                                )[:2]

                                application_status = []

                                if len(span_elements) >= 2:
                                    status_text = span_elements[0].text.strip()
                                    status_updated = (
                                        span_elements[1].text.strip().split("\n")[0]
                                    )
                                    application_status.append(
                                        {
                                            "status": status_text,
                                            "updated_at": status_updated,
                                        }
                                    )
                                else:
                                    print("Missing status data in span, skipping...")

                            except NoSuchElementException:
                                print("Missing status data in span, skipping...")

                            try:
                                status_wrapper.find_element(
                                    By.XPATH,
                                    ".//following-sibling::div//span[contains(text(), 'Lowongan kerja ini telah kedaluwarsa')]",
                                )
                                is_expired = True
                            except NoSuchElementException:
                                is_expired = False

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

                        except Exception as e:
                            print(f"Could not find application status section: {e}")
                            application_status = []
                            cv_text = "Not specified"
                            cl_text = "Not specified"
                            applicants_text = "Not specified"

                        # ------- Assign Data -------
                        job_info.update(
                            {
                                "data_retrieved_at": time.strftime(
                                    "%d-%m-%Y %H:%M:%S", time.localtime()
                                ),
                                "job_title": info_title.text.strip(),
                                "company_name": info_company.text.strip(),
                                "job_location": info_location.text.strip(),
                                "salary_range": salary_text if has_salary else "N/A",
                                "job_url": url_text,
                                "resume": cv_text,
                                "cover_letter": cl_text,
                                "total_applicants": applicants_text,
                                "is_expired": is_expired,
                                "application_status": application_status,
                            }
                        )

                        self._close_drawer()

                    except (
                        NoSuchElementException,
                        StaleElementReferenceException,
                        TimeoutException,
                    ) as e:
                        print(f"Error getting job details: {e}")
                        continue

                    self.jobs_data.append(job_info)
                    total_jobs += 1

                print(f"Completed page {page_num}, total jobs: {total_jobs}")

                if max_pages and page_num >= max_pages:
                    print(f"Reached maximum pages: {max_pages}")
                    break

                if not self._go_to_next_page():
                    print("No more pages available")
                    break

        finally:
            print(f"Scraping completed. Total jobs collected: {total_jobs}")
            return self.jobs_data
