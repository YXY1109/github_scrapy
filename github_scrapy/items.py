# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

from scrapy.loader.processors import MapCompose, TakeFirst


def add_start(value):
    return "start:" + value


def add_end(value):
    return value + "-test"


class CnBlogsItem(scrapy.Item):
    # itemloader 使用的
    # title = scrapy.Field(
    #     input_processor=MapCompose(add_start, add_end),
    #     output_processor=TakeFirst()
    # )
    title = scrapy.Field()
    content = scrapy.Field()
    front_image_url = scrapy.Field()
    image_file_path = scrapy.Field()
    url_object_id = scrapy.Field()
