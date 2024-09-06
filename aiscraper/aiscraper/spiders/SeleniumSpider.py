import scrapy
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from scrapy.selector import Selector
from scrapy.crawler import CrawlerProcess

class SeleniumSpider(scrapy.Spider):
    name = 'selenium_spider'
    
    start_urls = [f"https://www.cnbc.com/economy/"]
    
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    }
    def __init__(self, *args, **kwargs):
        super(SeleniumSpider, self).__init__(*args, **kwargs)

        # Prepare the selenium driver 
        gecko_driver_path = "./geckodriver.exe"  # Adjusted path
        options = Options()
        options.add_argument('-headless')

        self.driver = webdriver.Firefox(service=Service(gecko_driver_path), options=options)
    
    def parse(self, response):
        # Ignore the possibly incomplete scan made by Scrapy, but keep the link
        # Use the selenium driver to load the link
        print(f"Loading URL with Selenium: {response.url}")
        self.driver.get(response.url)
        page_source = self.driver.page_source
        self.driver.quit()

        # Pass the more "complete" content back to Scrapy
        selector = Selector(text=page_source)

        # Extract article links
        article_links = selector.css("a.Card-title::attr(href)").getall()

        # Debugging: Print the number of links found
        print(f"Found {len(article_links)} links")

        with open('article_links.txt', 'w') as f:
             for link in article_links:
                 f.write(f"{link}\n")

# Run the spider
process = CrawlerProcess()
process.crawl(SeleniumSpider)
process.start()
