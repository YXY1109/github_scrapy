import aiomysql

from scrapy.exceptions import NotConfigured
from scrapy.exporters import JsonItemExporter
from scrapy.pipelines.images import ImagesPipeline
import codecs

import json

from utils.sqlalchemy_base import MySession, Article


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


class JsonExporterPipline(object):
    """
    官方提供的json数据导出
    """

    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()


class MySQLPipeline(object):
    """
    数据写入数据库中
    sqlalchemy，同步写入
    """

    def __init__(self):
        self.session = MySession().session

    def process_item(self, item, spider):
        title = item.get("title", "")
        content = item.get("content", "")
        front_image_url = item.get("front_image_url", "")
        image_file_path = item.get("image_file_path", "")
        url_object_id = item.get("url_object_id", "")
        article = Article(title=title, content=content, url_object_id=url_object_id, front_image_url=front_image_url,
                          front_image_path=image_file_path)
        self.session.add(article)
        self.session.commit()
        return item


class AsyncMySQLPipeline:
    """
    异步写入mysql
    """

    def __init__(self, db_settings):
        print("init")
        self.db_pool = None
        self.db_settings = db_settings

    @classmethod
    def from_crawler(cls, crawler):
        print("from_crawler")
        db_settings = crawler.settings.getdict('MYSQL_SETTINGS')
        if not db_settings:
            raise NotConfigured
        return cls(db_settings)

    async def process_item(self, item, spider):
        print("process_item")
        self.db_pool = await aiomysql.create_pool(**self.db_settings)
        title = item.get("title", "")
        content = item.get("content", "")
        front_image_url = item.get("front_image_url", "")
        image_file_path = item.get("image_file_path", "")
        url_object_id = item.get("url_object_id", "")
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # 异步插入表中
                await cursor.execute(
                    'insert into cn_article(title, content, front_image_url, front_image_path, url_object_id) '
                    'values(%s, %s, %s, %s, %s)',
                    (title, content, front_image_url, image_file_path, url_object_id))
                # 异步提交事务
                await conn.commit()

        return item

    async def close_spider(self, spider):
        self.db_pool.close()
        await self.db_pool.wait_closed()
