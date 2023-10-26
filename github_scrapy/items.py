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

    def get_insert_sql(self):
        # todo 插入和更新一起操作了
        insert_sql = "insert into cnblogs_spider(title, content) values (%s, %s) " \
                     "ON DUPLICATE KEY UPDATE content=VALUES(content)"
        params = (self["title"], self["content"])
        return insert_sql, params


class ZhihuQuestionItem(scrapy.Item):
    """
    知乎的问题
    """
    question_id = scrapy.Field()
    url = scrapy.Field()  # 链接
    topics = scrapy.Field()  # 标签
    title = scrapy.Field()  # 标题
    content = scrapy.Field()  # 内容
    answer_num = scrapy.Field()  # 回答数
    good_num = scrapy.Field()  # 好问题
    comment_num = scrapy.Field()  # 评论数
    watch_user_num = scrapy.Field()  # 关注者
    scan_num = scrapy.Field()  # 被浏览
    create_time = scrapy.Field()
    crawl_time = scrapy.Field()

# class ZhihuAnswerItem(scrapy.item):
#     """
#     知乎的回答
#     """
#     zhihu_id = scrapy.Field()
#     url = scrapy.Field()
#     question_id = scrapy.Field()
#     author_id = scrapy.Field()
#     content = scrapy.Field()
#     comment_num = scrapy.Field()
#     create_time = scrapy.Field()
#     update_time = scrapy.Field()
#     crawl_time = scrapy.Field()
#     crawl_update_time = scrapy.Field()
