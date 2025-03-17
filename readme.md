~~~创建项目
scrapy startproject github_scrapy
~~~

- 博客园的新闻：https://www.cnblogs.com/
- 知乎的问答
- 拉钩的职位
- 贝壳网
- 七脉数据
- 极目新闻


### scrapy shell调试
~~~
conda activate github_scrapy
scrapy shell https://news.cnblogs.com/

点击chrome插件xpath helper
按住shift，鼠标移动到指定位置，获取xpath

再用这个验证：
response.xpath("//div[@class='content']/h2[@class='news_entry']/a/text()").get()
~~~

### 当初的学习项目，差不多也过时了
