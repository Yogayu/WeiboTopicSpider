# encoding=utf-8
import re
import datetime
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from weiboTopicSpider.items import WeibotopicspiderItem


class Spider(CrawlSpider):
    name = "weibo_topic_spider"
    host = "http://weibo.cn"
    allowed_domains = ["weibo.cn"]
    search_url = 'http://weibo.cn/search/mblog'
    max_page = 200
    keywords = ['#两会#']

    def start_requests(self):
    	for keyword in self.keywords:
    		url = '{url}?hideSearchFrame=&keyword={keyword}&sort=hot&page=1'.format(url=self.search_url, keyword=keyword)
    	yield Request(url,callback=self.parse_detail)

    def parse_detail(self, response):
        """ 抓取微博数据 """
        selector = Selector(response)
        tweets = selector.xpath('body/div[@class="c" and @id]')
        for tweet in tweets:
            tweetsItems = WeibotopicspiderItem()
            id = tweet.xpath('@id').extract_first()  # 微博ID
            content = tweet.xpath('div/span[@class="ctt"]/text()').extract()  # 微博内容
            like = re.findall(u'\u8d5e\[(\d+)\]', tweet.extract())  # 点赞数
            transfer = re.findall(u'\u8f6c\u53d1\[(\d+)\]', tweet.extract())  # 转载数
            others = tweet.xpath('div/span[@class="ct"]/text()').extract_first()  # 求时间和使用工具（手机或平台）

            tweetsItems["ID"] = id
            tweetsItems["_id"] = id
            if content:
                tweetsItems["Content"] = content.strip(u"[\u4f4d\u7f6e]")  # 去掉最后的"[位置]"
            # if cooridinates:
            #     cooridinates = re.findall('center=([\d|.|,]+)', cooridinates)
            #     if cooridinates:
            #         tweetsItems["Co_oridinates"] = cooridinates[0]
            if like:
                tweetsItems["Like"] = int(like[0])
            if transfer:
                tweetsItems["Transfer"] = int(transfer[0])
            if comment:
                tweetsItems["Comment"] = int(comment[0])
            if others:
                others = others.split(u"\u6765\u81ea")
                tweetsItems["PubTime"] = others[0]
                if len(others) == 2:
                    tweetsItems["Tools"] = others[1]
            yield tweetsItems
            url_next = selector.xpath(u'body/div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()
            if url_next:
            	yield Request(url=self.host + url_next[0],callback=self.parse_detail)
