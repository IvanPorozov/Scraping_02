from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from cloth.spiders.farfetch import FarfetchSpider


def main():
    process = CrawlerProcess(get_project_settings())
    process.crawl(FarfetchSpider)
    process.start()


if __name__ == '__main__':
    main()
