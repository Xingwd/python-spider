# Scrapy-抓取电影下载链接
本项目是 python scrapy 爬虫 练手项目，仅供学习使用。

本项目的爬取目标是 [电影天堂-最新电影](https://www.dy2018.com/html/gndy/dyzz/) 的所有电影的详情页的url，片名和磁力链接。

话不多说，接下来就直接开始吧

## 创建项目
在开始爬取之前，您必须创建一个新的Scrapy项目。 进入您打算存储代码的目录中，运行下列命令:

    scrapy startproject dianying

该命令将会创建包含下列内容的 tutorial 目录:

    dianying/
        scrapy.cfg
        dianying/
            __init__.py
            items.py
            pipelines.py
            settings.py
            spiders/
                __init__.py
                ...

这些文件分别是:
- scrapy.cfg: 项目的配置文件
- dianying/: 该项目的python模块。之后您将在此加入代码。
- dianying/items.py: 项目中的item文件.
- dianying/pipelines.py: 项目中的pipelines文件.
- dianying/settings.py: 项目的设置文件.
- dianying/spiders/: 放置spider代码的目录.


## 定义Item
Item 是保存爬取到的数据的容器；其使用方法和python字典类似， 并且提供了额外保护机制来避免拼写错误导致的未定义字段错误。

类似在ORM中做的一样，您可以通过创建一个 scrapy.Item 类， 并且定义类型为 scrapy.Field 的类属性来定义一个Item。 (如果不了解ORM, 不用担心，您会发现这个步骤非常简单)

首先根据需要从 电影天堂-最新电影 获取到的数据对item进行建模。 我们需要从 最新电影 中获取所有电影的详情页的url，片名和磁力链接。 对此，在item中定义相应的字段。编辑 dianying 目录中的 items.py 文件:

    import scrapy

    class DianyingItem(scrapy.Item):
        url = scrapy.Field()
        name = scrapy.Field()
        magnet = scrapy.Field()

一开始这看起来可能有点复杂，但是通过定义item， 您可以很方便的使用Scrapy的其他方法。而这些方法需要知道您的item的定义。


## 编写爬虫(Spider)
Spider是用户编写用于从单个网站(或者一些网站)爬取数据的类。

其包含了一个用于下载的初始URL，如何跟进网页中的链接以及如何分析页面中的内容， 提取生成 item 的方法。

为了创建一个Spider，您必须继承 scrapy.Spider 类， 且定义以下三个属性:
- name: 用于区别Spider。 该名字必须是唯一的，您不可以为不同的Spider设定相同的名字。
- start_urls: 包含了Spider在启动时进行爬取的url列表。 因此，第一个被获取到的页面将是其中之一。 后续的URL则从初始的URL获取到的数据中提取。
- parse() 是spider的一个方法。 被调用时，每个初始URL完成下载后生成的 Response 对象将会作为唯一的参数传递给该函数。 该方法负责解析返回的数据(response data)，提取数据(生成item)以及生成需要进一步处理的URL的 Request 对象。


### 分析网页
您可以在终端中输入 response.body 来观察HTML源码并确定合适的XPath表达式。不过，这任务非常无聊且不易。您可以考虑使用Firefox的Firebug扩展来使得工作更为轻松。详情请参考 [使用Firebug进行爬取](http://scrapy-chs.readthedocs.io/zh_CN/latest/topics/firebug.html#topics-firebug) 和 [借助Firefox来爬取](http://scrapy-chs.readthedocs.io/zh_CN/latest/topics/firefox.html#topics-firefox) 。

这里笔者使用的是Chrome的XPath Helper扩展，很方便。

在查看了[网页](https://www.dy2018.com/html/gndy/dyzz/)的源码后，您会发现所有电影的详情页的link的信息的 XPath 路径是：

    //a[@class="ulink"]/@href

进入单个详情页进行分析，可以发现：
- 单个详情页的url的组成结构是 https://www.dy2018.com 与 详情页的link 的字符串拼接
- 单个详情页的片名的信息的 XPath 路径是：

      //div[@id="Zoom"]/p[3]/text()
- 单个详情页的磁力链接的信息的 XPath 路径是：

      //div[@id="Zoom"]/table[2]/tbody/tr/td/a/text()


### 提取数据
现在，我们来尝试从这些页面中提取些有用的数据。

获取所有电影的详情页的url的信息:

    for link in response.xpath('//a[@class="ulink"]/@href').extract():
        url = "https://www.dy2018.com" + link

获取具体详情页的片名和磁力链接：

    for sel in response.xpath('//div[@id="Zoom"]'):
        name = (sel.xpath('p[3]/text()').extract())[0]
        magnet = (sel.xpath('table[2]/tbody/tr/td/a/@href').extract())[0]

提取数据的大概逻辑就是这样了，接下来是代码实现。
在我们的spiders目录下创建dianying_spider，并加入这段代码:

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


现在尝试爬取dy2018.com，您将看到爬取到的网站信息被成功输出:

    scrapy crawl dianying


## 保存爬取到的数据
最简单存储爬取的数据的方式是使用 [Feed exports](http://scrapy-chs.readthedocs.io/zh_CN/latest/topics/feed-exports.html#topics-feed-exports):

    scrapy crawl dianying -o items.json

该命令将采用 [JSON](https://en.wikipedia.org/wiki/JSON) 格式对爬取的数据进行序列化，生成 items.json 文件。
