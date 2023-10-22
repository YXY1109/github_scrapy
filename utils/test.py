if __name__ == '__main__':
    all_urls = ['https://www.baidu.com', 'https://www.sina.com.cn', 'https://www.taobao.com', 'assdm']
    all_urls = filter(lambda x: x.startswith("https"), all_urls)
    for url in all_urls:
        print(url)
