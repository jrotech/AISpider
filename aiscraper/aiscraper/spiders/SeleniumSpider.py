import os
import scrapy
import logging
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from scrapy.selector import Selector
from scrapy.crawler import CrawlerProcess

class SeleniumSpider(scrapy.Spider):
    name = 'selenium_spider'
    start_urls = [
        "https://www.cnbc.com/banks/",
        "https://www.cnbc.com/investing/",
        "https://www.cnbc.com/wealth/",
        "https://www.cnbc.com/real-estate/",
        "https://www.cnbc.com/financial-advisors/",
        "https://www.cnbc.com/trader-talk/",
        "https://www.cnbc.com/earnings/",
        "https://www.cnbc.com/rising-risks/",
        "https://www.cnbc.com/fintech/",
        "https://www.cnbc.com/stocks/"
    ]
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        },
        'LOG_LEVEL': 'WARNING'
    }

    def __init__(self, *args, **kwargs):
        super(SeleniumSpider, self).__init__(*args, **kwargs)

        # Prepare the selenium driver 
        current_dir = os.path.dirname(os.path.abspath(__file__))
        gecko_driver_path = os.path.join(current_dir, 'geckodriver.exe')
        logging.info(f"GeckoDriver path: {gecko_driver_path}")
        options = Options()
        options.add_argument('-headless')
        options.set_preference("log.level", "fatal")  # Set selenium log level to suppress logs
        service = Service(executable_path=gecko_driver_path, log_path=os.devnull)  # Set geckodriver log level to suppress logs
        self.driver = webdriver.Firefox(service=service, options=options)
        logging.info("Selenium WebDriver initialized")

    def parse(self, response):
        # Use the selenium driver to load the link
        logging.info(f"Loading URL with Selenium: {response.url}")
        self.driver.get(response.url)
        page_source = self.driver.page_source

        # Pass the more "complete" content back to Scrapy
        selector = Selector(text=page_source)

        # Extract article links
        article_links = selector.css("a.Card-title::attr(href)").getall()

        # Debugging: Print the number of links found
        logging.info(f"Found {len(article_links)} links")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        links_file = os.path.join(current_dir, '../resources/article_links.txt')
        with open(links_file, 'a') as f:  # Use 'a' to append to the file
            for link in article_links:
                f.write(f"{link}\n")
        logging.info(f"Article links written to {links_file}")

    def closed(self, reason):
        # Quit the driver when the spider is closed
        self.driver.quit()
        logging.info(f"WebDriver closed due to: {reason}")

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(SeleniumSpider)
    process.start()