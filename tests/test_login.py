import os

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.fixture
def browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,800")
    remote_url = os.getenv("SELENIUM_REMOTE_URL")
    if remote_url:
        driver = webdriver.Remote(command_executor=remote_url, options=options)
    else:
        # Selenium Manager automatically locates/downloads the matching driver.
        driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    try:
        yield driver
    finally:
        driver.quit()


def open_page(browser, path="/"):
    base_url = os.getenv("BASE_URL", "http://localhost:5000").rstrip("/")
    browser.get(base_url + path)


def element(browser, element_id):
    return WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.ID, element_id))
    )


def assert_message(browser, expected, success=False):
    message = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.ID, "message"))
    )
    assert message.text == expected
    assert ("success" if success else "error") in message.get_attribute("class").split()
    # A response must never echo the submitted password back into the form.
    assert element(browser, "password").get_attribute("value") == ""


@pytest.mark.parametrize(
    "email,password,expected,success",
    [
        ("admin@example.com", "admin123", "Login successful!", True),
        ("admin@example.com", "wrong-password", "Invalid email or password.", False),
        ("unknown@example.com", "admin123", "Invalid email or password.", False),
        ("", "", "Email and password are required.", False),
        ("", "admin123", "Email and password are required.", False),
        ("admin@example.com", "", "Email and password are required.", False),
        ("not-an-email", "admin123", "Enter a valid email address.", False),
    ],
    ids=["valid-login", "wrong-password", "unknown-email", "both-empty",
         "empty-email", "empty-password", "invalid-email-format"],
)
def test_login(browser, email, password, expected, success):
    open_page(browser)
    element(browser, "email").send_keys(email)
    element(browser, "password").send_keys(password)
    element(browser, "login-button").click()
    assert_message(browser, expected, success)


def test_password_visibility(browser):
    open_page(browser)
    password = element(browser, "password")
    password.send_keys("admin123")
    assert password.get_attribute("type") == "password"
    toggle = element(browser, "toggle-password")
    toggle.click()
    WebDriverWait(browser, 10).until(lambda _: password.get_attribute("type") == "text")
    assert toggle.text == "Hide password"
    assert toggle.get_attribute("aria-pressed") == "true"
    assert password.get_attribute("value") == "admin123"
    toggle.click()
    WebDriverWait(browser, 10).until(lambda _: password.get_attribute("type") == "password")
    assert toggle.text == "Show password"
    assert toggle.get_attribute("aria-pressed") == "false"
    assert password.get_attribute("value") == "admin123"


def test_remember_me(browser):
    open_page(browser)
    checkbox = element(browser, "remember-me")
    assert not checkbox.is_selected()
    checkbox.click()
    assert checkbox.is_selected()
    checkbox.click()
    assert not checkbox.is_selected()
    checkbox.click()
    element(browser, "email").send_keys("admin@example.com")
    element(browser, "password").send_keys("admin123")
    element(browser, "login-button").click()
    assert_message(browser, "Login successful!", success=True)
    assert element(browser, "remember-me").is_selected()
    assert element(browser, "email").get_attribute("value") == "admin@example.com"


def test_forgot_password(browser):
    open_page(browser)
    element(browser, "forgot-password").click()
    message = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.ID, "reset-message"))
    )
    assert message.text == (
        "Password reset is a demonstration. No email is sent. "
        "Use admin@example.com / admin123 to sign in."
    )
    element(browser, "back-to-login").click()
    assert element(browser, "login-button").is_displayed()


@pytest.mark.parametrize(
    "overrides,accept_terms,expected,success",
    [
        ({}, True, "Registration successful (demo only). No account was saved.", True),
        ({"full-name": "", "email": "", "password": "", "confirm-password": "", "phone": ""},
         True, "All registration fields are required.", False),
        ({"email": "invalid-email"}, True, "Enter a valid email address.", False),
        ({"password": "short", "confirm-password": "short"}, True,
         "Password must contain at least 8 characters.", False),
        ({"confirm-password": "different123"}, True, "Passwords do not match.", False),
        ({"phone": "12345abc90"}, True, "Phone number must contain exactly 10 digits.", False),
        ({}, False, "You must accept the terms and conditions.", False),
    ],
    ids=["success", "empty-fields", "invalid-email", "short-password",
         "password-mismatch", "invalid-phone", "terms-required"],
)
def test_registration(browser, overrides, accept_terms, expected, success):
    # Each case starts a fresh browser and submits its own complete form.
    open_page(browser)
    element(browser, "register-link").click()
    fields = {"full-name": "Lab Student", "email": "student@example.com",
              "password": "student123", "confirm-password": "student123",
              "phone": "9876543210"}
    fields.update(overrides)
    for field_id, value in fields.items():
        element(browser, field_id).send_keys(value)
    assert not element(browser, "terms").is_selected()
    if accept_terms:
        element(browser, "terms").click()
    element(browser, "register-button").click()
    assert_message(browser, expected, success)
    assert element(browser, "confirm-password").get_attribute("value") == ""
