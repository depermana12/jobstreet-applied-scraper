from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium import webdriver
from pathlib import Path
import tempfile
import platform
import logging
import shutil
import time
import os

configurations = {
    "base_url": "https://id.jobstreet.com/id/my-activity/applied-jobs",
    "profile_name": "default",  # this is clean profile. 'default-release' is existing profile but hangs
    "default_wait": 20,
    "short_wait": 3,
    "default_not_available": "N/A",
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


def init_driver(browser="firefox", profile_name="default", headless=False):

    browser = browser.lower()
    if browser not in ["firefox", "chrome"]:
        raise ValueError(
            f"Unsupported browser {browser}. Please use 'firefox' or 'chrome'."
        )

    if profile_name is None:
        profile_name = "default" if browser == "firefox" else "Default"

    logger.info(f"Initializing {browser} driver with profile: {profile_name}")

    try:
        if browser == "firefox":
            return init_firefox_driver(profile_name, headless)
        elif browser == "chrome":
            return init_chrome_driver(profile_name, headless)
        else:
            raise ValueError(f"Unsupported browser {browser}")
    except Exception as e:
        logger.error(f"Error initializing {browser} driver: {e}")
        raise


def init_firefox_driver(use_profile=None, headless=False):
    try:
        options = FirefoxOptions()

        if platform.system() == "Linux":
            profile_dir = os.path.expanduser("~/.mozilla/firefox")
        elif platform.system() == "Darwin":
            profile_dir = os.path.expanduser(
                "~/Library/Application Support/Firefox/Profiles"
            )
        elif platform.system() == "Windows":
            profile_dir = os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles")
        else:
            raise OSError("Unsupported OS for Firefox profiles.")

        if not os.path.exists(profile_dir):
            raise FileNotFoundError(
                f"Firefox profile directory not found: {profile_dir}"
            )

        if os.path.exists(profile_dir):
            for folder in os.listdir(profile_dir):
                if folder.endswith(f".{use_profile}") or use_profile == "default":
                    profile_path = os.path.join(profile_dir, folder)
                    break

        if not profile_path:
            raise FileNotFoundError(
                f"Firefox profile '{use_profile}' not found in {profile_dir}"
            )

        profile = FirefoxProfile(profile_path)
        options.profile = profile

        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")

        options.set_preference("dom.webnotifications.enabled", False)
        options.set_preference("dom.push.enabled", False)
        options.set_preference("permissions.default.desktop-notification", 2)
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)

        driver = webdriver.Firefox(options=options)
        if not headless:
            driver.maximize_window()

        time.sleep(2)
        logger.info(f"Initialized Firefox driver with profile: {use_profile}")
        return driver

    except Exception as e:
        logger.error(f"Error initializing Firefox driver: {e}")
        raise


def init_chrome_driver(profile_name=None, headless=False):
    try:
        options = ChromeOptions()

        if profile_name:
            options.add_argument(f"--profile-directory={profile_name}")

        if platform.system() == "Linux":
            base_dir = os.path.expanduser("~/.config/google-chrome")
        elif platform.system() == "Darwin":  # macOS
            base_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome")
        elif platform.system() == "Windows":
            base_dir = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
        else:
            raise OSError("Unsupported OS for Chrome profiles.")

        if not os.path.exists(base_dir):
            raise FileNotFoundError(f"Chrome profile directory not found: {base_dir}")

        profile_path = os.path.join(base_dir, profile_name)
        if not os.path.exists(profile_path):
            raise FileNotFoundError(
                f"Chrome profile '{profile_name}' not found in {base_dir}"
            )

        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")

        # chrome requires you to set a custom user data directory when using remote debugging
        # to avoid issues with the default user data directory.
        temp_user_data_dir = tempfile.mkdtemp(prefix="chrome_selenium_")

        options.add_argument(f"--user-data-dir={temp_user_data_dir}")
        options.add_argument(f"profile-directory={profile_name}")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("prefs", {"translate": {"enabled": False}})

        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )

        driver = webdriver.Chrome(options=options)

        if headless:
            driver.execute_script(
                """
                Object.defineProperty(navigator, 'userAgent', {
                    get: () => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                });
            """
            )

        time.sleep(2)
        logger.info(f"Initialized Chrome driver with profile: {profile_name}")
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
                    logger.debug(f"Cleanup up chrome temp directory: {dir}")
                except Exception as e:
                    logger.warning(f"Failed to clean temp directory {dir}: {e}")
    except Exception as e:
        logger.warning(f"Error during temp directory cleanup: {e}")
