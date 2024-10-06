import os
import sys
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from multiprocessing import Process

# Add the parent directory of 'aiscraper' to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import your spiders
from aiscraper.spiders.SeleniumSpider import SeleniumSpider
from aiscraper.spiders.ArticleSpider import ArticleSpider

def run_spider(spider):
    process = CrawlerProcess(get_project_settings())
    process.crawl(spider)
    process.start()

if __name__ == "__main__":
    # Create a process for each spider
    selenium_spider_process = Process(target=run_spider, args=(SeleniumSpider,))
    article_spider_process = Process(target=run_spider, args=(ArticleSpider,))

    # Start the processes
    print("Starting SeleniumSpider process...")
    selenium_spider_process.start()
    selenium_spider_process.join()  # Wait for the SeleniumSpider to finish
    print("SeleniumSpider process finished.")

    print("Starting ArticleSpider process...")
    article_spider_process.start()
    article_spider_process.join()  # Wait for the ArticleSpider to finish
    print("ArticleSpider process finished.")