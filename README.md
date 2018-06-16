# Scrapy入门教程
本笔记是跟随[scrapy官网](http://scrapy-chs.readthedocs.io/zh_CN/latest/intro/tutorial.html)学习的第一个案例

本篇教程中将带您完成下列任务:
1. 创建一个Scrapy项目
2. 定义提取的Item
3. 编写爬取网站的 spider 并提取 Item
4. 编写 Item Pipeline 来存储提取到的Item(即数据)


## 创建项目
在开始爬取之前，您必须创建一个新的Scrapy项目。 进入您打算存储代码的目录中，运行下列命令:

    scrapy startproject tutorial

