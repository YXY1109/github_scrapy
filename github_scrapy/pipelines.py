# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class GithubScrapyPipeline:
    def process_item(self, item, spider):
        title = item.get("title")
        print(f"pipeline----------------------:{title}")
        return item
