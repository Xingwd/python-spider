import scrapy
from dianying.items import DianyingItem

class DianyingSpider(scrapy.Spider):
    name = "dianying"
    allowed_domains = ["dy2018.com"]
    start_urls = [
        "https://www.dy2018.com/html/gndy/dyzz/"
    ]

    def parse(self, response):
        for sel in response.xpath('//a[@class="ulink"]'):
            item = DianyingItem()
            item['title'] = sel.xpath('@title').extract()
            item['link'] = sel.xpath('@href').extract()
            yield item

