import time
from dataclasses import dataclass

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from typing import List, Iterable
from selenium_driver import BaseSeleniumDriver

import settings


class ProductLinksPaginationScraper:
    def __init__(self, driver_handler: BaseSeleniumDriver, start_url: str) -> None:
        self.driver_handler = driver_handler
        self.driver = driver_handler.get_webdriver()
        self.start_url = start_url

    def _get_urls(self) -> List[str]:
        elements = self.driver.find_elements(
            by=By.XPATH, value="//a[@class='product-item-link']"
        )
        return [x.get_attribute("href") for x in elements]

    def get_result(self) -> List[str]:
        self.driver.get(self.start_url)
        result = self._get_urls()
        statement = (By.XPATH, "//a[@class='action  next']")
        element = self.driver_handler.wait_for_element(self.driver, statement)
        while element:
            self.driver.get(element.get_attribute("href"))
            result += self._get_urls()
            element = self.driver_handler.wait_for_element(self.driver, statement)
        return result

    def run(self):
        result = self.get_result()
        return result


@dataclass
class ProductData:
    url: str
    title: str
    price: float
    description: str
    images: List[str]


class ProductPaginationScraper:
    def __init__(self, driver_handler: BaseSeleniumDriver) -> None:
        self.driver_handler = driver_handler
        self.driver: WebDriver = driver_handler.get_webdriver()

    def get_title(self) -> str:
        statement = (By.XPATH, "//span[@data-ui-id='page-title-wrapper']")
        element = self.driver_handler.wait_for_element(self.driver, statement)
        return element.text

    def get_price(self) -> float:
        allowed_symbols = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]
        statement = (
            By.XPATH,
            "//div[@class='product-info-price']/div[1]/span[1]/span[1]/span[1]",
        )
        element = self.driver_handler.wait_for_element(self.driver, statement)
        price = "".join(s for s in element.text if s in allowed_symbols).strip(".")
        return float(price)

    def get_description(self) -> str:
        statement = (
            By.XPATH,
            "//div[@class='product attribute description']/div[1]",
        )
        element = self.driver_handler.wait_for_element(self.driver, statement)
        if element:
            statement = (By.TAG_NAME, "p")
            desc_elements = element.find_elements(by=By.TAG_NAME, value="p")
            description = "\n".join([i.text for i in desc_elements])
            return description

    def get_images(self) -> str:
        def get_image_link(num: int = 3):
            statement = (
                By.XPATH,
                f"//div[@class='fotorama__stage__shaft fotorama__grab']/div[{num}]",
            )
            image_div = self.driver_handler.wait_for_element(self.driver, statement)
            return image_div.get_attribute("href")

        def paginate_trough_images():
            image_links = []
            image_links.append(get_image_link(1))
            statement = (By.XPATH, "//div[@class='fotorama__arr fotorama__arr--next']")
            button = self.driver_handler.wait_for_element(self.driver, statement)
            while True:
                button.click()
                time.sleep(settings.WAIT_FOR_IMAGE_SLIDER_TO_LOAD_NEXT_IMAGE)
                link = get_image_link()
                if link in image_links:
                    break
                image_links.append(link)
            return image_links

        def get_image_links() -> List[str]:
            images_on_loading = self.driver.find_elements(
                By.XPATH, "//div[@class='fotorama__stage__shaft fotorama__grab']/div"
            )
            if len(images_on_loading) < 3:
                image_links = [
                    image_div.get_attribute("href") for image_div in images_on_loading
                ]
            else:
                image_links = paginate_trough_images()
            return image_links

        return get_image_links()

    def create_door_data(self, url: List[str]) -> dict:
        for i in range(settings.MAX_RETRIES):
            try:
                self.driver.get(url)
                url = self.driver.current_url
                title = self.get_title()
                price = self.get_price()
                description = self.get_description()
                images = self.get_images()
                return ProductData(
                    url=url,
                    title=title,
                    price=price,
                    description=description,
                    images=images,
                ).__dict__
            except Exception as e:
                print(i, url)
                continue

    def run(self, links: Iterable) -> List[dict]:
        doors = [self.create_door_data(link) for link in links]
        return doors
