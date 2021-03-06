# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re

import pymongo
from scrapy.exceptions import DropItem


class BuberCrowlerPipeline(object):
    def process_item(self, item, spider):
        title = item['title']
        phoneSuffix = item['phoneSuffix']
        if phoneSuffix not in title:
            raise DropItem("Ad {} doesn't contain phone suffix {} in title {}.".format(item['url'], phoneSuffix, title))

        # service property used by spring data mongo when loading document to know on which entity document mapped
        item['_class'] = 'com.slesh.gallery.persistence.model.Ad'
        url = item['url']
        pattern = '((?:\d+_)+{})'.format(phoneSuffix)
        rawPhone = re.search(pattern, url).group()
        phone = re.sub("[^0-9]", "", rawPhone)
        item['phone'] = phone
        return item


class MongoPipeline(object):
    collection_name = 'ad'

    def __init__(self, url, db_name):
        self.url = url
        self.db_name = db_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            crawler.settings.get('MONGO_URL'),
            crawler.settings.get('MONGO_DATABASE'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.url)
        self.db = self.client[self.db_name]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item
