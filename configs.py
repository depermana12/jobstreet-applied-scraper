from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium import webdriver
import platform
import logging
import time
import os

configurations = {
    "base_url": "https://id.jobstreet.com/id/my-activity/applied-jobs",
    "profile_name": "default",  # this is clean profile. 'default-release' is existing profile but hangs
    "default_wait": 20,
    "short_wait": 3,
    "default_not_available": "N/A",
}


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


def init_driver(use_profile="default"):
    options = Options()

    firefox_profile_dir = None
    if platform.system() == "Linux":
        firefox_profile_dir = os.path.expanduser("~/.mozilla/firefox")
    elif platform.system() == "Darwin":  # macOS
        firefox_profile_dir = os.path.expanduser(
            "~/Library/Application Support/Firefox/Profiles"
        )
    elif platform.system() == "Windows":
        firefox_profile_dir = os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles")
    else:
        print("Unsupported OS. Please use Linux, macOS, or Windows.")
        return None

    if not firefox_profile_dir:
        raise FileNotFoundError(
            "Firefox profile directory not found. Please ensure Firefox is installed."
        )

    profile_path = None
    if os.path.exists(firefox_profile_dir):
        for folder in os.listdir(firefox_profile_dir):
            if folder.endswith(f".{use_profile}") or use_profile == "default":
                profile_path = os.path.join(firefox_profile_dir, folder)
                break

    if not profile_path:
        raise FileNotFoundError(
            f"Firefox profile '{use_profile}' not found in {firefox_profile_dir}"
        )

    profile = FirefoxProfile(profile_path)
    options.profile = profile

    options.add_argument("--start-maximized")
    options.set_preference("dom.webnotifications.enabled", False)
    options.set_preference("dom.push.enabled", False)
    options.set_preference("permissions.default.desktop-notification", 2)
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)

    driver = webdriver.Firefox(options=options)
    time.sleep(2)
    return driver


def init_firefox_driver(use_profile="default", headless=False):
    try:
        options = Options()

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

        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")

        options.set_preference("dom.webnotifications.enabled", False)
        options.set_preference("dom.push.enabled", False)
        options.set_preference("permissions.default.desktop-notification", 2)
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)

        options.profile = profile
        driver = webdriver.Firefox(options=options)
        if not headless:
            driver.maximize_window()

        time.sleep(2)
        logging.info(f"Initialized Firefox driver with profile: {use_profile}")
        return driver

    except Exception as e:
        logging.error(f"Error initializing Firefox driver: {e}")
        raise


def init_chrome_driver(profile_name="Default", headless=False):
    try:
        options = Options()

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
        options.add_argument(f"user-data-dir={base_dir}")
        options.add_argument(f"profile-directory={profile_name}")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        driver = webdriver.Chrome(options=options)

        time.sleep(2)
        logging.info(f"Initialized Chrome driver with profile: {profile_name}")
        return driver

    except Exception as e:
        logging.error(f"Error initializing Chrome driver: {e}")
        raise


def list_all_profiles(browser="firefox"):
    try:
        browser = browser.lower()

        if browser.lower() == "firefox":

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

            if os.path.exists(profile_dir):
                return [
                    folder
                    for folder in os.listdir(profile_dir)
                    if os.path.isdir(os.path.join(profile_dir, folder))
                ]
            else:
                logging.warning(f"Firefox profile directory not found: {profile_dir}")
                return []

        elif browser.lower() == "chrome":

            if platform.system() == "Linux":
                profile_dir = os.path.expanduser("~/.config/google-chrome")
            elif platform.system() == "Darwin":
                profile_dir = os.path.expanduser(
                    "~/Library/Application Support/Google/Chrome"
                )
            elif platform.system() == "Windows":
                profile_dir = os.path.expandvars(
                    r"%LOCALAPPDATA%\Google\Chrome\User Data"
                )
            else:
                raise OSError("Unsupported OS for Chrome profiles.")

            if os.path.exists(profile_dir):
                return [
                    folder
                    for folder in os.listdir(profile_dir)
                    if os.path.isdir(os.path.join(profile_dir, folder))
                    and (folder.startswith("Profile") or folder == "Default")
                ]
            else:
                logging.warning(f"Chrome profile directory not found: {profile_dir}")
                return []

        else:
            raise ValueError(f"Unsupported browser: {browser}")

    except Exception as e:
        logging.error(f"Error listing {browser} profiles: {e}")
        return []
