from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException
# from seleniumrequests import Chrome
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import ChromeOptions
import time
import random
import requests

IP = '10.1.99.51'
PORT = '8001'


def get_note(phone: str, task_type: str) -> str:
    """
    获取短信验证码
    :param phone: 手机号
    :param task_type: 平台 目前支持：SYCM/WAREHOUSE/KUAISHOU/WEIBO
    :return: 验证码
    {
      "阿里巴巴": "SYCM",
      "唯品会": "WEIPINHUI",
      "抖店": "DOUYIAN",
      "小店": "DOUYIAN",
      "快手科技": "KUAISHOU",
      "微博": "WEIBO",
      "京东": "JINGDONG",
      "拼多多": "PINDUODUO"
    }
    """
    url = f"http://{IP}:{PORT}/note/verify/get?key={task_type}:{phone}"
    print(url)
    for i in range(59 * 5):
        try:
            response = requests.get(url)
            txet = response.text
            print(txet)
            if txet != 'null':
                return txet[1:-1]
            else:
                time.sleep(1)
        except Exception as a:
            time.sleep(1)
            print(a)
    else:
        return str()


def move_to_gap(slider, tracks, browser):  # slider是要移动的滑块,tracks是要传入的移动轨迹
    ActionChains(browser).click_and_hold(slider).perform()
    for x in tracks:
        ActionChains(browser).move_by_offset(xoffset=x, yoffset=0).perform()
    ActionChains(browser).release().perform()


def get_track(distance, t):  # distance为传入的总距离，a为加速度
    track = []
    current = 0
    mid = distance * t / (t + 1)
    v = 0
    while current < distance:
        if current < mid:
            a = 3
        else:
            a = -1
        v0 = v
        v = v0 + a * t
        move = v0 * t + 1 / 2 * a * t * t
        current += move
        track.append(round(move))
    return track


def validate_code(driver, phone):
    """验证码"""
    child_frames = driver.find_elements_by_tag_name('iframe')
    driver.switch_to.frame(child_frames[0])
    time.sleep(5)
    child_frames = driver.find_elements_by_tag_name('iframe')
    try:
        driver.switch_to.frame(child_frames[0])
    except:
        return
    try:
        driver.find_element_by_xpath('//*[@id="J_GetCode"]').click()
    except:
        ...
    else:
        yzm = get_note(phone=phone, task_type='SYCM')

        assert yzm
        # yzm = input('输入验证码：')
        driver.find_element_by_id('J_Checkcode').send_keys(yzm)
        time.sleep(5)
        driver.find_element_by_id('btn-submit').click()
        time.sleep(5)


def login(username="arko海外旗舰店:apollo2", password="APOLLO2021", shop_phone='15388091192'):
    # 设置浏览器,防止selenium被检测出来
    options = ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    driver = webdriver.Chrome(options=options)
    driver.get(
        'https://cnlogin.cainiao.com/login?isNewLogin=true&showae=true&showoa=true&showin=true&redirectURL=http%3A%2F%2Fg.cainiao.com%2Fdashboard')
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="other-login-box"]/li[1]/a').click()
    time.sleep(1)
    # 切换到frame
    driver.switch_to.frame('alibaba-login-box')
    driver.find_element_by_xpath('//*[@id="fm-login-id"]').clear()
    driver.find_element_by_xpath('//*[@id="fm-login-id"]').send_keys(username)
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="fm-login-password"]').clear()
    driver.find_element_by_xpath('//*[@id="fm-login-password"]').send_keys(password)
    time.sleep(1)

    js = """
            (function() {
                document.querySelector('#fm-agreement-checkbox',':before').click();;
            })()
            """
    try:
        driver.execute_script(js)
    except Exception:
        print('无协议选择')

    '''滑块'''
    time1 = [3, 4, 5, 6, 2.1, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7,
             3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5.0, 5.1, 5.2]
    t1 = random.choice(time1)
    slider = driver.find_element_by_xpath("//span[contains(@class, 'btn_slide')]")
    slider1 = driver.find_element_by_xpath('//*[@id="nc_1__scale_text"]')  # 整个滑块元素
    slider2 = driver.find_element_by_xpath('//*[@id="nc_1_n1z"]')  # 小滑块
    max_size = slider1.size
    max_width = max_size['width']
    min_size = slider2.size
    min_width = min_size['width']
    width = max_width + 250  # - min_width
    size_dict = driver.get_window_size()
    window_width = size_dict['width']
    if slider.is_displayed():
        try:
            move_to_gap(slider, get_track(width, t1), driver)
        except:
            ...

    '''登录'''
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="login-form"]/div[4]/button').click()
    driver.switch_to.parent_frame()  # 回到父节点

    validate_code(driver, phone=shop_phone)  # 验证码

    return True


if __name__ == '__main__':
    login()
