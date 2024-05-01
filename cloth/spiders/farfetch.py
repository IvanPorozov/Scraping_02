import scrapy
from scrapy_splash import SplashRequest

from cloth.locators import Locators


class FarfetchSpider(scrapy.Spider):
    name = "cloth"
    url = ["https://www.farfetch.com/ca/shopping/women/dresses-1/items.aspx"]

    def start_requests(self):
        for url in self.url:
            yield SplashRequest(url, self.parse, args={'wait': 0.5})

    def parse(self, response):
        second_page = response.xpath(Locators.SECOND_PAGE).get()
        product_type = response.xpath(Locators.FIRST_PAGE).get() + '/' + second_page + '/'
        gpc = ' > ' + second_page
        products = response.xpath('//li[@data-testid="productCard"]')

        for product in products:
            product_link = 'https://www.farfetch.com' + product.xpath(
                './/div//a[@data-component="ProductCardLink"]/@href').get()
            yield SplashRequest(product_link, self.parse_product, meta={'product_link': product_link,
                                                                        'product_type': product_type,
                                                                        'google_product_category': gpc})

    def parse_product(self, response):
        yield {
            'id': response.xpath(Locators.ID).get().strip(),
            'item_group_id': response.xpath(Locators.ITEM_GROUP_ID).get().strip(),
            'mpn': response.xpath(Locators.MPN).get().strip(),
            'title': response.xpath(Locators.TITLE).get(),
            'description': response.xpath(Locators.DESCRIPTION).get(),
            'image_link': response.xpath(Locators.IMAGE_LINK).get(),
            'additional_image_link': response.xpath(Locators.ADDITIONAL_IMAGE_LINK).get(),
            'link': response.meta['product_link'],
            'gender': 'women',
            'availability': self.check_availability(response.xpath(Locators.AVAILABILITY).get()),
            'brand': response.xpath(Locators.BRAND).get(),
            'price': response.xpath(Locators.PRICE).get(),
            'product_type': response.meta['product_type'] + response.xpath(Locators.PRODUCT_CATEGORY).get(),
            'google_product_category': response.xpath(Locators.PRODUCT_CATEGORY).get()
                                       + response.meta['google_product_category'],
        }

    @staticmethod
    def check_availability(availability):
        if availability:
            return availability
        else:
            return 'In stock'
