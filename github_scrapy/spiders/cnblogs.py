import scrapy
import undetected_chromedriver as uc


class QuotesSpider(scrapy.Spider):
    name = "cnblogs"

    custom_settings = {
        "COOKIES_ENABLED": True,
    }

    def start_requests(self):
        urls = [
            "https://news.cnblogs.com/"
        ]
        options = uc.ChromeOptions()
        options.headless = False
        browser = uc.Chrome(options=options, version_main=114)
        browser.get("https://account.cnblogs.com/signin")
        input("回车，继续")
        cookies = browser.get_cookies()
        cookies_dict = {}
        for cookie in cookies:
            cookies_dict[cookie["name"]] = cookie["value"]

        for url in urls:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            }
            yield scrapy.Request(url=url, callback=self.parse, cookies=cookies_dict, headers=headers, dont_filter=True)

    def parse(self, response):
        """
        selector：#entry_751406 > div.content > h2 > a
        XPath：//*[@id="entry_751406"]/div[2]/h2/a
        full XPath：/html/body/div[2]/div[2]/div[4]/div[1]/div[2]/h2/a
        """
        # 手写的
        url_list = response.xpath('/html/body/div[2]/div[2]/div[4]/div/div[2]/h2/a/@href').extract()
        title_list = response.xpath('/html/body/div[2]/div[2]/div[4]/div/div[2]/h2/a/text()').extract()
        # ['阿秒激光：为“狂飙”的电子摄影 ——解读2023年诺贝尔物理学奖']
        title = response.xpath('//*[@id="entry_751406"]/div[2]/h2/a/text()').extract()
        # ['阿秒激光：为“狂飙”的电子摄影 ——解读2023年诺贝尔物理学奖']
        title = response.xpath('/html/body/div[2]/div[2]/div[4]/div[1]/div[2]/h2/a/text()').extract()

        # 有局限性
        url = response.xpath('//*[@id="entry_751406"]/div[2]/h2/a/@href').extract_first("")
        # 优化1
        url = response.xpath('//div[@id="news_list"]/div[1]/div[2]/h2/a/@href').extract_first("")
        # 优化2
        url = response.xpath('//div[@id="news_list"]//h2/a/@href').extract_first("")
        # 优化3 提取第一个链接
        url = response.xpath('//div[@id="news_list"]//h2[@class="news_entry"]/a/@href').extract_first("")
        # 优化3 所有的链接
        url_list = response.xpath('//div[@id="news_list"]//h2[@class="news_entry"]/a/@href').extract()

        # 使用css
        url_list = response.css('#news_list h2 a::attr(href)').extract()

        pass
