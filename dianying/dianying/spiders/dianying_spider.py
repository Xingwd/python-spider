import scrapy
from dianying.items import DianyingItem
from scrapy.contrib.loader import ItemLoader

class DianyingSpider(scrapy.Spider):
    name = "dianying"
    allowed_domains = ["dy2018.com"]
    start_urls = [
        "https://www.dy2018.com/html/gndy/dyzz"
    ]

    # 程序入口
    def parse(self, response):
        # 遍历 最新电影 的所有页面
        for page in response.xpath("//select/option/@value").extract():
            url = "https://www.dy2018.com" + page
            yield scrapy.Request(url, callback=self.parsePage)

    # 处理单个页面
    def parsePage(self, response):
        # 获取到该页面的所有电影的详情页链接
        for link in response.xpath('//a[@class="ulink"]/@href').extract():
            url = "https://www.dy2018.com" + link
            yield scrapy.Request(url, callback=self.parseChild)

    # 处理单个电影详情页
    def parseChild(self, response):
        # 获取电影信息，并提取数据
        l = ItemLoader(item=DianyingItem(), response=response)
        l.add_value('url', response.url)
        l.add_xpath('title', '//div[@class="title_all"]/h1/text()')
        l.add_xpath('magnet', '//div[@id="Zoom"]//a[starts-with(@href, "magnet:")]/@href')
        yield l.load_item()

