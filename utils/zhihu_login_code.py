from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as Ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import time
import requests
import os
import random
import cv2
import numpy as np
import undetected_chromedriver as uc

from utils.config import global_config


class ZhiHuCode(object):
    def __init__(self, slider_ele=None, background_ele=None, count=1, save_image=False):
        self.slider_ele = slider_ele
        self.background_ele = background_ele
        self.count = count
        self.save_image = save_image

    def get_slide_locus(self, distance):
        """
        计算出一个滑动轨迹
        :param distance:
        :return:
        """
        distance += 8
        v = 0
        m = 0.3
        # 保存0.3内的位移
        tracks = []
        current = 0
        mid = distance * 4 / 5
        while current < distance:
            if current < mid:
                a = 2
            else:
                a = -3
            v0 = v
            s = v0 * m + 0.5 * a * (m ** 2)
            current += s
            tracks.append(round(s))
            v = v0 + a * m
        return tracks

    def slide_verification(self, driver, slide_element, distance):
        """
        控制滑块的滑动
        :param driver:
        :param slide_element: 滑块
        :param distance: 滑动的距离
        :return:
        """
        print(f"滑动的距离是:{distance}")
        # 根据滑动的距离生成滑动轨迹
        locus = self.get_slide_locus(distance)

        print(f"生成的滑块轨迹为:{locus},轨迹的距离之和为{distance}")

        # 按下鼠标左键
        ActionChains(driver).click_and_hold(slide_element).perform()

        time.sleep(0.5)

        # 遍历轨迹进行滑动
        for loc in locus:
            time.sleep(0.01)
            ActionChains(driver, duration=50).move_by_offset(loc, random.randint(-5, 5)).perform()
            ActionChains(driver).context_click(slide_element)

        # 释放鼠标
        ActionChains(driver).release(on_element=slide_element).perform()

    def onload_save_img(self, url, filename="image.png"):
        """
        下载图片并保存
        :param url:
        :param filename:
        :return:
        """
        try:
            r = requests.get(url)
        except Exception as e:
            print("下载图片失败")
            raise e
        else:
            with open(filename, "wb") as f:
                f.write(r.content)

    def get_element_slide_distance(self, slider_ele, background_ele, correct=0):
        """
        根据传入滑块和背景的节点，计算滑块的距离
        :param slider_ele: 滑块节点参数
        :param background_ele: 背景图的节点
        :param correct:
        :return:
        """

        # 获取验证码的图片
        slider_url = slider_ele.get_attribute('src')
        background_url = background_ele.get_attribute('src')

        # 下载验证码链接
        slider = "slider.jpg"
        background = "background.jpg"

        self.onload_save_img(slider_url, slider)
        self.onload_save_img(background_url, background)

        # 进行灰度图片，转化为numpy中的数组类型数据
        slider_pic = cv2.imread(slider, 0)
        background_pic = cv2.imread(background, 0)

        # 获取缺口数组的形状,宽高
        width, height = slider_pic.shape[::-1]

        # 将处理之后的图片另存
        slider01 = "slider01.jpg"
        slider02 = "slider02.jpg"
        background01 = "background01.jpg"

        cv2.imwrite(slider01, slider_pic)
        cv2.imwrite(background01, background_pic)

        # 读取另存的滑块
        slider_pic = cv2.imread(slider01)

        # 进行色彩转化
        slider_pic = cv2.cvtColor(slider_pic, cv2.COLOR_RGB2GRAY)

        # 获取色差的绝对值
        slider_pic = abs(255 - slider_pic)
        # 保存图片
        cv2.imwrite(slider02, slider_pic)
        # 读取滑块
        slider_pic = cv2.imread(slider02)

        # 读取背景图
        background_pic = cv2.imread(background01)

        time.sleep(3)

        # 比较两张图片的重叠部分
        result = cv2.matchTemplate(slider_pic, background_pic, cv2.TM_CCOEFF_NORMED)

        # 通过数组运算，获取图片缺口位置
        top, left = np.unravel_index(result.argmax(), result.shape)

        # 背景图缺口坐标
        print(f"当前滑块缺口位置：{left},{top},{left + width},{top + height}")

        # 判断是否需要保存识别过程中的截图文件
        if self.save_image:
            loc = [(left + correct, top + correct), (left + width - correct, top + height - correct)]
            self.image_crop(background, loc)
        else:
            # 删除临时文件
            os.remove(slider01)
            os.remove(slider02)
            os.remove(background)
            os.remove(background01)
            os.remove(slider)

        return left

    def image_crop(self, image, loc):
        """
        截取图片
        :param image:
        :param loc:
        :return:
        """
        cv2.rectangle(image, loc[0], loc[1], (7, 249, 151), 2)
        cv2.imshow("show", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


class ZhiHuLogin(object):

    def __init__(self, user, password, retry=3):
        options = uc.ChromeOptions()
        options.headless = False
        self.browser = uc.Chrome(options=options, version_main=114)
        self.wait = WebDriverWait(self.browser, 20)
        self.url = "https://www.zhihu.com/signin"
        self.sli = ZhiHuCode()
        self.user = user
        self.password = password
        self.retry = retry

    def login(self):
        self.browser.get(self.url)
        # 密码登录
        password_login_xpath = '//*[@id="root"]/div/main/div/div/div/div/div[2]' \
                               '/div/div[1]/div/div[1]/form/div[1]/div[2]'
        # 2=账号 3=密码
        input_xpath = '//*[@id="root"]/div/main/div/div/div/div/div[2]' \
                      '/div/div[1]/div/div[1]/form/div[{}]/div/label/input'
        # 点击登录，弹出滑框
        button_xpath = '//*[@id="root"]/div/main/div/div/div/div/div[2]/div/div[1]/div/div[1]/form/button'

        # 1=背景图 2=滑块图
        img_xpath = '/html/body/div[4]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/img[{}]'
        # 点击密码登录
        # 方式1:ok
        # login_element = self.browser.find_element(by=By.XPATH, value=password_login_xpath).click()

        # 方式2:ok
        login_element = self.browser.find_element(by=By.XPATH, value=password_login_xpath)
        self.browser.execute_script("arguments[0].click();", login_element)

        # 输入账号
        user_name = self.wait.until(Ec.element_to_be_clickable((By.XPATH, input_xpath.format(2))))
        user_name.send_keys(self.user)

        # 输入密码
        password = self.wait.until(Ec.element_to_be_clickable((By.XPATH, input_xpath.format(3))))
        password.send_keys(self.password)

        # 点击登录按钮
        login_button = self.wait.until(Ec.element_to_be_clickable((By.XPATH, button_xpath)))
        login_button.click()
        time.sleep(3)

        # 验证码已弹出，开始识别，并滑动

        k = 1
        while k < self.retry:
            # 获取背景原图
            bg_img = self.wait.until(Ec.presence_of_element_located((By.XPATH, img_xpath.format(1))))
            # 获取滑块原图
            front_img = self.wait.until(Ec.presence_of_element_located((By.XPATH, img_xpath.format(2))))

            # 获取验证码滑动距离
            distance = self.sli.get_element_slide_distance(front_img, bg_img)
            print(f"滑动的距离：{distance}")
            distance = distance - 4
            print(f"实际滑动的距离是：{distance}")

            # 滑块对象
            element = self.browser.find_element(by=By.XPATH,
                                                value="/html/body/div[4]/div[2]/div/div/div[2]/div/div[2]/div[2]")
            # 滑动函数
            self.sli.slide_verification(self.browser, element, distance)

            # 滑动之后的url链接
            time.sleep(5)
            # 登录框
            try:
                login_button.click()
                time.sleep(3)
            except Exception as e:
                print(f"登录失败：{e}")

            end_url = self.browser.current_url
            print(f"end_url:{end_url}")

            if end_url == "https://www.zhihu.com/":
                print("登录成功")
                return self.get_cookies()
            else:
                print("登录失败")
                time.sleep(3)
                k += 1

    def get_cookies(self):
        cookies = self.browser.get_cookies()
        cookies_dict = {}
        for cookie in cookies:
            # cookies_dict += '{}={};'.format(cookie['name'], cookie['value'])
            cookies_dict[cookie['name']] = cookie['value']
        return cookies_dict

    def __del__(self):
        self.browser.close()
        self.browser.quit()
        print("已退出")


if __name__ == '__main__':
    phone = global_config.get("zhihu", "phone")
    password = global_config.get("zhihu", "password")
    zhihu_login = ZhiHuLogin(phone, password, retry=5)
    cookies = zhihu_login.login()
    print(cookies)
    print("完成")
