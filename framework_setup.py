import os
from pathlib import Path

# Define the project structure
folders = [
    "config",
    "features",
    "features/steps",
    "pages",
    "reports",
    "reports/logs",
    "reports/screenshots",
    "testData",
    "utils"
]


files = {
    "requirements.txt": "selenium\nbehave\nallure-behave\nallure-pytest\nallure-python-commons\npytest-html\nfaker\npandas\nPyYAML",
    "behave.ini": """
[behave]\nstdout_capture = true\nstderr_capture = true\nlog_capture = true\nformat = allure_behave.formatter:AllureFormatter\noutfiles = ./reports\nshow_skipped = false\nsummary = true
""",
    "features/environment.py": """import os

from selenium import webdriver
from selenium.common.exceptions import WebDriverException, SessionNotCreatedException, InvalidArgumentException, \
    TimeoutException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.wait import WebDriverWait

import utils.attachments as attachments
from utils.config_reader import SITE_URL, BROWSER
from utils.fake_data import FakeData
from utils.log_util import Logger

logger = Logger().get_logger()
LOG_FILE = Logger.LOG_FILE

def before_all(context):
    pass

def before_scenario(context, scenario):
   #Initialize WebDriver before each scenario (including each Scenario Outline row).
    logger.info(f"Running scenario: {scenario.name}")

    browser = BROWSER.lower()
    remote = bool(os.getenv("CI"))
    selenium_url = os.getenv("SELENIUM_URL") if remote else None

    options = configure_browser_options(browser)
    context.driver = init_driver(browser, options, selenium_url)

    _prepare_driver(context.driver)
    context.row_index = getattr(getattr(scenario, "_row", None), "index", None) - 1 if getattr(scenario, "_row",
                                                                                               None) else None

    faker_instance = FakeData()
    context.test_data = {
        "user": faker_instance.get_user_data(),
        "form": faker_instance.get_form_data(),
        "card": faker_instance.get_user_card_details()
    }

    logger.info(f"Generated fresh test data for scenario. User Email: {context.test_data['user']['email']}")

def _prepare_driver(driver):
    #Maximize window, set waits, navigate to base URL.
    try:
        driver.maximize_window()  # Works in non-headless
    except Exception as e:
        logger.error(f"{e}")  # Ignore if headless
    # Force viewport size regardless of headless mode
    driver.set_window_size(1920, 1080)
    driver.get(SITE_URL)
    WebDriverWait(driver, 25).until(
        lambda _driver: _driver.execute_script("return document.readyState") == "complete"
    )
    logger.info(f"Navigated to {SITE_URL}")


def init_driver(browser, options, selenium_url=None):
    #Create WebDriver instance (remote or local).
    try:
        if selenium_url:
            logger.info(f"Selenium URL: {selenium_url}")
            return webdriver.Remote(command_executor=selenium_url, options=options)

        local_drivers = {
            "chrome": webdriver.Chrome,
            "firefox": webdriver.Firefox
        }
        return local_drivers[browser](options=options)

    except (SessionNotCreatedException, InvalidArgumentException, WebDriverException, TimeoutException) as e:
        logger.error(f"Error creating WebDriver for {browser} ({'remote' if selenium_url else 'local'}): {e}")
        raise e


def configure_browser_options(browser):
    #Return browser-specific options with common args applied.
    option_classes = {
        "chrome": ChromeOptions,
        "firefox": FirefoxOptions
    }
    if browser not in option_classes:
        raise ValueError(f"Unsupported browser: {browser}")

    opts = option_classes[browser]()

    common_args = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-extensions",
        "--dns-prefetch-disable",
        "--headless"
    ]

    chrome_args = [
        "--start-maximized",
        "--window-size=1920,1080",
        "--ignore-certificate-errors",
        "--allow-insecure-localhost",
        "--incognito",
        "--disable-infobars"
    ]
    firefox_args = [
        "-private",
        "--width=1920",
        "--height=1080"
    ]

    for arg in common_args:
        opts.add_argument(arg)

    if browser.lower() == "chrome":
        for arg in chrome_args:
            opts.add_argument(arg)

    elif browser.lower() == "firefox":
        for arg in firefox_args:
            opts.add_argument(arg)
        opts.set_preference("acceptInsecureCerts", True)

    return opts


def after_scenario(context, scenario):
    #Quit browser after each scenario + capture screenshot for reporting.
    try:
        attachments.attach_screenshot(f"{scenario.status} Step Screenshot", scenario.name, context.driver)
        logger.info(f"attaching screenshot of {scenario.name}")
    except Exception as e:
        logger.error(f"Error in taking screenshot: {e}")

    attachments.attach_logs()

    if hasattr(context, "driver"):
        context.driver.quit()


""",
    "features/test.feature":"""Feature: Checkout
  Scenario: checkout with the desired product
    Given I am on the home page
    When I click on the product
    And I click on the add to cart button
    Then I should see the product in the cart
    When I click on the cart icon
    Then I click on the checkout button
""",
    "features/steps/test.py":"""from behave import given,when,then

@given(u'I am on the home page')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given I am on the home page')


@when(u'I click on the product')
def step_impl(context):
    raise NotImplementedError(u'STEP: When I click on the product')


@when(u'I click on the add to cart button')
def step_impl(context):
    raise NotImplementedError(u'STEP: When I click on the add to cart button')


@then(u'I should see the product in the cart')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then I should see the product in the cart')


@when(u'I click on the cart icon')
def step_impl(context):
    raise NotImplementedError(u'STEP: When I click on the cart icon')


@then(u'I click on the checkout button')
def step_impl(context):
    raise NotImplementedError(u'STEP: When I click on the checkout button')
""",
    "pages/__init__.py": "",
    "pages/basePage.py":"""from typing import Tuple, List

from selenium.common import StaleElementReferenceException
from selenium.webdriver import Chrome
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.actions import Actions
from utils.log_util import Logger


class BasePage:

    def __init__(self, driver: Chrome):
        self.driver = driver
        self.timeout = 30
        self.logger = Logger().get_logger()
        self.actions = Actions()

    def do_click(self, locator: Tuple[str, str]):
        #Waits for element to be clickable and clicks it. Retries on Stale Element Reference.
        attempts = 0
        while attempts < 3:  # Try clicking up to 3 times for robustness against StaleElement
            try:
                WebDriverWait(self.driver, self.timeout).until(
                    EC.element_to_be_clickable(locator)
                ).click()
                return  # Click successful, exit loop
            except StaleElementReferenceException:
                self.logger.warning(
                    f"StaleElementReferenceException caught for {locator}. Retrying attempt {attempts + 1}...")
                attempts += 1
            except Exception as e:
                # Catch any other unexpected exception and re-raise immediately
                self.logger.error(
                    f"Failed to click element {locator} due to unexpected error: {type(e).__name__} - {e}")
                raise e

        # If the loop finishes, it means all retries failed due to StaleElementReferenceException.
        # Re-attempt one last time which will raise the final StaleElementReferenceException if it persists.
        self.logger.error(
            f"Failed to click element {locator} after {attempts} retries due to persistent StaleElementReferenceException.")
        WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable(locator)
        ).click()

    def do_send_keys(self, locator: Tuple[str, str], text: str):
        #Waits for element to be visible, clears it, and sends keys.
        element = WebDriverWait(self.driver, self.timeout).until(
            EC.visibility_of_element_located(locator)
        )
        element.clear()
        element.send_keys(text)

    def get_element_text(self, locator: Tuple[str, str]) -> str:
        #Waits for element to be visible and returns its text.
        element = WebDriverWait(self.driver, self.timeout).until(
            EC.visibility_of_element_located(locator)
        )
        return element.text

    def get_element(self, locator: Tuple[str, str]) -> WebElement:
        #Waits for element to be present and returns it.
        return WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located(locator)
        )

    def get_iframe(self, iframe: Tuple[str, str]):
        #Waits for iframe to be present and returns it.
        return WebDriverWait(self.driver, self.timeout).until(
            EC.frame_to_be_available_and_switch_to_it(iframe)
        )

    def get_elements(self, locator: Tuple[str, str]) -> List[WebElement]:
        #Waits for elements to be present and returns the list.
        return WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_all_elements_located(locator)
        )

    def do_hover(self, locator: Tuple[str, str]):
        #Waits for element to be visible and hovers over it.
        element = WebDriverWait(self.driver, self.timeout).until(
            EC.visibility_of_element_located(locator)
        )
        self.actions.hover_to_dest(self.driver, element)""",
    "utils/__init__.py": "",
    "features/__init__.py": "",
    "reports/logs/logfile.log":"",
    "testData/testdata.csv":"",
    "config/config.yaml":"""env:
  site_url: "https://qa1.akhyar.org/"
  selenium_url: "http://selenium:4444/wd/hub"

driver:
  browser: "firefox"

data:
  os_data_csv: "testData/orphan-sponsorship.csv"
  currencies_csv: "testData/currencies.csv"
  ziyarah_data_csv: "testData/ziyarah_form_data.csv"
  user_data_csv: "testData/signed_up_user.csv"
  city_code_json: "testData/country_city_map.json"
""",
    "utils/actions.py":"""from selenium.webdriver import ActionChains


class Actions:

    def hover_to_dest(self, driver, element):
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
""",
    "utils/attachments.py":"""import os
from datetime import datetime

import allure
from selenium.webdriver.common.by import By

from utils.log_util import Logger

logger = Logger().get_logger()

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")


def attach_screenshot(name, scenario_name, driver):
    scc_name = scenario_name.replace(" ", "_")
    file_name = f"{scc_name}_{timestamp}.png"
    folder_path = os.path.join("reports", "screenshots")
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, file_name)  # Ensure directory exists

    screenshot_success = False
    try:
        driver.save_screenshot(file_path)
        screenshot_success = True
    except Exception as e:
        logger.warning(f"Standard screenshot failed ({e}). Attempting element screenshot fallback...")

    if not screenshot_success:
        try:
            logger.info("Attempting fallback: Body element screenshot")
            driver.find_element(By.TAG_NAME, "html").screenshot(file_path)
            screenshot_success = True
        except Exception as e:
            logger.error(f"Fallback body screenshot also failed: {e}")

    if screenshot_success and os.path.exists(file_path):
        # Attach to Allure
        allure.attach.file(file_path, name=name, attachment_type=allure.attachment_type.PNG)
    else:
        logger.error("Could not capture screenshot by any method.")



def attach_logs():
    file_path = Logger().LOG_FILE
    try:
        allure.attach.file(file_path, name="logfile", attachment_type=allure.attachment_type.TEXT)
    except Exception as e:
        logger.error(f"Failed to attach logs because of {e}")""",
    "utils/config_reader.py":"""import logging
import os

import yaml

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

config = {}


def _load_config():
    global config
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")

    if not os.path.exists(config_path):
        logger.error(f"Config file not found at: {config_path}. All config values will be None.")
        config = {}
        return

    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            logger.info(f"Successfully loaded config from {config_path}")
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML config file {config_path}: {e}. All config values will be None.")
        config = {}
    except Exception as e:
        logger.error(
            f"An unexpected error occurred while loading config file {config_path}: {e}. All config values will be None.")
        config = {}


_load_config()


def get_config_value(section: str, key: str, default=None):
    if not isinstance(config, dict):
        logger.warning(f"Config is not a dictionary. Attempted to get [{section}][{key}]. Returning default: {default}")
        return default

    value = config.get(section, {}).get(key, default)
    if value is default and default is not None:
        logger.debug(f"Config key [{section}][{key}] not found, returning default: {default}")
    return value


# Environment
SITE_URL = config["env"]["site_url"]
SELENIUM_URL = config["env"]["selenium_url"]

# Driver
BROWSER = config["driver"]["browser"]

# Data Files
OS_DATA_CSV = config["data"]["os_data_csv"]
CURRENCIES_CSV = config["data"]["currencies_csv"]
ZIYARAH_DATA_CSV = config["data"]["ziyarah_data_csv"]
USER_DATA_CSV = config["data"]["user_data_csv"]
CITIES_DATA_JSON = config["data"]["city_code_json"]
""",
    "utils/csv_util.py":"""import os

import pandas as pd


class CSVUtil:

    def get_test_data(self, file):
        #Reads test data from a CSV file and returns a list of dictionaries.
        return pd.read_csv(file).to_dict(orient="records")

    def set_test_data(self, file, data, col_title):
        #Writes test data to a CSV file.
        pd.DataFrame({col_title: data}).to_csv(file, index=False)

    def update_column(self, file, column_name, cell_value):
        df = pd.DataFrame([{column_name: cell_value}])

        # Check if file exists and is not empty
        file_exists = os.path.isfile(file)
        file_empty = os.path.getsize(file) == 0 if file_exists else True

        df.to_csv(file, index=False, mode='a', header=not file_exists or file_empty)

        return df.to_dict(orient="records")

""",
    "utils/log_util.py":"""import logging
import os
from datetime import datetime


class Logger:

    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # Go one level up
    LOG_DIR = os.path.join(PROJECT_ROOT, "reports", "logs")

    TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
    FILE_NAME = f"logfile_{TIMESTAMP}.log"
    LOG_FILE = os.path.join(LOG_DIR, FILE_NAME)
    _logger = None  # Private variable to hold the logger instance

    def get_logger(self):
        #Returns a single shared logger instance across the framework.
        if Logger._logger is None:
            # Ensure logs directory exists
            if not os.path.exists(Logger.LOG_DIR):
                os.makedirs(Logger.LOG_DIR, exist_ok=True)

            # Create or retrieve a named logger
            logger = logging.getLogger("AutomationLogger")
            logger.setLevel(logging.INFO)

            # Clear existing handlers (to prevent duplicate logs)
            if logger.hasHandlers():
                logger.handlers.clear()

            # Create file handler
            log_file = logging.FileHandler(Logger.LOG_FILE, mode="w")  # Overwrites on each test run
            log_format = logging.Formatter("%(asctime)s : %(levelname)s : %(lineno)d : %(name)s : %(message)s")
            log_file.setFormatter(log_format)

            logger.addHandler(log_file)

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(log_format)
            logger.addHandler(console_handler)

            Logger._logger = logger  # Assign to private variable

        return Logger._logger

"""
}

def create_structure():
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)

    for filepath, content in files.items():
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.strip() + "\n", encoding="utf-8")

    print("✅ Framework structure created successfully.")

# Run the setup
if __name__ == "__main__":

    create_structure()
