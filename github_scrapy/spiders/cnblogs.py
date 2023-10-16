from urllib import parse

import scrapy
import undetected_chromedriver as uc

from github_scrapy.items import CnBlogsItem
from utils.common import get_md5


class CnBlogsSpider(scrapy.Spider):
    name = "cnblogs"
    custom_settings = {
        "COOKIES_ENABLED": True,
    }

    def start_requests(self):
        options = uc.ChromeOptions()
        options.headless = False
        browser = uc.Chrome(options=options, version_main=114)
        browser.get("https://account.cnblogs.com/signin")
        # time.sleep(3)
        input("回车继续！！！")
        cookies = browser.get_cookies()
        cookies_dict = {}
        for cookie in cookies:
            cookies_dict[cookie["name"]] = cookie["value"]

        urls = [
            "https://news.cnblogs.com/"
        ]
        for url in urls:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            }
            yield scrapy.Request(url=url, callback=self.parse, cookies=cookies_dict, headers=headers, dont_filter=True)

        # for url in urls:
        #     yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """
        selector：#entry_751406 > div.content > h2 > a
        XPath：//*[@id="entry_751406"]/div[2]/h2/a
        full XPath：/html/body/div[2]/div[2]/div[4]/div[1]/div[2]/h2/a

        1：获取新闻列表页中的新闻url，并交给scrapy进行下载后调用相应的解析方法
        2：获取下一页的url并交给scrapy进行下载，下载完成后交给parse继续跟进解析
        """
        # # 手写的
        # url_list = response.xpath('/html/body/div[2]/div[2]/div[4]/div/div[2]/h2/a/@href').extract()
        # title_list = response.xpath('/html/body/div[2]/div[2]/div[4]/div/div[2]/h2/a/text()').extract()
        # # ['阿秒激光：为“狂飙”的电子摄影 ——解读2023年诺贝尔物理学奖']
        # title = response.xpath('//*[@id="entry_751406"]/div[2]/h2/a/text()').extract()
        # # ['阿秒激光：为“狂飙”的电子摄影 ——解读2023年诺贝尔物理学奖']
        # title = response.xpath('/html/body/div[2]/div[2]/div[4]/div[1]/div[2]/h2/a/text()').extract()
        #
        # # 有局限性
        # url = response.xpath('//*[@id="entry_751406"]/div[2]/h2/a/@href').extract_first("")
        # # 优化1
        # url = response.xpath('//div[@id="news_list"]/div[1]/div[2]/h2/a/@href').extract_first("")
        # # 优化2
        # url = response.xpath('//div[@id="news_list"]//h2/a/@href').extract_first("")
        # # 优化3 提取第一个链接
        # url = response.xpath('//div[@id="news_list"]//h2[@class="news_entry"]/a/@href').extract_first("")
        # # 优化3 所有的链接
        # url_list = response.xpath('//div[@id="news_list"]//h2[@class="news_entry"]/a/@href').extract()
        #
        # # 使用css
        # url_list = response.css('#news_list h2 a::attr(href)').extract()

        # 获取详情页面的链接，并准备解析详情数据
        post_nodes = response.xpath('//div[@id="news_list"]/div[@class="news_block"]')[:5]
        for post_node in post_nodes:
            # todo xpath无法获取下一个 css可以
            image_url = post_node.xpath('//div[@class="entry_summary"]/a/img/@src').get()
            image_url = post_node.css('.entry_summary a img::attr(src)').get()
            print(f"image_url:{image_url}")
            post_url = post_node.xpath('//h2[@class="news_entry"]/a/@href').get()
            post_url = post_node.css('h2 a::attr(href)').get()
            detail_url = parse.urljoin(response.url, post_url)
            print(f"detail_url:{detail_url}")
            if image_url.startswith("//"):
                image_url = f"https:{image_url}"
            yield scrapy.Request(url=detail_url, callback=self.parse_detail,
                                 meta={"front_image_url": image_url})

            """
            # 提取下一页的数据,第一种方式
            next_url = response.xpath('//*[@id="sideleft"]/div[5]/a[11]/text()').extract_first()
            # next_url = response.css('div.pager a:last-child::text').extract_first()
            if next_url == 'Next >':
                # 说明有下一页
                next_url = response.xpath('//*[@id="sideleft"]/div[5]/a[11]/@href').extract_first()
                # next_url = response.css('div.pager a:last-child::attr(href)').extract_first()
                yield scrapy.Request(url=parse.urljoin(response.url, next_url), callback=self.parse)
            """

            # 提取下一页的数据,第二种方式
            # next_url = response.xpath('//a[contains(text(),"Next >")]/@href').extract_first()
            # yield scrapy.Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        """
        详情页面的解析
        :param response:
        :return:
        """
        cn_item = CnBlogsItem()
        title = response.xpath('//div[@id="news_title"]/a/text()').get()
        content_list = response.xpath('//div[@id="news_body"]//p/text()').getall()
        cn_item["title"] = title
        cn_item["content"] = ",".join(content_list)
        image_url = response.meta.get("front_image_url", "")
        if image_url:
            cn_item["front_image_url"] = [image_url]
        else:
            cn_item["front_image_url"] = []
        cn_item["url_object_id"] = get_md5(response.url)

        yield cn_item
