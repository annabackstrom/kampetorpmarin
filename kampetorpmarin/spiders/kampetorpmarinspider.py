# -*- coding: utf-8 -*-
import scrapy


class KampetorpmarinspiderSpider(scrapy.Spider):
    name = 'kampetorpmarinspider'
    allowed_domains = ['kampetorpmarin.se']
    start_urls = ['http://kampetorpmarin.se/']

    def parse(self, response):
        pass
