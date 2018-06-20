# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from dianying.customconfigs import CustomJsonLinesItemExporter
from scrapy.conf import settings  # 引入配置，因为数据库的一些连接信息写在settings文件里
import pymysql


class DianyingPipeline(object):
    def process_item(self, item, spider):
        return item


class MagnetPipeline(object):
    def process_item(self, item, spider):
        # 如果页面中没有magnet的信息，那么对应的item就没有 'magnet' 这个key
        # 所以这里判断item的所有key中有没有 'magnet' 即可
        if 'magnet' in item.keys():
            return item
        else:
            # 丢弃或者不再处理item
            raise DropItem("Without magnet in {0}".format(item))


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