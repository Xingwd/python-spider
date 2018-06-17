import scrapy
from dianying.items import DianyingItem

class DianyingSpider(scrapy.Spider):
    name = "dianying"
    allowed_domains = ["dy2018.com"]
    start_urls = [
        "https://www.dy2018.com/html/gndy/dyzz/"
    ]

    def parse(self, response):
        for link in response.xpath('//a[@class="ulink"]/@href').extract():
            url = "https://www.dy2018.com" + link
            yield scrapy.Request(url, callback=self.parseChild)

    def parseChild(self, response):
        for sel in response.xpath('//div[@id="Zoom"]'):
            items = DianyingItem()
            items['url'] = response.url
            items['name'] = (sel.xpath('p[3]/text()').extract())[0]
            items['magnet'] = (sel.xpath('table[2]/tbody/tr/td/a/@href').extract())[0]
            yield items