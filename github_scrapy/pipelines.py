# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import requests
from scrapy.pipelines.images import ImagesPipeline
import codecs

import json


class GithubScrapyPipeline:
    def process_item(self, item, spider):
        title = item.get("title")
        print(f"pipeline----------------------1:{title}")
        front_image_url = item.get("front_image_url")
        print(f"pipeline----------------------2:{front_image_url}")
        image_file_path = item.get("image_file_path")
        print(f"pipeline----------------------3:{image_file_path}")
        return item


class JsonWithEncodingPipline(object):
    """
    自定义json文件的导出
    """

    def __init__(self):
        self.file = codecs.open("article.json", "a", encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class ArticleImagePipeline(ImagesPipeline):
    """
    保存下载图片的相对路径
    """

    def item_completed(self, results, item, info):
        image_file_path = ''
        for ok, value in results:
            image_file_path = value.get("path")
        item["image_file_path"] = image_file_path
        return item
