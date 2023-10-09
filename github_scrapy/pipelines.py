# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import requests
from scrapy.pipelines.images import ImagesPipeline


class GithubScrapyPipeline:
    def process_item(self, item, spider):
        title = item.get("title")
        print(f"pipeline----------------------1:{title}")
        front_image_url = item.get("front_image_url")
        print(f"pipeline----------------------2:{front_image_url}")
        image_file_path = item.get("image_file_path")
        print(f"pipeline----------------------3:{image_file_path}")
        return item


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            image_file_path = ''
            for ok, value in results:
                image_file_path = value.get("path")
            item["image_file_path"] = image_file_path
            return item
