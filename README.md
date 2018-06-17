# Scrapy-抓取电影下载链接
本项目是 python scrapy 爬虫 练手项目，仅供学习使用。

本项目的爬取目标是 [电影天堂-最新电影](https://www.dy2018.com/html/gndy/dyzz/) 的所有电影的title，详情页的link以及每个详情页的电影简介和磁力链接。

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

首先根据需要从 电影天堂-最新电影 获取到的数据对item进行建模。 我们需要从 最新电影 中获取所有电影的title，详情页的link以及每个详情页的电影简介和磁力链接。 对此，在item中定义相应的字段。编辑 dianying 目录中的 items.py 文件:

    import scrapy

    class DianyingItem(scrapy.Item):
        title = scrapy.Field()
        link = scrapy.Field()
        jianjie = scrapy.Field()
        magnet = scrapy.Field()

一开始这看起来可能有点复杂，但是通过定义item， 您可以很方便的使用Scrapy的其他方法。而这些方法需要知道您的item的定义。


## 编写爬虫(Spider)
Spider是用户编写用于从单个网站(或者一些网站)爬取数据的类。

其包含了一个用于下载的初始URL，如何跟进网页中的链接以及如何分析页面中的内容， 提取生成 item 的方法。

为了创建一个Spider，您必须继承 scrapy.Spider 类， 且定义以下三个属性:
- name: 用于区别Spider。 该名字必须是唯一的，您不可以为不同的Spider设定相同的名字。
- start_urls: 包含了Spider在启动时进行爬取的url列表。 因此，第一个被获取到的页面将是其中之一。 后续的URL则从初始的URL获取到的数据中提取。
- parse() 是spider的一个方法。 被调用时，每个初始URL完成下载后生成的 Response 对象将会作为唯一的参数传递给该函数。 该方法负责解析返回的数据(response data)，提取数据(生成item)以及生成需要进一步处理的URL的 Request 对象。


### 爬取
进入项目的根目录，执行下列命令启动spider:

    scrapy crawl dianying

crawl dianying 启动用于爬取 dy2018.com 的spider，您将得到类似的输出:

    2018-06-17 08:26:01 [scrapy.core.engine] INFO: Spider opened
    2018-06-17 08:26:01 [scrapy.extensions.logstats] INFO: Crawled 0 pages (at 0 pages/min), scraped 0 items (at 0 items/min)
    2018-06-17 08:26:01 [scrapy.extensions.telnet] DEBUG: Telnet console listening on 127.0.0.1:6023
    2018-06-17 08:26:01 [scrapy.core.engine] DEBUG: Crawled (404) <GET https://www.dy2018.com/robots.txt> (referer: None)
    2018-06-17 08:26:01 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.dy2018.com/html/gndy/dyzz/> (referer: None)
    2018-06-17 08:26:01 [scrapy.core.engine] INFO: Closing spider (finished)

查看输出，可以看到输出的log中包含定义在 start_urls 的初始URL，并且与spider中是一一对应的。在log中可以看到其没有指向其他页面( (referer:None) )。

除此之外，更有趣的事情发生了。就像我们 parse 方法指定的那样，有一个包含url所对应的内容的文件被创建了: dyzz 。

> 这里的dyzz文件，打开后可能有编码问题，切换成GBK编码格式就不会有乱码信息了


### 提取Item
#### Selectors选择器简介
从网页中提取数据有很多方法。Scrapy使用了一种基于 [XPath](https://www.w3.org/TR/xpath/all/) 和 [CSS](https://www.w3.org/TR/selectors/) 表达式机制: [Scrapy Selectors](http://scrapy-chs.readthedocs.io/zh_CN/latest/topics/selectors.html#topics-selectors) 。 关于selector和其他提取机制的信息请参考 [Selector文档](http://scrapy-chs.readthedocs.io/zh_CN/latest/topics/selectors.html#topics-selectors) 。

这里给出XPath表达式的例子及对应的含义:
- /html/head/title: 选择HTML文档中 \<head> 标签内的 \<title> 元素
- /html/head/title/text(): 选择上面提到的 \<title> 元素的文字
- //td: 选择所有的 \<td> 元素
- //div[@class="mine"]: 选择所有具有 class="mine" 属性的 div 元素

上边仅仅是几个简单的XPath例子，XPath实际上要比这远远强大的多。 如果您想了解的更多，我们推荐 [这篇XPath教程](http://www.w3school.com.cn/xpath/index.asp) 。

为了配合XPath，Scrapy除了提供了 Selector 之外，还提供了方法来避免每次从response中提取数据时生成selector的麻烦。

Selector有四个基本的方法:
- xpath(): 传入xpath表达式，返回该表达式所对应的所有节点的selector list列表 。
- css(): 传入CSS表达式，返回该表达式所对应的所有节点的selector list列表.
- extract(): 序列化该节点为unicode字符串并返回list。
- re(): 根据传入的正则表达式对数据进行提取，返回unicode字符串list列表。


#### 在Shell中尝试Selector选择器
为了介绍Selector的使用方法，接下来我们将要使用内置的 [Scrapy shell](http://scrapy-chs.readthedocs.io/zh_CN/latest/topics/shell.html#topics-shell) 。Scrapy Shell需要您预装好IPython(一个扩展的Python终端)。

您需要进入项目的根目录，执行下列命令来启动shell:

    scrapy shell "https://www.dy2018.com/html/gndy/dyzz/"

> 当您在终端运行Scrapy时，请一定记得给url地址加上引号，否则包含参数的url(例如 & 字符)会导致Scrapy运行失败。

shell的输出类似:

    2018-06-17 15:51:56 [scrapy.core.engine] DEBUG: Crawled (200) <GET https://www.dy2018.com/html/gndy/dyzz/> (referer: None)
    [s] Available Scrapy objects:
    [s]   scrapy     scrapy module (contains scrapy.Request, scrapy.Selector, etc)
    [s]   crawler    <scrapy.crawler.Crawler object at 0x0000000003A9AF98>
    [s]   item       {}
    [s]   request    <GET https://www.dy2018.com/html/gndy/dyzz/>
    [s]   response   <200 https://www.dy2018.com/html/gndy/dyzz/>
    [s]   settings   <scrapy.settings.Settings object at 0x0000000004D92C18>
    [s]   spider     <DianyingSpider 'dianying' at 0x501ce80>
    [s] Useful shortcuts:
    [s]   fetch(url[, redirect=True]) Fetch URL and update local objects (by default, redirects are followed)
    [s]   fetch(req)                  Fetch a scrapy.Request and update local objects
    [s]   shelp()           Shell help (print this help)
    [s]   view(response)    View response in a browser

当shell载入后，您将得到一个包含response数据的本地 response 变量。输入 response.body 将输出response的包体， 输出 response.headers 可以看到response的包头。

更为重要的是，当输入 response.selector 时， 您将获取到一个可以用于查询返回数据的selector(选择器)， 以及映射到 response.selector.xpath() 、 response.selector.css() 的 快捷方法(shortcut): response.xpath() 和 response.css() 。

同时，shell根据response提前初始化了变量 sel 。该selector根据response的类型自动选择最合适的分析规则(XML vs HTML)。

让我们来试试:

    In [1]: sel.xpath('//title')
    Out[1]: [<Selector xpath='//title' data='<title>电影 / 最新电影_电影天堂-迅雷电影下载</title>'>]

    In [2]: sel.xpath('//title').extract()
    Out[2]: ['<title>电影 / 最新电影_电影天堂-迅雷电影下载</title>']

    In [3]: sel.xpath('//title/text()')
    Out[3]: [<Selector xpath='//title/text()' data='电影 / 最新电影_电影天堂-迅雷电影下载'>]

    In [4]: sel.xpath('//title/text()').extract()
    Out[4]: ['电影 / 最新电影_电影天堂-迅雷电影下载']


#### 提取数据
现在，我们来尝试从这些页面中提取些有用的数据。

您可以在终端中输入 response.body 来观察HTML源码并确定合适的XPath表达式。不过，这任务非常无聊且不易。您可以考虑使用Firefox的Firebug扩展来使得工作更为轻松。详情请参考 [使用Firebug进行爬取](http://scrapy-chs.readthedocs.io/zh_CN/latest/topics/firebug.html#topics-firebug) 和 [借助Firefox来爬取](http://scrapy-chs.readthedocs.io/zh_CN/latest/topics/firefox.html#topics-firefox) 。

这里笔者使用的是Chrome的XPath Helper扩展，很方便。

在查看了网页的源码后，您会发现所有电影的title，详情页的link的信息的 XPath 路径是：

    //a[@class="ulink"]

进入单个详情页进行分析，可以发现：
- 单个详情页的简介的信息的 XPath 路径是：

      //div[@id="Zoom"]/p[36]/text()
- 单个详情页的磁力链接的信息的 XPath 路径是：

      //div[@id="Zoom"]/table[2]/tbody/tr/td/a/text()

获取所有电影的title，详情页的link的信息:

    sel.xpath('//a[@class="ulink"]').extract()

之前提到过，每个 .xpath() 调用返回selector组成的list，因此我们可以拼接更多的 .xpath() 来进一步获取某个节点。我们将在下边使用这样的特性:

    for sel in response.xpath('//a[@class="ulink"]'):
        title = sel.xpath('@title').extract()
        link = sel.xpath('@href').extract()
        print title, link

> 关于嵌套selctor的更多详细信息，请参考 [嵌套选择器(selectors)](http://scrapy-chs.readthedocs.io/zh_CN/latest/topics/selectors.html#topics-selectors-nesting-selectors) 以及 [选择器(Selectors)](http://scrapy-chs.readthedocs.io/zh_CN/latest/topics/selectors.html#topics-selectors) 文档中的 [使用相对XPaths](http://scrapy-chs.readthedocs.io/zh_CN/latest/topics/selectors.html#topics-selectors-relative-xpaths) 部分。

在我们的spider中加入这段代码:

    import scrapy

    class DianyingSpider(scrapy.spiders.Spider):
        name = "dianying"
        allowed_domains = ["dy2018.com"]
        start_urls = [
            "https://www.dy2018.com/html/gndy/dyzz/"
        ]

        def parse(self, response):
            for sel in response.xpath('//a[@class="ulink"]'):
                title = sel.xpath('@title').extract()
                link = sel.xpath('@href').extract()
                print(title, link)

现在尝试再次爬取dy2018.com，您将看到爬取到的网站信息被成功输出:

    scrapy crawl dianying

#### 提取子页面数据


### 使用item
Item 对象是自定义的python字典。 您可以使用标准的字典语法来获取到其每个字段的值。(字段即是我们之前用Field赋值的属性):

    >>> item = DianyingItem()
    >>> item['title'] = 'Example title'
    >>> item['title']
    'Example title'

一般来说，Spider将会将爬取到的数据以 Item 对象返回。所以为了将爬取的数据返回，我们最终的代码将是:

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

现在对dy2018.com进行爬取将会产生 DianyingItem 对象:

    2018-06-17 16:38:36 [scrapy.core.scraper] DEBUG: Scraped from <200 https://www.dy2018.com/html/gndy/dyzz/>
    {'link': ['/i/99632.html'], 'title': ['2018年美国动作片《金蝉脱壳2》BD中英双字']}
    2018-06-17 16:38:36 [scrapy.core.scraper] DEBUG: Scraped from <200 https://www.dy2018.com/html/gndy/dyzz/>
    {'link': ['/i/99626.html'], 'title': ['2018年欧美6.5分剧情片《火狐一号出击》BD中英双字']}
    2018-06-17 16:38:36 [scrapy.core.scraper] DEBUG: Scraped from <200 https://www.dy2018.com/html/gndy/dyzz/>
    {'link': ['/i/99621.html'], 'title': ['2018年国产动作片《低压槽：欲望之城》HD国语中字']}


## 保存爬取到的数据
最简单存储爬取的数据的方式是使用 [Feed exports](http://scrapy-chs.readthedocs.io/zh_CN/latest/topics/feed-exports.html#topics-feed-exports):

    scrapy crawl dianying -o items.json

该命令将采用 [JSON](https://en.wikipedia.org/wiki/JSON) 格式对爬取的数据进行序列化，生成 items.json 文件。

在类似本篇教程里这样小规模的项目中，这种存储方式已经足够。 如果需要对爬取到的item做更多更为复杂的操作，您可以编写 [Item Pipeline](http://scrapy-chs.readthedocs.io/zh_CN/latest/topics/item-pipeline.html#topics-item-pipeline) 。 类似于我们在创建项目时对Item做的，用于您编写自己的 tutorial/pipelines.py 也被创建。 不过如果您仅仅想要保存item，您不需要实现任何的pipeline。


## 下一步
本篇教程仅介绍了Scrapy的基础，还有很多特性没有涉及。请查看 [初窥Scrapy](http://scrapy-chs.readthedocs.io/zh_CN/latest/intro/overview.html#intro-overview) 章节中的 [还有什么？](http://scrapy-chs.readthedocs.io/zh_CN/latest/intro/overview.html#topics-whatelse) 部分,大致浏览大部分重要的特性。

接着，我们推荐您把玩一个例子(查看 [例子](http://scrapy-chs.readthedocs.io/zh_CN/latest/intro/overview.html#topics-whatelse))，而后继续阅读 [基本概念](http://scrapy-chs.readthedocs.io/zh_CN/latest/index.html#section-basics) 。

这里的例子已经被弃用，请参看 [新例子](https://github.com/scrapy/quotesbot)