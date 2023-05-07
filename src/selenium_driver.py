import abc

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.options import BaseOptions

import settings

from typing import Optional, Tuple, Union


class BaseSeleniumDriver(abc.ABC):
    def __init__(
        self,
        options: Optional[webdriver.ChromeOptions] = None,
    ) -> None:
        self.options = options

    @abc.abstractmethod
    def _get_webdriver_options(self) -> BaseOptions:
        pass

    @abc.abstractmethod
    def get_webdriver(self) -> WebDriver:
        pass

    def wait_for_element(
        self, driver: WebDriver, statement: Tuple[str, str]
    ) -> Union[WebElement, None]:
        try:
            element = WebDriverWait(driver, settings.WAIT_FOR_ELEMNT).until(
                EC.presence_of_element_located(statement)
            )
            return element
        except Exception as E:
            print(E)
            raise (E)


class SeleniumChromeDriver(BaseSeleniumDriver):
    def _get_webdriver_options(self) -> webdriver.ChromeOptions:
        return self.options or webdriver.ChromeOptions()

    def get_webdriver(self) -> webdriver.Chrome:
        options = self._get_webdriver_options()
        driver = webdriver.Chrome(
            options=options,
            service=Service(ChromeDriverManager().install()),
        )
        return driver
