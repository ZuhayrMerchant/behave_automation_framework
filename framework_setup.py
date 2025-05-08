import os
from pathlib import Path

# Define the project structure
folders = [
    "config",
    "features",
    "features/steps",
    "logs",
    "pages",
    "reports",
    "reports/screenshots",
    "testData",
    "utils"
]


files = {
    "requirements.txt": "selenium\nbehave\nallure-behave\nallure-pytest\nallure-python-commons\npytest-html\nfaker\npandas",
    "behave.ini": """
[behave]\nstdout_capture = true\nstderr_capture = true\nlog_capture = true\nformat = allure_behave.formatter:AllureFormatter\noutfiles = ./reports\nshow_skipped = false\nsummary = true
""",
    "features/environment.py": """from selenium import webdriver
from utils.config_reader import BASE_URL, BROWSER
from utils.log_util import Logger
import utils.attachments as attachments

log = Logger.get_logger()
LOG_FILE = Logger.LOG_FILE


def before_all(context):
    # Initialize WebDriver before tests start using values from config.ini.
    log.info("Initializing WebDriver")
    if BROWSER == "chrome":
        context.driver = webdriver.Chrome()
    elif BROWSER == "firefox":
        context.driver = webdriver.Firefox()

    context.driver.maximize_window()
    context.driver.implicitly_wait(10)
    context.driver.get(BASE_URL)
    log.info(f'Navigated to {BASE_URL}')


def after_all(context):
    # Quit WebDriver after all tests are completed.
    log.info("Closing WebDriver")
    context.driver.quit()


def after_scenario(context, scenario):
    # Take a screenshot if a Behave scenario fails.
    if scenario.status == "failed":
        attachments.attach_screenshot("Failed Step Screenshot", scenario.name, context.driver)

    if scenario.status == "passed":
        attachments.attach_screenshot("Passed Step Screenshot", scenario.name, context.driver)

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
    "pages/testPage.py":"""from typing import ClassVar
from selenium.webdriver import Chrome

class TestPage:
    driver: ClassVar[Chrome]

    def __init__(self, driver: Chrome):
        self.driver = driver""",
    "utils/__init__.py": "",
    "features/__init__.py": "",
    "logs/logfile.log":"",
    "testData/testdata.csv":"",
    "config/config.ini":"""[DEFAULT]
base_url = https://google.com
browser = chrome

# add file names here
[FILES]
user_data_csv = testData/testdata.csv""",
    "utils/actions.py":"""from selenium.webdriver import ActionChains


class Actions:

    @staticmethod
    def hover_to_dest(driver, element):
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
""",
    "utils/attachments.py":"""import os
import allure

def attach_screenshot(name, scenario_name, driver):
    file_name = scenario_name.replace(" ", "_") + ".png"
    file_path = os.path.join("reports/screenshots", file_name)

    os.makedirs("reports/screenshots", exist_ok=True)  # Ensure directory exists
    driver.save_screenshot(file_path)

    # Attach to Allure
    allure.attach.file(file_path, name=name, attachment_type=allure.attachment_type.PNG)""",
    "utils/config_reader.py":"""import configparser

# Initialize ConfigParser
config = configparser.ConfigParser()
config.read("config/config.ini")

# Read values from config.ini
BASE_URL = config["DEFAULT"]["base_url"]
BROWSER = config["DEFAULT"]["browser"]
USER_DATA_CSV = config["FILES"]["user_data_csv"]

# Function to retrieve values dynamically
def get_config_value(key):
    # Returns configuration values from config.ini.
    return config["DEFAULT"].get(key, None)
""",
    "utils/data_reader.py":"""import pandas as pd

def get_test_data(file):
    #  Reads test data from a CSV file and returns a list of dictionaries.
    return pd.read_csv(file).to_dict(orient="records")
""",
    "utils/log_util.py":"""import logging
import os

class Logger:

    LOG_DIR = "logs"
    LOG_FILE = os.path.join(LOG_DIR, "logfile.log")
    _logger = None  # Private variable to hold the logger instance

    @staticmethod
    def get_logger():
        # Returns a single shared logger instance across the framework.
        if Logger._logger is None:
            # Ensure logs directory exists
            if not os.path.exists(Logger.LOG_DIR):
                os.makedirs(Logger.LOG_DIR)

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