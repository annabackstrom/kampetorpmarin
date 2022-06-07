# -*- coding: utf-8 -*-
import re
import json
from copy import deepcopy
import scrapy
from kampetorpmarin.countrysettings import countries
from kampetorpmarin.items import ScrapedProduct, ScrapedCategory, ScrapedProductCategoryAssociation
from hashlib import sha1


class KampetorpmarinspiderSpider(scrapy.Spider):
    name = 'kampetorpmarinspider'

    def start_requests(self):
        return [scrapy.Request(
            url=x['url'],
            callback=self.parsemainpage,
            cb_kwargs={
                "countryinfo": x,
            }
        ) for x in countries]

    def parse(self, response):
        pass

    def parsemainpage(self, response: scrapy.http.Response, countryinfo: dict):
        rawdata = response.xpath('//section[@class="ammenu-menu-wrapper"]/@data-bind').get()
        jsonbody = json.loads(re.findall(r'data: (.*?), config:', rawdata)[0])

        for menuitem in jsonbody['elems']:
            maincat = ScrapedCategory()
            maincat['name'] = menuitem['name']
            maincat['url'] = menuitem['url']
            maincat['platformcategoryid'] = self.createidfromstring(maincat['url'])
            maincat['level'] = 1
            maincat['agegroup'] = "adult"
            maincat['targetgender'] = "unisex"
            maincat['storeid'] = countryinfo['storeid']

            yield maincat

            yield scrapy.Request(
                url=maincat['url'],
                callback=self.parsecategory,
                cb_kwargs={
                    "cat": maincat,
                    "additionalcats": [],
                    "countryinfo": countryinfo
                }
            )

            for subcatitem in menuitem['elems']:
                subcat = ScrapedCategory()
                subcat['name'] = subcatitem['name']
                subcat['url'] = subcatitem['url']
                subcat['platformcategoryid'] = self.createidfromstring(subcat['url'])
                subcat['level'] = 2
                subcat['agegroup'] = "adult"
                subcat['targetgender'] = "unisex"
                subcat['storeid'] = countryinfo['storeid']

                yield subcat

                yield scrapy.Request(
                    url=subcat['url'],
                    callback=self.parsecategory,
                    cb_kwargs={
                        "cat": subcat,
                        "additionalcats": [maincat],
                        "countryinfo": countryinfo
                    }
                )

                for subsubcatitem in subcatitem['elems']:
                    subsubcat = ScrapedCategory()
                    subsubcat['name'] = subsubcatitem['name']
                    subsubcat['url'] = subsubcatitem['url']
                    subsubcat['platformcategoryid'] = self.createidfromstring(subsubcat['url'])
                    subsubcat['level'] = 3
                    subsubcat['agegroup'] = "adult"
                    subsubcat['targetgender'] = "unisex"
                    subsubcat['storeid'] = countryinfo['storeid']

                    yield subsubcat

                    yield scrapy.Request(
                        url=subsubcat['url'],
                        callback=self.parsecategory,
                        cb_kwargs={
                            "cat": subsubcat,
                            "additionalcats": [subcat, maincat],
                            "countryinfo": countryinfo
                        }
                    )

    def parsecategory(self,
                      response: scrapy.http.Response,
                      cat: ScrapedCategory,
                      additionalcats: list,
                      countryinfo: dict):
        productcards = response.xpath('//ol[@class="products list items product-items"]/li/div/a/@href').extract()

        for productcard in productcards:
            yield scrapy.Request(
                url=productcard,
                callback=self.parseproduct,
                cb_kwargs={
                    "cat": cat,
                    "additionalcats": additionalcats,
                    "countryinfo": countryinfo
                }
            )

    def parseproduct(self,
                     response: scrapy.http.Response,
                     cat: ScrapedCategory,
                     additionalcats: list,
                     countryinfo: dict):
        oneprod = ScrapedProduct()
        oneprod['name'] = response.xpath('//h1/span/text()').get()
        if oneprod['name'] is None:
            return
        oneprod['url'] = response.url
        oneprod['platformproductid'] = self.createidfromstring(oneprod['url'])
        oneprod['platformvariantid'] = "1"
        oneprod['imageLink'] = response.xpath('//meta[@property="og:image"]/@content').get() or ""
        oneprod['additionalImageLinks'] = []
        oneprod['description'] = response.xpath('//meta[@name="description"]/@content').get()

        oldprice = response.xpath('//span[@data-price-type="oldPrice"]/@data-price-amount').get()
        finalprice = response.xpath('//span[@data-price-type="finalPrice"]/@data-price-amount').get()

        if oldprice:
            oneprod['price'] = oldprice
            oneprod['saleprice'] = finalprice
        else:
            oneprod['price'] = finalprice
            oneprod['saleprice'] = None

        oneprod['brand'] = ""
        oneprod['gender'] = "unisex"
        oneprod['agegroup'] = "adult"
        oneprod['gtin'] = [None]
        oneprod['color'] = None
        oneprod['material'] = None
        oneprod['sizes'] = [None]
        oneprod['instock'] = response.xpath('//meta[@property="product:availability"]/@content').get() == "in stock"
        oneprod['additionalcategoryids'] = [x['platformcategoryid'] for x in additionalcats]
        oneprod['storeid'] = countryinfo['storeid']
        oneprod['mpn'] = response.xpath('//div[@itemprop="sku"]/text()').get()
        oneprod['name'] = oneprod['name'].replace(oneprod['mpn'], "").strip()
        oneprod['platformcategoryid'] = cat['platformcategoryid']

        yield oneprod

    @staticmethod
    def createidfromstring(string: str) -> str:
        sha = sha1()
        sha.update(string.encode('utf-8'))
        return sha.hexdigest()[-15:]

    @staticmethod
    def pricefrompricestring(pricestring: str, thousandseparator: str, commaseparator: str) -> str:
        return ''.join(
            re.findall(r'\d*#?\d*',
                       pricestring.replace(thousandseparator, "").replace(commaseparator, "#"))
        ).replace("#", ".")


