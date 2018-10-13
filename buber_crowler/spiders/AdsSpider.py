import re

import scrapy
from scrapy.exceptions import DropItem

from buber_crowler.items import AdItemLoader


class AdsCrowler(scrapy.Spider):
    host = "https://www.leolist.cc"
    path = "personals/female-escorts"
    base_url = host + "/" + path

    name = "ads"

    start_urls = [
        base_url + "/greater-toronto/",
        base_url + "/metro-vancouver/vancouver/",
        base_url + "/calgary/calgary/",
        base_url + "/nova-scotia/halifax/",
        base_url + "/greater-toronto/city-toronto/"
    ]

    def parse_profile(self, response):
        loader = response.meta['loader']

        ad = response.selector.css('#ad')
        desc = ad.css('#item-desc')
        rawPhoneSuffix = response.css('.right-contacts-container [class*="icon-phone"] + strong .contacts-view-btn::text').extract_first()
        if not rawPhoneSuffix:
            rawPhoneSuffix = response.css('.ad-description-container .contacts-view-btn::text').extract_first()

        if rawPhoneSuffix:
            loader.add_value('phoneSuffix', re.sub("[^0-9]", "", rawPhoneSuffix))

        loader.add_value('avatar', ad.css('.in .pic img::attr(src)').extract_first())
        loader.add_value('title', ad.css('.in .head [itemprop=name]::text').extract_first())
        loader.add_value('tagline', desc.css('.tagline::text').extract_first())
        loader.add_value('description', desc.css('.ad-description-container *::text').extract())
        loader.add_value('photos', ad.css('.account-photos__item img::attr(src)').extract())

        user_data_items = ad.css('.info .user-data')
        for user_data in user_data_items:
            label = user_data.css('.user-label::text').extract_first()
            if not label: continue

            key = None
            label = label.lower()
            if label == 'Name'.lower():
                key = 'name'
            elif label == 'Age'.lower():
                key = 'age'
            elif label == 'City'.lower():
                key = 'city'
            elif label == 'Ethnicity'.lower():
                key = 'ethnicity'
            elif label == 'Availability'.lower():
                key = 'availability'
            elif label == 'Hourly Rate'.lower():
                key = 'price'

            if not key: raise DropItem('No known labels were found. Found label is {}'.format(label))

            if key == 'city':
                value = user_data.css('.value [itemprop=addressLocality]::text').extract_first()
            elif key == 'price':
                value = user_data.css('.value [itemprop=price]::text').extract_first()
            else:
                value = user_data.css('.value::text').extract_first()

            loader.add_value(key, value)

        yield loader.load_item()

    def parse_page(self, response):
        groups = response.selector.css('div[id=main_list] > div.group')
        for group in groups:
            loader = AdItemLoader()
            id = group.css('::attr(id)').re_first('(\d+)')
            loader.add_value('_id', str(id))

            url = group.css('a.mainlist-item::attr(href)').extract_first()
            loader.add_value('url', url)
            yield response.follow(url, meta={'loader': loader}, callback=self.parse_profile)

    def parse(self, response):
        pages = int(response.selector.css('.pagination li:last-of-type > a::text').extract_first())
        for page in range(1, pages):
            url = response.request.url + "?page=" + str(page)
            yield response.follow(url, callback=self.parse_page)
