import os
import pickle
import time

import scrapy
from scrapy.spiders import CrawlSpider, Rule

from scrapy.linkextractors import LinkExtractor
import undetected_chromedriver as uc

from selenium.webdriver.common.by import By

from github_scrapy.items import LagouItemLoader, LagouItem


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    rules = (
        Rule(LinkExtractor(allow=r'gongsi/v1/j/.*'), callback='parse_job', follow=True),
        Rule(LinkExtractor(allow=r'wn/jobs/\d+.*'), callback='parse_job', follow=True)
    )

    # 账号=1，密码=2
    login_path = '//*[@id="lg-passport-box"]/div/div[2]/div/div[2]/div/div[1]/div[{}]/input'
    # 登录
    login_button = '//*[@id="lg-passport-box"]/div/div[2]/div/div[3]/button'
    # 同意
    login_agree = '//*[@id="lg-passport-box"]/div/div[2]/div/div[4]/div[2]/div'

    def start_requests(self):
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cookies_path = os.path.join(project_dir, "cookies", "lagou.cookie")

        cookies = []
        if os.path.exists(cookies_path):
            cookies = pickle.load(open(cookies_path, "rb"))

        if not cookies:
            # 使用selenium模拟登录
            # todo 账号密码需要改为正式的
            options = uc.ChromeOptions()
            options.headless = False
            browser = uc.Chrome(options=options, version_main=114)
            browser.get("https://passport.lagou.com/login/login.html")
            name = browser.find_element(by=By.XPATH, value=self.login_path.format(1))
            name.send_keys("yxy")
            password = browser.find_element(by=By.XPATH, value=self.login_path.format(2))
            password.send_keys("yxy")
            button = browser.find_element(by=By.XPATH, value=self.login_button)
            agree = browser.find_element(by=By.XPATH, value=self.login_agree)
            agree.click()
            button.click()
            time.sleep(5)
            cookies = browser.get_cookies()
            # 写入文件中
            pickle.dump(cookies, open(cookies_path, "wb"))

        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']

        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, cookies=cookie_dict)

    def parse_job(self, response):
        # todo 找时间优化
        print(response.url)
        item_loader = LagouItemLoader(item=LagouItem(), response=response)
        item_loader.add_css("title", ".job-name")

        item = item_loader.load_item()
        return item
