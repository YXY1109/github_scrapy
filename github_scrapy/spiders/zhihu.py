from typing import Any

import scrapy
from fake_useragent import UserAgent
from scrapy.http import Response

from utils.config import global_config
from utils.zhihu_login_code import ZhiHuLogin


class ZhiHuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['http://www.zhihu.com/']
    custom_settings = {
        "COOKIES_ENABLED": True,
    }
    ua = UserAgent()

    def start_requests(self):
        # 模拟登录拿到cookie
        # 处理滑动登录
        # 1：opencv
        # 2：机器学习
        phone = global_config.get("zhihu", "phone")
        password = global_config.get("zhihu", "password")
        zhihu_login = ZhiHuLogin(phone, password, retry=5)
        cookie_dict = zhihu_login.login()

        for url in self.start_urls:
            headers = {
                'User-Agent': self.ua.random
            }
            yield scrapy.Request(url, cookies=cookie_dict, headers=headers, callback=self.parse, dont_filter=True)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        pass
