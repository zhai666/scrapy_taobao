# -*- coding: utf-8 -*-
import re
import time

import scrapy
from lxml import etree
from pydispatch import dispatcher
from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver import ActionChains

from taobao.items import TaobaoItem


def zhuye():
    url = 'https://www.taobao.com/'
    browser = webdriver.Chrome()
    browser.get(url=url)
    browser.maximize_window()
    dd = browser.find_elements_by_xpath('//div[@class="service J_Service"]/ul[@class="service-bd"]/li[@class="J_Cat a-all"]/a[1]')
    hh = []
    for i in dd:
        bq = i.text
        aa = browser.find_element_by_link_text(bq)
        ActionChains(browser).move_to_element(aa).perform()
        time.sleep(3)
    g = browser.page_source
    html_ = etree.HTML(g)
    bq4_url = html_.xpath('//div[@class="service-fi-links"]/div[@class="service-panel"]/p/a/@href')
    for i in bq4_url:
        # hh.append(i)
        http_ = i.replace('https:','')
        bq_url = 'https:'+http_
        hh.append(bq_url)
    bq_urls = sorted(set(hh), key=hh.index)
    return bq_urls
    # print(len(bq_urls))
    # print(bq_urls)
class TbSpider(scrapy.Spider):
    name = 'tb'
    allowed_domains = ['www.taobao.com','s.taobao.com','item.taobao.com']
    # start_urls = ['https://www.taobao.com/']
    start_urls = zhuye()
    # start_urls = ['https://s.taobao.com/list?spm=a21bo.2017.201867-links-0.14.5af911d9ysC6Nd&q=%E9%98%94%E8%85%BF%E8%A3%A4&cat=16&seller_type=taobao&oetag=6745&source=qiangdiao']
    def __init__(self):
        super(TbSpider,self).__init__()
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        self.browser.maximize_window()
        dispatcher.connect(self.spider_close,signal=signals.spider_closed)

    def spider_close(self):
        self.browser.close()

    def parse(self,response:HtmlResponse,):
        # print('*******************')
        html_ = etree.HTML(response.text)
        urls_ = html_.xpath('//a[starts-with(@href,"//item.taobao.com/item.htm?id=")]/@href')
        urls_ = sorted(set(urls_), key=urls_.index)
        # print(len(urls_))
        for i in urls_:
            bq_url = 'https:'+i
            # print(bq_url)
            yield scrapy.Request(url=bq_url,callback=self.parse_html)
    def parse_html(self,response):
        tao = TaobaoItem()
        html_ = response.text
        tao['name'] = re.findall('<h3.*?data-title="(.*?)">',html_)[0]
        price = re.findall('<strong.*?<em.*?</em><em.*?>(.*?)</em></strong>', html_)
        imgs_url = re.findall(r'auctionImages.*?\[(".*?")]', html_)[0]
        tao['imgs_url'] = imgs_url.replace('"','')
        # imgs = imgs_url.split(',')
        # for i in imgs:
        #     img = i.replace('"', '')
        #     img = 'http:' + img
        #     print(img)
        if len(price) < 2:
            tao['y_price'] = price[0]
            # print('{}的原价为{}'.format(name, y_price))

        else:
            tao['y_price'] = price[0]
            tao['x_price'] = price[1]
            # print('{}的原价为{},现价为{}'.format(name, y_price, x_price))
        yield tao