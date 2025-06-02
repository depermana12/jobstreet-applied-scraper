import re


def email_validation(email: str):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email.strip()) is not None


def max_validation(max_page: str):
    if max_page.lower() == "all":
        return None

    if max_page.isdigit() and int(max_page) > 0:
        return int(max_page)
    return None
