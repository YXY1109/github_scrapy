import scrapy


class ZhiHuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['http://www.zhihu.com/']
    custom_settings = {
        "COOKIES_ENABLED": True,
    }

    def start_requests(self):
        # 模拟登录拿到cookie
        # 处理滑动登录
        # 1：opencv
        # 2：机器学习
        pass
