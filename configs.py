from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium import webdriver
from pathlib import Path
import tempfile
import logging
import shutil
import time
import os

configurations = {
    "base_url": "https://id.jobstreet.com/id/my-activity/applied-jobs",
    "default_wait": 20,
    "short_wait": 3,
}

logger = logging.getLogger(__name__)


def init_logging(log_dir="logs", log_file="jobstreet_scraper.log", log_console=False):
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)
    handlers = [logging.FileHandler(log_path, encoding="utf-8")]

    if log_console:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] %(name)s - %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
        handlers=handlers,
    )


def init_driver(browser="firefox", headless=False):

    browser = browser.lower()
    if browser not in ["firefox", "chrome"]:
        raise ValueError(
            f"Unsupported browser {browser}. Please use 'firefox' or 'chrome'."
        )

    logger.info(f"Initializing {browser} driver")

    try:
        if browser == "firefox":
            return init_firefox_driver(headless)
        elif browser == "chrome":
            return init_chrome_driver(headless)
        else:
            raise ValueError(f"Unsupported browser {browser}")
    except Exception as e:
        logger.error(f"Error initializing {browser} driver: {e}")
        raise


def init_firefox_driver(headless=False):
    try:
        options = FirefoxOptions()
        firefox_profile = FirefoxProfile()
        options.profile = firefox_profile

        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            logger.info(f"Firefox running in headless mode")

        #  disable notification
        options.set_preference("dom.webnotifications.enabled", False)
        options.set_preference("dom.push.enabled", False)
        options.set_preference("permissions.default.desktop-notification", 2)
        # anti-detection
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)

        driver = webdriver.Firefox(options=options)
        # firefox not support --start-maximize preference, manual here
        if not headless:
            driver.maximize_window()

        if headless:
            driver.execute_script(
                """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """
            )

        time.sleep(2)
        logger.info("Firefox driver initialized successfully")
        return driver

    except Exception as e:
        logger.error(f"Error initializing Firefox driver: {e}")
        raise


def init_chrome_driver(headless=False):
    try:
        options = ChromeOptions()
        temp_user_data_dir = tempfile.mkdtemp(prefix="chrome_selenium_")
        options.add_argument(f"--user-data-dir={temp_user_data_dir}")
        logger.info(f"Using temporary chrome profile dir: {temp_user_data_dir}")

        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            logger.info(f"Chrome running in headless mode")

        options.add_argument("--start-maximized")

        # disable notifications and other features
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")

        # disable automation flags
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("prefs", {"translate": {"enabled": False}})

        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        driver = webdriver.Chrome(options=options)

        if headless:
            driver.execute_script(
                """
                Object.defineProperty(navigator, 'userAgent', {
                    get: () => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
                });
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """
            )

        time.sleep(2)
        logger.info("Chrome driver initialized successfully")
        return driver

    except Exception as e:
        logger.error(f"Error initializing Chrome driver: {e}")
        raise


def cleanup_chrome_temp_dir():
    try:
        temp_dir = Path(tempfile.gettempdir())
        for dir in temp_dir.glob("chrome_selenium_*"):
            if dir.is_dir():
                try:
                    shutil.rmtree(dir)
                    logger.info(f"Cleanup up chrome temp directory: {dir}")
                except Exception as e:
                    logger.warning(f"Failed to clean temp directory {dir}: {e}")
    except Exception as e:
        logger.warning(f"Error during temp directory cleanup: {e}")


def cleanup_firefox_temp_dir(profile_path):
    if profile_path and os.path.exists(profile_path):
        try:
            shutil.rmtree(profile_path)
            logger.info(f"Cleaned up Firefox profile directory: {profile_path}")
        except Exception as e:
            logger.warning(
                f"Failed to clean Firefox profile directory {profile_path}: {e}"
            )


def cleanup_webdriver_temp_dir(browser, profile_path=None):
    if browser == "firefox":
        cleanup_firefox_temp_dir(profile_path)
    elif browser == "chrome":
        cleanup_chrome_temp_dir()
