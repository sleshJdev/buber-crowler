# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join, Identity


class AdItem(scrapy.Item):
    _id = scrapy.Field()
    price = scrapy.Field()
    title = scrapy.Field()
    city = scrapy.Field()
    birthyear = scrapy.Field()
    name = scrapy.Field()
    ethnicity = scrapy.Field()
    availability = scrapy.Field()
    url = scrapy.Field()
    tagline = scrapy.Field()
    description = scrapy.Field()
    phone = scrapy.Field()
    phoneSuffix = scrapy.Field()
    photos = scrapy.Field()
    avatar = scrapy.Field()
    _class = scrapy.Field()


class AdItemLoader(ItemLoader):

    def __init__(self):
        super().__init__(AdItem())

    default_output_processor = TakeFirst()
    price_in = MapCompose(int)
    description_in = MapCompose(str.strip)
    description_out = Join(u'\n')
    tagline_in = MapCompose(str.strip)
    tagline_out = Join(u'\n')
    photos_out = MapCompose(Identity())