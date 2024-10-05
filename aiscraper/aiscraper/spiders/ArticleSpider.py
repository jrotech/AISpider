import json
import re
import scrapy
import os
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
        },
        'LOG_LEVEL': 'WARNING'  # Set Scrapy logging level to WARNING
    }
    
    def __init__(self, *args, **kwargs):
        super(ArticleSpider, self).__init__(*args, **kwargs)

        # Prepare the selenium driver 
        options = Options()
        options.add_argument('-headless')
        options.set_preference("log.level", "fatal")  # Set selenium log level to suppress logs
        service = Service(executable_path='../geckodriver.exe', log_path=os.devnull) # Set geckodriver log level to suppress logs
        self.driver = webdriver.Firefox(service=service, options=options)
        #Initialize the json array
        with open('../resources/articles_content.json', 'w') as f:
            json.dump([], f)
    
    def start_requests(self):
        with open('../resources/article_links.txt','r') as f:
            urls=f.readlines()
        for url in urls:
            yield scrapy.Request(url=url.strip(),callback=self.parse)

    def clean_text(self, text):
        # Remove non-ASCII characters
        return re.sub(r'[^\x00-\x7F]+', '', text)
    
    def parse(self, response):
        self.driver.get(response.url)
        page_source = self.driver.page_source
       
        
        if "/video/" in response.url:
            return
        
        # Pass the more "complete" content back to Scrapy
        selector = Selector(text=page_source)
        article_header = selector.css("h1.ArticleHeader-headline::text").get()
       
        if selector.css("span.xyz-data::text").getall() != []:
            article_text = selector.css("span.xyz-data::text").getall()
        else:
            article_text = selector.xpath("//div[@class='group']//p//text()").getall()
            article_text = " ".join(article_text)

        article_text = "".join(article_text)
        
        # Clean the text to remove non-ASCII characters
        article_text = self.clean_text(article_text)
        article_text

        article_data = {
            'url': response.url,
            'header': article_header,
            'content': article_text
        }

        try:
            with open('../resources/articles_content.json', 'r') as f:
                articles = json.load(f)
        except FileNotFoundError:
            articles = []

        articles.append(article_data)

        # Add to the json array
        with open('../resources/articles_content.json', 'w') as f:
            json.dump(articles, f,  ensure_ascii=False, indent=4)

    def closed(self, reason):
        # Quit the driver when the spider is closed
        self.driver.quit()

# Run the spider
if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(ArticleSpider)
    process.start()
