import json

from pathlib import Path

import settings

from scraper import ProductLinksPaginationScraper, ProductPaginationScraper, ProductData
from selenium_driver import SeleniumChromeDriver
from typing import List


def parse_good_links() -> List[str]:
    driver_handler = SeleniumChromeDriver()
    scraper = ProductLinksPaginationScraper(
        driver_handler=driver_handler,
        start_url="https://www.fastcabinetdoors.com/cabinet-doors.html?p=1",
    )
    scraper.run()


def write_goods_links():
    links = parse_good_links()
    base_path = settings.BASE_DIR / "data/"
    base_path.mkdir(exist_ok=True)
    content = ", ".join(links)
    file_path = base_path / "goods_links.txt"
    file_path.write_text(content)


def get_goods_links() -> List[str]:
    file_path = settings.BASE_DIR / "data/" / "goods_links.txt"
    links = file_path.read_text(encoding="utf-8").split(",")
    return links


def parse_door_data() -> List[ProductData]:
    links = get_goods_links()
    driver_handler = SeleniumChromeDriver()
    return ProductPaginationScraper(driver_handler=driver_handler).run(links=links)


def main():
    # write_goods_links()
    doors = parse_door_data()
    write_to = settings.BASE_DIR / "data" / "doors.json"
    with open(write_to, "w") as f:
        json.dump(doors, f)


if __name__ == "__main__":
    main()
