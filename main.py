import sys
import os

from scrapy.cmdline import execute

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 博客园
# execute(["scrapy", "crawl", "cnblogs"])
# 知乎
execute(["scrapy", "crawl", "zhihu"])
