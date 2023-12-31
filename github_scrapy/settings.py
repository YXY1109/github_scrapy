import sys
import os

# Scrapy settings for github_scrapy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "github_scrapy"

SPIDER_MODULES = ["github_scrapy.spiders"]
NEWSPIDER_MODULE = "github_scrapy.spiders"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "github_scrapy (+http://www.yourdomain.com)"

# Obey robots.txt rules
# 默认遵守循robots协议，True
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False  # 设置为true,后续的所有请求都会使用第一次的cookies
COOKIES_DEBUG = True

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "github_scrapy.middlewares.GithubScrapySpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    "github_scrapy.middlewares.GithubScrapyDownloaderMiddleware": 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # "github_scrapy.pipelines.ArticleImagePipeline": 1,  # 图片下载
    # "github_scrapy.pipelines.JsonWithEncodingPipline": 2,  # 自定导出json
    # "github_scrapy.pipelines.JsonExporterPipline": 3,  # 官方导出json
    # "github_scrapy.pipelines.MySQLPipeline": 4,  # 同步存入mysql
    # "github_scrapy.pipelines.AsyncMySQLPipeline": 5,  # 异步存入mysql
    "github_scrapy.pipelines.GithubScrapyPipeline": 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# 图片下载路径设置，要安装：pip install pillow
project_dir = os.path.dirname(os.path.abspath(__file__))
print(f"project_dir:{project_dir}")
# /Users/cj/PycharmProjects/github_scrapy/github_scrapy/images
image_store_path = os.path.join(project_dir, "images")
print(f"image_store_path:{image_store_path}")
IMAGES_STORE = image_store_path

# 图片下载的字段
IMAGES_URLS_FIELD = "front_image_url"
IMAGES_RESULT_FIELD = "image_file_path"

MYSQL_SETTINGS = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'db': 'github_spider',
    'charset': 'utf8mb4',
}
