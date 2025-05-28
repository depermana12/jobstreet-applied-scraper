import subprocess
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import os

configurations = {
    "base_url": "https://id.jobstreet.com/id/my-activity/applied-jobs",
    "email": "deddiapermana97@gmail.com",
    "firefox_profile_dir": os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles"),
    "profile_name": "default",  # this is clean profile. 'default-release' is existing profile but hangs
}


def init_driver(use_profile: str):
    options = Options()

    firefox_profile_dir = configurations["firefox_profile_dir"]

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
