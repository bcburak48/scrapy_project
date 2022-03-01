# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyprojectItem(scrapy.Item):
    # define the fields for your item here like:

    blocknumber = scrapy.Field()
    txhash = scrapy.Field()
    dtblockchain = scrapy.Field()
    signer = scrapy.Field()
    email = scrapy.Field()
    productid = scrapy.Field()
    departmentid = scrapy.Field()
    categoryid = scrapy.Field()
    shortdescription = scrapy.Field()
    description = scrapy.Field()
    specifications = scrapy.Field()
    photos = scrapy.Field()
    videos = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    upcean = scrapy.Field()
    returnpolicy = scrapy.Field()
    guarantee = scrapy.Field()
    minimumquantity = scrapy.Field()
    packagesizel = scrapy.Field()
    packagesizeh = scrapy.Field()
    packagesizew = scrapy.Field()
    packageweight = scrapy.Field()
    info = scrapy.Field()

    image_urls = scrapy.Field()
    images = scrapy.Field()
