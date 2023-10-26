import re
from typing import Any
from urllib import parse

import scrapy
from fake_useragent import UserAgent
from scrapy.http import Response
from scrapy.loader import ItemLoader
# from github_scrapy.items import ZhihuQuestionItem
import undetected_chromedriver as uc
from utils.config import global_config
from utils.zhihu_login_code import ZhiHuLogin


class ZhiHuSpider(scrapy.Spider):
    # 方便调试
    is_debug = True
    name = "zhihu"
    if is_debug:
        # 测试
        start_urls = ['https://www.zhihu.com/signin']
    else:
        start_urls = ['http://www.zhihu.com/']

    allowed_domains = ["www.zhihu.com"]
    custom_settings = {
        "COOKIES_ENABLED": True,
    }
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random
    }

    def start_requests(self):
        # 模拟登录拿到cookie
        # 处理滑动登录
        # 1：opencv
        # 2：机器学习
        if self.is_debug:
            # 测试
            options = uc.ChromeOptions()
            options.headless = False
            browser = uc.Chrome(options=options, version_main=114)
            browser.get('https://www.zhihu.com/signin')
            # time.sleep(3)
            input("回车继续！！！")
            cookies = browser.get_cookies()
            cookies_dict = {}
            for cookie in cookies:
                cookies_dict[cookie["name"]] = cookie["value"]
            yield scrapy.Request("http://www.zhihu.com/", cookies=cookies_dict, headers=self.headers, dont_filter=True)
        else:
            # 正式
            phone = global_config.get("zhihu", "phone")
            password = global_config.get("zhihu", "password")
            zhihu_login = ZhiHuLogin(phone, password, retry=5)
            cookie_dict = zhihu_login.login()

            for url in self.start_urls:
                yield scrapy.Request(url, cookies=cookie_dict, headers=self.headers, dont_filter=True)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        print("开始解析首页数据")
        # 提取所有url
        all_urls = response.css("a::attr(href)").extract()
        # 拼接url
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        # 保留https开始的url
        all_urls = filter(lambda x: x.startswith("https"), all_urls)
        for url in all_urls:
            print(f"url:{url}")
            # https://www.zhihu.com/question/627004253/answer/3258704195
            # https://www.zhihu.com/question/627004253
            match_object = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_object:
                # 如果提取到question相关页面，继续提取详情
                request_url = match_object.group(1)
                question_id = match_object.group(2)
                print(f"request_url:{request_url}")
                print(f"question_id:{question_id}")
                # 找到question
                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question,
                                     dont_filter=True, meta={"question_id": question_id})
                if self.is_debug:
                    # 调试使用
                    break
            else:
                # 如果没有提取到question，继续跟踪
                if not self.is_debug:
                    yield scrapy.Request(url, headers=self.headers, dont_filter=True)

    def parse_question(self, response):
        # 处理question页面，从页面中提取具体的question item
        # 方式1
        # print(f"开始提取问题内容")
        title = response.css("h1.QuestionHeader-title::text").extract_first()
        title = response.xpath('//h1[@class="QuestionHeader-title"]/text()').extract_first()
        print(f"title:{title}")
        content = response.css("div.Question-main").extract_first()

        # response.xpath('//span[@class="RichText ztext css-117anjg"]/p/text()').extract()

        # 方式2 todo 待优化
        # ZhihuQuestionItem()
        # item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        # item_loader.add_css("title", "h1.QuestionHeader-title::text")
        # item_loader.add_xpath("content", '//*[@id="root"]/div/main/div/div/'
        #                                  'div[1]/div[2]/div/div[1]/div[1]/div[4]/div/div/div/div/span/p')
        # item_loader.add_value("url", response.url)
        # item_loader.add_value("zhihu_id", response.mata.get("question_id"))
        # item_loader.add_css("answer_num", "span.List-headerText::text")
        #
        # question_item = item_loader.load_item()
        # yield question_item
