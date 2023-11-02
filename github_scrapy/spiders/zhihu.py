import re
import time
from typing import Any
from urllib import parse

import scrapy
from fake_useragent import UserAgent
from scrapy.http import Response
import undetected_chromedriver as uc

from github_scrapy.items import ZhihuQuestionItem
from utils.config import global_config
from utils.zhihu_login_code import ZhiHuLogin


class ZhiHuSpider(scrapy.Spider):
    # 方便调试
    is_debug = True
    name = "zhihu"
    if is_debug:
        # 测试,手动扫码登录
        start_urls = ['https://www.zhihu.com/signin']
    else:
        start_urls = ['http://www.zhihu.com/']

    allowed_domains = ["www.zhihu.com"]
    custom_settings = {  # 单个爬虫的设置参数
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
            # 测试，扫码登录
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
            # 正式，自动登录
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
        print(f"开始提取问题内容")
        question_id = response.meta.get("question_id")
        url = response.url  # https://www.zhihu.com/question/627868335
        topics_list = response.xpath("//div[@class='QuestionHeader-topics']/div[@class='Tag QuestionTopic css-1s3a4zw']"
                                     "//div[@class='css-1gomreu']//text()").getall()
        topics = ",".join(topics_list)
        title = response.xpath("//h1[@class='QuestionHeader-title']/text()").get()

        content = response.xpath("//div[@class='QuestionRichText QuestionRichText--expandable "
                                 "QuestionRichText--collapsed']//span/text()").get()
        if not content:  # 未找到的情况
            content = response.xpath("//div[@class='QuestionRichText QuestionRichText--collapsed']//span/text()").get()

        answer_num = response.xpath("//h4[@class='List-headerText']/span/text()").get()
        good_item = response.xpath("//div[@class='GoodQuestionAction']/button/text()").get()
        good_num = good_item.split(" ")[1] if good_item else 0
        comment_item = response.xpath("//div[@class='QuestionHeader-Comment']/button/text()").get()
        comment_num = comment_item.split(" ")[0] if comment_item else 0
        watch_user_num_item = response.xpath("//div[@class='NumberBoard-itemInner']/strong"
                                             "[@class='NumberBoard-itemValue']/text()").getall()
        watch_num = watch_user_num_item[0]  # 关注者
        scan_num = watch_user_num_item[1]  # 被浏览

        question = ZhihuQuestionItem()
        question["question_id"] = question_id
        question['url'] = url
        question['topics'] = topics
        question['title'] = title
        question['content'] = content
        question['answer_num'] = answer_num
        question['good_num'] = good_num
        question['comment_num'] = comment_num
        question['watch_user_num'] = watch_num
        question['scan_num'] = scan_num
        question['create_time'] = time.time()
        yield question

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
