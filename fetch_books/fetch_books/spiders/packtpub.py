# -*- coding: utf-8 -*-
import scrapy
from os import environ
import os
import pathlib

class PacktpubSpider(scrapy.Spider):
    name = 'packtpub'
    allowed_domains = ['packtpub.com']
    base_url = 'https://www.packtpub.com/'
    start_urls = [base_url]
    storage_dir = './books'

    email = environ['PACKT_EMAIL']
    password = environ['PACKT_PASSWORD']

    def parse(self, response):
        yield scrapy.FormRequest.from_response(
            response,
            formcss='#packt-user-login-form',
            formdata={
              'email': self.email,
              'password': self.password,
            },
            callback=self.parse_loggedin,
        )

    def parse_loggedin(self, response):
        yield scrapy.Request(
            url='https://www.packtpub.com/account/my-ebooks',
            callback=self.parse_list,
        )

    def parse_list(self, response):
        for item in response.css('#product-account-list > div'):
            title = (item.css('div.product-top-line > div.float-left.content-width > div.title ::text').extract_first() or '').strip()
            if not title:
                continue
            title = title.replace(' [eBook]', '')
            slug = title.replace(' ', '_').lower().encode(encoding='ascii', errors='ignore').decode(encoding='ascii')
            path = pathlib.Path(self.storage_dir + os.path.sep + slug)
            authors = item.css('div.product-top-line > div.float-left.content-width > div.author ::text').extract_first().strip()
            path.mkdir(parents=True, exist_ok=True)
            path.joinpath('authors.txt').write_text(authors, encoding='utf-8')
            path.joinpath('title.txt').write_text(title, encoding='utf-8')

            pdf_link = item.css('div.product-buttons-line.toggle > div:nth-child(2) > a:nth-child(1) ::attr(href)').extract_first()
            p = path.joinpath(slug + '.pdf')
            if pdf_link and not p.exists():
                yield scrapy.Request(
                    url=self.base_url + pdf_link,
                    callback=self.save_file,
                    meta={'path': p},
                )
            epub_link = item.css('div.product-buttons-line.toggle > div:nth-child(2) > a:nth-child(2) ::attr(href)').extract_first()
            p = path.joinpath(slug + '.epub')
            if epub_link and not p.exists():
                yield scrapy.Request(
                    url=self.base_url + epub_link,
                    callback=self.save_file,
                    meta={'path': p},
                )
            mobi_link = item.css('div.product-buttons-line.toggle > div:nth-child(2) > a:nth-child(3) ::attr(href)').extract_first()
            p = path.joinpath(slug + '.mobi')
            if mobi_link and not p.exists():
                yield scrapy.Request(
                    url=self.base_url + mobi_link,
                    callback=self.save_file,
                    meta={'path': p},
                )
            code_link = item.css('div.product-buttons-line.toggle > div:nth-child(2) > a:nth-child(4) ::attr(href)').extract_first()
            p = path.joinpath(slug + 'codes.zip')
            if code_link and not p.exists():
                yield scrapy.Request(
                    url=self.base_url + code_link,
                    callback=self.save_file,
                    meta={'path': p},
                )

            isbn = item.css('div.product-buttons-line.toggle > div:nth-child(1) > a:nth-child(1) > div ::attr(isbn)').extract_first()
            path.joinpath('isbn.txt').write_text(isbn)

    def save_file(self, response):
        path = response.meta['path']
        self.logger.info('writing %s', str(path))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(response.body)
