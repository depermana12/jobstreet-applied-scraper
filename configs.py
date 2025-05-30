import subprocess
import time
from selenium import webdriver
import platform
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import os

configurations = {
    "base_url": "https://id.jobstreet.com/id/my-activity/applied-jobs",
    "profile_name": "default",  # this is clean profile. 'default-release' is existing profile but hangs
    "default_wait": 20,
    "short_wait": 3,
    "default_not_available": "N/A",
}


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
