# Scrapy实战二
本项目是 [Scrapy实战一](https://github.com/Xingwd/python-spider/tree/scrapy-2) 的升级版，仅供学习使用。

本项目在 Scrapy实战一 的基础上优化了保存到json的数据格式，并引入 [Item Loaders](http://scrapy-chs.readthedocs.io/zh_CN/latest/topics/loaders.html#module-scrapy.contrib.loader) 和 [Item Pipeline](http://scrapy-chs.readthedocs.io/zh_CN/latest/topics/item-pipeline.html#item-pipeline)


## 改变保存到json的数据格式
在 Scrapy实战一 中，我们使用以下命令保存数据：

    scrapy crawl dianying -o items.json
这里有一个问题，就是在items.json文件中，中文的数据格式是unicode编码格式，这严重影响了可读性，所以这里做一些改动，使数据保存为可读的格式。

创建 customconfigs.py，写入代码：

    '''
    改变默认的 JSON Exporter 的数据格式
    '''

    from scrapy.exporters import JsonLinesItemExporter

    class CustomJsonLinesItemExporter(JsonLinesItemExporter):
        def __init__(self, file, **kwargs):
            # 这里只需要将超类的ensure_ascii属性设置为False即可
            super(CustomJsonLinesItemExporter, self).__init__(file, ensure_ascii=False, **kwargs)

同时要在settings.py文件中启用新的Exporter类，追加代码：

    FEED_EXPORTERS = {
        'json': 'dianying.customconfigs.CustomJsonLinesItemExporter',
    }

再次尝试：

    scrapy crawl dianying -o items.json

查看items.json，可以看到已经是可读的中文了。


## Item Loaders
Item Loaders提供了一种便捷的方式填充抓取到的 :Items 。 虽然Items可以使用自带的类字典形式API填充，但是Items Loaders提供了更便捷的API， 可以分析原始数据并对Item进行赋值。

从另一方面来说， Items 提供保存抓取数据的 **容器** ， 而 Item Loaders提供的是 **填充** 容器的机制。

Item Loaders提供的是一种灵活，高效的机制，可以更方便的被spider或source format (HTML, XML, etc)扩展，并override更易于维护的、不同的内容分析规则。


### Item Loaders用法样例
下面是在 Spider 中典型的Item Loader的用法, 假设 已经声明 ExampleItem item:

    from scrapy.contrib.loader import ItemLoader
    from example.items import ExampleItem

    def parse(self, response):
        l = ItemLoader(item=ExampleItem(), response=response)
        l.add_xpath('name', '//div[@class="product_name"]')
        l.add_xpath('name', '//div[@class="product_title"]')
        l.add_xpath('price', '//p[@id="price"]')
        l.add_css('stock', 'p#stock]')
        l.add_value('last_updated', 'today') # you can also use literal values
        return l.load_item()

快速查看这些代码之后,我们可以看到发现 name 字段被从页面中两个不同的XPath位置提取:
- //div[@class="product_name"]
- //div[@class="product_title"]

换言之,数据通过用 add_xpath() 的方法,把从两个不同的XPath位置提取的数据收集起来. 这是将在以后分配给 name 字段中的数据｡

之后,类似的请求被用于 price 和 stock 字段 (后者使用 CSS selector 和 add_css() 方法), 最后使用不同的方法 add_value() 对 last_update 填充文本值( today ).

最终, 当所有数据被收集起来之后, 调用 ItemLoader.load_item() 方法, 实际上填充并且返回了之前通过调用 add_xpath(), add_css(), and add_value() 所提取和收集到的数据的Item.


### 使用Item Loaders
要使用Item Loader, 你必须先将它实例化. 你可以使用类似字典的对象(例如: Item or dict)来进行实例化, 或者不使用对象也可以, 当不用对象进行实例化的时候,Item会自动使用 ItemLoader.default_item_class 属性中指定的Item 类在Item Loader constructor中实例化.

然后,你开始收集数值到Item Loader时,通常使用 Selectors. 你可以在同一个item field 里面添加多个数值;Item Loader将知道如何用合适的处理函数来“添加”这些数值.

现在直接写代码，改造在 Scrapy实战一 中写好的 dianying_spider 的中 parseChild函数 ：

    import scrapy
    from dianying.items import DianyingItem
    from scrapy.contrib.loader import ItemLoader

    class DianyingSpider(scrapy.Spider):
    ......

        # 处理单个电影详情页
        def parseChild(self, response):
            # 获取电影信息，并提取数据
            l = ItemLoader(item=DianyingItem(), response=response)
            l.add_value('url', response.url)
            l.add_xpath('title', '//div[@class="title_all"]/h1/text()')
            l.add_xpath('magnet', '//div[@id="Zoom"]//a[starts-with(@href, "magnet:")]/@href')
            yield l.load_item()

现在尝试再次爬取dy2018.com，您将看到爬取到的网站信息被成功输出，并且与改造代码之前的输出一致:

    scrapy crawl dianying

简单存储爬取的数据：

    scrapy crawl dianying -o items.json


## Item Pipeline
当Item在Spider中被收集之后，它将会被传递到Item Pipeline，一些组件会按照一定的顺序执行对Item的处理。

每个item pipeline组件(有时称之为“Item Pipeline”)是实现了简单方法的Python类。他们接收到Item并通过它执行一些行为，同时也决定此Item是否继续通过pipeline，或是被丢弃而不再进行处理。

以下是item pipeline的一些典型应用：
- 清理HTML数据
- 验证爬取的数据(检查item包含某些字段)
- 查重(并丢弃)
- 将爬取结果保存到数据库中


### Item pipeline用法样例
#### 验证价格，同时丢弃没有价格的item
让我们来看一下以下这个假设的pipeline，它为那些不含税(price_excludes_vat 属性)的item调整了 price 属性，同时丢弃了那些没有价格的item:

    from scrapy.exceptions import DropItem

    class PricePipeline(object):

        vat_factor = 1.15

        def process_item(self, item, spider):
            if item['price']:
                if item['price_excludes_vat']:
                    item['price'] = item['price'] * self.vat_factor
                return item
            else:
                raise DropItem("Missing price in %s" % item)


#### 将item写入JSON文件
以下pipeline将所有(从所有spider中)爬取到的item，存储到一个独立地 items.jl 文件，每行包含一个序列化为JSON格式的item:

    import json

    class JsonWriterPipeline(object):

        def __init__(self):
            self.file = open('items.jl', 'wb')

        def process_item(self, item, spider):
            line = json.dumps(dict(item)) + "\n"
            self.file.write(line)
            return item


### 使用Item pipeline
pipeline相关代码写到 pipelines.py 文件中。

为了启用一个Item Pipeline组件，你必须将它的类添加到配置文件setting.py的 ITEM_PIPELINES 配置，就像下面这个例子:

    ITEM_PIPELINES = {
        'myproject.pipelines.PricePipeline': 300,
        'myproject.pipelines.JsonWriterPipeline': 800,
    }
分配给每个类的整型值，确定了他们运行的顺序，item按数字从低到高的顺序，通过pipeline，通常将这些数字定义在0-1000范围内。

#### 处理抓取的数据
观察存储数据的items.json文件，可以发现，有大量的item的magnet字段的内容是空的，所以为了数据的有效性，我们需要做一些处理：不存储magnet字段内容为空的item项。

代码实现，编辑 pipelines.py 文件：

    from scrapy.exceptions import DropItem

    ......

    class MagnetPipeline(object):
        def process_item(self, item, spider):
            # 如果页面中没有magnet的信息，那么对应的item就没有 'magnet' 这个key
            # 所以这里判断item的所有key中有没有 'magnet' 即可
            if 'magnet' in item.keys():
                return item
            else:
                # 丢弃或者不再处理item
                raise DropItem("Without magnet in {0}".format(item))

启用MagnetPipeline组件：

    ITEM_PIPELINES = {
        'dianying.pipelines.MagnetPipeline': 1,
    }

重新存储爬取的数据：

    scrapy crawl dianying -o items.json
> 注意：这个命令会把数据追加到item.json文件中，并不会覆盖原有数据，如果只想要新的数据内容，请删除item.json文件，再执行命令


#### 自定义pipeline保存数据到json文件
目前为止，我们都是使用命令将数据保存到一个json文件的，其实也可以使用pipeline将数据保存到json文件。

代码实现，编辑 pipelines.py 文件，追加代码：

    import json

    ......

    class JsonWriterPipeline(object):
        def __init__(self):
            self.file = open('pipeitems.json', 'wb')

        def process_item(self, item, spider):
            line = json.dumps(dict(item)) + "\n"
            # 这里要求写入bytes类型，所以将str类型转换成bytes类型
            self.file.write(line.encode())
            return item

启用JsonWriterPipeline组件，添加一行 "'dianying.pipelines.JsonWriterPipeline':2,"：

    ITEM_PIPELINES = {
        'dianying.pipelines.MagnetPipeline': 1,
        'dianying.pipelines.JsonWriterPipeline':2,
    }

启动爬虫：

    scrapy crawl dianying

完成之后，查看 pipeitems.json 文件，可以看到已经成功将数据写进去。

不过写进 pipeitems.json 的数据并不可读，并且没有关闭文件的操作，所以改造MagnetPipeline：

    from dianying.customconfigs import CustomJsonLinesItemExporter

    ......

    class JsonWriterPipeline(object):
        # 定义开始爬虫的行为
        def open_spider(self, spider):
            self.file = open('pipeitems.json', 'wb')
            self.exporter = CustomJsonLinesItemExporter(self.file)
            self.exporter.start_exporting()

        # 定义爬虫结束的行为
        def close_spider(self, spider):
            self.exporter.finish_exporting()
            self.file.close()

        # 定义爬虫过程中的行为
        def process_item(self, item, spider):
            self.exporter.export_item(item)
            return item

可以再次启动爬虫，完成之后，查看 pipeitems.json 文件中的数据，可以发现已经变成可读的了



#### 保存数据到mysql数据库
很多情况下，我们需要将抓取的数据直接存储到数据库，在scrapy官方文档Item Pipeline章节中，给出了 [Write items to MongoDB](https://doc.scrapy.org/en/latest/topics/item-pipeline.html#write-items-to-mongodb)，有兴趣的道友可以看看。

这里，我们写数据到mysql数据库，来体验pipeline的功能。

以下代码的数据库连接部分是参照笔者创建的数据库信息，数据库创建过程的详细信息请看 create_table.sql 文件。如有不同，请注意相应调整。

代码实现，编辑 pipelines.py 文件，追加代码：

    from scrapy.conf import settings
    import pymysql

    ......

    class MysqlPipeline(object):

        def open_spider(self, spider):
            host = settings['MYSQL_HOST']
            user = settings['MYSQL_USER']
            psd = settings['MYSQL_PASSWORD']
            db = settings['MYSQL_DB']
            c = settings['CHARSET']
            port = settings['MYSQL_PORT']
            # 数据库连接
            self.db = pymysql.connect(host=host,user=user,passwd=psd,db=db,charset=c,port=port)
            # 数据库游标
            self.cursor = self.db.cursor()

        def close_spider(self, spider):
            self.db.close()

        def process_item(self, item, spider):
            title = item['title']
            url = item['url']
            magnet = item['magnet']

            # sql 语句
            insert_sql = """INSERT INTO dianying(dianying_title,
                     dianying_url, dianying_magnet)
                     VALUES (%s, %s, %s)"""
            try:
                # 执行sql语句
                self.cursor.execute(insert_sql, (title, url, magnet))
                # 提交到数据库执行
                self.db.commit()
            except:
                # 如果发生错误则回滚
                self.db.rollback()
            return item

编辑 settings.py 文件，追加代码：

    # mysql数据库信息
    MYSQL_HOST='192.168.1.201'
    MYSQL_USER='xwd'
    MYSQL_PASSWORD='xwd'
    MYSQL_PORT =3306
    MYSQL_DB='dianying'
    CHARSET='utf8'

启用MysqlPipeline组件，添加一行 "'dianying.pipelines.MysqlPipeline':3,"：

    ITEM_PIPELINES = {
        'dianying.pipelines.MagnetPipeline': 1,
        'dianying.pipelines.JsonWriterPipeline':2,
        'dianying.pipelines.MysqlPipeline':3,
    }

---
持续更新地址：https://github.com/Xingwd/python-spider/tree/scrapy-3