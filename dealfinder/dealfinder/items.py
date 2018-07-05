# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DealFinderItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    url = scrapy.Field()
    year = scrapy.Field()
    make = scrapy.Field()
    model = scrapy.Field()
    transmission = scrapy.Field()
    manufacturer_marketing_year = scrapy.Field()
    price = scrapy.Field()
    odometer = scrapy.Field()
    engine_capacity = scrapy.Field()
    fuel_type = scrapy.Field()
    n_cylinders = scrapy.Field()
    listing = scrapy.Field()
    drive_type = scrapy.Field()
