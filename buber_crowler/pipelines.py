# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re

from scrapy.exceptions import DropItem


class BuberCrowlerPipeline(object):
    def process_item(self, item, spider):
        title = item['title']
        phoneSuffix = item['phoneSuffix']
        if phoneSuffix not in title:
            raise DropItem("Ad {} doesn't contain phone suffix {} in title {}.".format(item['url'], phoneSuffix, title))

        url = item['url']
        pattern = '((?:\d+_)+{})'.format(phoneSuffix)
        item['phone'] = re.search(pattern, url).group().replace('_', '-')
        return item
