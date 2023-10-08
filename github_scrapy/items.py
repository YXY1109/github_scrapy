# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CnBlogsItem(scrapy.Item):
    title = scrapy.Field()
    content = scrapy.Field()
    image_urls = scrapy.Field()
    url_object_id = scrapy.Field()
