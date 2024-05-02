import xml.etree.ElementTree as ET
import scrapy
from scrapy_splash import SplashRequest

from cloth.locators import Locators

gender_type = {
    'Women Home': 'Female',
    'Men Home': 'Male',
    'Kids Home': 'Kids'
}


class FarfetchSpider(scrapy.Spider):
    name = "cloth"
    url = ["https://www.farfetch.com/ca/shopping/women/dresses-1/items.aspx?page=1",
           "https://www.farfetch.com/ca/shopping/women/dresses-1/items.aspx?page=2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = []

    def start_requests(self):
        for url in self.url:
            yield SplashRequest(url, self.parse, args={'wait': 0.5})

    def parse(self, response):
        second_page = response.xpath(Locators.SECOND_PAGE).get()
        product_type = response.xpath(Locators.FIRST_PAGE).get() + '/' + second_page + '/'
        gpc = '/' + second_page
        products = response.xpath('//li[@data-testid="productCard"]')

        for product in products:
            product_link = 'https://www.farfetch.com' + product.xpath(
                './/div//a[@data-component="ProductCardLink"]/@href').get()
            yield SplashRequest(product_link, self.parse_product, meta={'product_link': product_link,
                                                                        'product_type': product_type,
                                                                        'google_product_category': gpc})

    def parse_product(self, response):
        item = {
            'id': response.xpath(Locators.ID).get().strip(),
            'item_group_id': response.xpath(Locators.ITEM_GROUP_ID).get().strip(),
            'mpn': response.xpath(Locators.MPN).get().strip(),
            'title': response.xpath(Locators.TITLE).get(),
            'description': response.xpath(Locators.DESCRIPTION).get(),
            'image_link': response.xpath(Locators.IMAGE_LINK).get(),
            'additional_image_link': response.xpath(Locators.ADDITIONAL_IMAGE_LINK).get(),
            'link': response.meta['product_link'],
            'gender': gender_type[response.xpath(Locators.CLOTH_GENDER_TYPE).get()],
            'availability': self.check_availability(response.xpath(Locators.AVAILABILITY).get()),
            'brand': response.xpath(Locators.BRAND).get(),
            'price': response.xpath(Locators.PRICE).get(),
            'product_type': response.meta['product_type'] + response.xpath(Locators.PRODUCT_CATEGORY).get(),
            'google_product_category': response.xpath(Locators.PRODUCT_CATEGORY).get()
                                       + response.meta['google_product_category'],
        }

        self.items.append(item)
        return item

    @staticmethod
    def check_availability(availability):
        if availability:
            return availability
        else:
            return 'In stock'

    def closed(self, reason):
        root = ET.Element("items")
        for item_data in self.items:
            xml_item = ET.SubElement(root, "item")
            for key, value in item_data.items():
                child = ET.SubElement(xml_item, key)
                child.text = value if value else ''

        tree = ET.ElementTree(root)
        tree.write("items.xml", xml_declaration=True)
