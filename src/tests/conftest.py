import logging
import os
import allure
import pytest
from selenium import webdriver
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
import requests
import time

DRIVERS = os.path.expanduser("~\\Downloads\\drivers")
path_to_opencart_yml = os.path.expanduser("~\\proj\\opencart\\")
path_to_selenoid = os.path.expanduser("~\\proj\\selenoid\\")

# configure output log file
logging.basicConfig(level=logging.INFO, filename="log3.log")


def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome", choices=["chrome", "firefox", "opera"])
    parser.addoption("--url", action="store", default="")
    parser.addoption("--selenoid_run", action="store_true", default=True)
    parser.addoption("--bversion", action="store", default=None)
    parser.addoption("--vnc", action="store_true", default=True)
    parser.addoption("--selenoid_logs", action="store_true", default=False)
    parser.addoption("--videos", action="store_true", default=False)


@allure.step("Configure url (use docker if needed)")
@pytest.fixture(scope="session")
def url(request):
    target_url = request.config.getoption("--url")
    logger = logging.getLogger("url_handler")
    # if url empty -> run opencart in docker
    if target_url:
        logger.info(f"Tests run with url: {target_url}")
        return target_url
    else:
        logger.info(f"Tests run on local opencart docker container")
        opencart_url = f"http://{os.environ['OPENCART_HOST']}:{os.environ['OPENCART_PORT']}/"

        # wait when docker finally loading
        for i in range(1, 30):
            try:
                requests.get(opencart_url).status_code == 200
                logger.info("Network access to opencart is OK. Run tests.")
                return opencart_url
            except requests.ConnectionError:
                logger.info(f"Failed connect to opencart in docker. Attempt {i}/30 Retry...")
                time.sleep(1)
        raise EnvironmentError(f"Connection fail. Url: {opencart_url}")


@allure.step("Selenoid handler working")
@pytest.fixture(scope="session")
def selenoid_handler(request):
    selenoid_run = request.config.getoption("--selenoid_run")
    if selenoid_run:
        logger = logging.getLogger("selenoid_handler")
        bversion = request.config.getoption("--bversion")
        selenoid_ip = os.environ['EXECUTOR_IP']
        vnc = request.config.getoption("--vnc")
        sel_logs = request.config.getoption("--selenoid_logs")
        videos = request.config.getoption("--videos")
        logger.info(f"Run tests on Selenoid server {selenoid_ip}")
        return {"vnc": vnc, "sel_logs": sel_logs, "videos": videos, "selenoid_ip": selenoid_ip, "bversion": bversion}
    else:
        return None


@allure.step("Configure driver")
@pytest.fixture
def browser(request, selenoid_handler):
    _browser = request.config.getoption("--browser")
    logger = logging.getLogger("browser_fixture")
    test_name = request.node.name
    logger.info(f"Started test: {test_name}")

    caps = {
            "browserName": _browser,
            "browserVersion": selenoid_handler["bversion"],
            "screenResolution": "1280x1024",
            "name": "selenoid test run",
            "selenoid:options": {
                "sessionTimeout": "20s",
                "enableVNC": selenoid_handler["vnc"],
                "enableVideo": selenoid_handler["videos"],
                "enableLog": selenoid_handler["sel_logs"]
            }
        }
    driver = webdriver.Remote(
            command_executor=f"http://{selenoid_handler['selenoid_ip']}:4444/wd/hub",
            desired_capabilities=caps
        )

    def final():
        logger.info(f"Finished test: {test_name}")
        driver.quit()

    request.addfinalizer(final)
    logger.info(
        f"Target browser: {driver.capabilities['browserName']} and version: {driver.capabilities['browserVersion']}")
    driver = EventFiringWebDriver(driver, ExceptionListener())
    return driver


@pytest.fixture(autouse=True)
def get_environment(browser, request):
    if request.config.getoption("--selenoid_run"):
        _executor = "selenoid"
    else:
        _executor = "other"
    with open('allure-results/environment.properties', 'w') as f:
        f.write(f"Browser={browser.capabilities['browserName']}\n")
        f.write(f"Browser.Version={browser.capabilities['browserVersion']}\n")
        f.write(f'Executor={_executor}')


# attach screenshot on fail test
class ExceptionListener(AbstractEventListener):
    def on_exception(self, exception, driver):
        allure.attach(
            name=f"{exception}",
            body=driver.get_screenshot_as_png(),
            attachment_type=allure.attachment_type.PNG
        )
