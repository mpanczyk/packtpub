# -*- coding: utf-8 -*-
import scrapy


class PacktpubSpider(scrapy.Spider):
    name = 'packtpub'
    allowed_domains = ['packtpub.com']
    start_urls = ['http://packtpub.com/']

    def parse(self, response):
        pass
