import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join

class AdItem(scrapy.Item):
    id = scrapy.Field()    
    price = scrapy.Field()
    title = scrapy.Field()
    city = scrapy.Field()
    age = scrapy.Field()
    name = scrapy.Field()
    ethnicity = scrapy.Field()
    availability = scrapy.Field()
    url = scrapy.Field()
    tagline = scrapy.Field()
    description = scrapy.Field()
    phone = scrapy.Field()
    
class AdItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
    age_in = MapCompose(int)
    price_in = MapCompose(int)
    description_in = MapCompose(str.strip)
    description_out = MapCompose(lambda text: text if text and text.strip() else None)
    tagline_in = MapCompose(str.strip)
    tagline_out = Join(u'\n')
    
class AdsCrowler(scrapy.Spider):
    host = "https://www.leolist.cc"
    path = "personals/female-escorts"
    base_url = host + "/" + path
    
    name = "ads"

    start_urls = [
        base_url + "/greater-toronto/"      
    ]

    def parse_profile(self, response):
        loader = response.meta['loader']

        ad = response.selector.css('#ad')
        user_data_items =  ad.css('.info .user-data')
        
        for user_data in user_data_items:
            label = user_data.css('.user-label::text').extract_first()
            if not label: continue

            key = None
            label = label.lower()
            if label == 'Name'.lower(): key = 'name'
            elif label == 'Age'.lower(): key = 'age'
            elif label == 'City'.lower(): key = 'city'                
            elif label == 'Ethnicity'.lower(): key = 'ethnicity'
            elif label == 'Availability'.lower(): key = 'availability'
            elif label == 'Hourly Rate'.lower(): key = 'price'

            if not key: raise Error('No known labels were found. Found label is {}'.format(label))

            if key == 'city': value = user_data.css('.value [itemprop=addressLocality]::text').extract_first()
            else: value = user_data.css('.value::text').extract_first()

            if key == 'price': value = user_data.css('.value [itemprop=price]::text').extract_first()
            
            loader.add_value(key, value)

        loader.add_value('title', ad.css('.in .head [itemprop=name]::text').extract_first())
        
        desc = ad.css('#item-desc')
        loader.add_value('tagline', desc.css('.tagline::text').extract_first())
        loader.add_value('description', desc.css('.ad-description-container *::text').extract())
        
        
        yield loader.load_item()
                         
    def parse(self, response):
        groups = response.selector.css('div[id=main_list] > div.group')        
        index = 1
        for group in groups:
            if index > 1:
                continue
            index = index + 1

            loader = AdItemLoader(item = AdItem())
            id = group.css('::attr(id)').re_first('(\d+)')
            loader.add_value('id', str(id))            

            url = group.css('a.mainlist-item::attr(href)').extract_first()
            loader.add_value('url', url)

            yield response.follow(url, meta = {'loader': loader}, callback = self.parse_profile)
