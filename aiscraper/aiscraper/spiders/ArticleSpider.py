import json
import scrapy
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from scrapy.selector import Selector
from scrapy.crawler import CrawlerProcess

class ArticleSpider(scrapy.Spider):
    name = 'article_spider'
    
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    }
    def __init__(self, *args, **kwargs):
        super(ArticleSpider, self).__init__(*args, **kwargs)

        # Prepare the selenium driver 
        gecko_driver_path = "./geckodriver.exe"  
        options = Options()
        options.add_argument('-headless')

        self.driver = webdriver.Firefox(service=Service(gecko_driver_path), options=options)
        #Initialize the json array
        with open('articles_content.json', 'w') as f:
            json.dump([], f)
    
    def start_requests(self):
        with open('article_links.txt','r') as f:
            urls=f.readlines()
        for url in urls:
            yield scrapy.Request(url=url.strip(),callback=self.parse)
    
    def parse(self, response):
        self.driver.get(response.url)
        page_source = self.driver.page_source

        # Pass the more "complete" content back to Scrapy
        selector = Selector(text=page_source)

        article_header=selector.css("h1.ArticleHeader-headline::text").get()
        article_text = selector.css("p::text").getall()
        article_text="".join(article_text)

        article_data = {
            'url': response.url,
            'header': article_header,
            'content': article_text
        }

        with open('articles_content.json', 'r') as f:
            articles = json.load(f)

        articles.append(article_data)

        # Add to the json array
        with open('articles_content.json', 'w') as f:
            json.dump(articles, f, indent=4)

    def closed(self, reason):
        # Quit the driver when the spider is closed
        self.driver.quit()

# Run the spider
process = CrawlerProcess()
process.crawl(ArticleSpider)
process.start()
