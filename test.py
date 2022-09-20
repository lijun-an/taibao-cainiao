import pyppeteer
import time
import random
import asyncio
import requests
from time import sleep

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
                sleep(1)
        except Exception as a:
            sleep(1)
            print(a)
    else:
        return str()


async def page_evaluate(page):
    """
    替换淘宝在检测浏览时采集的一些参数。
    就是在浏览器运行的时候，始终让window.navigator.webdriver=false
    navigator是windiw对象的一个属性，同时修改plugins，languages，navigator
    :param page: 浏览器对象
    :return:
    """
    await page.setViewport({'width': 1480, 'height': 980})
    # await page.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => undefined } }) }''')
    await page.evaluateOnNewDocument('''() => {
        const newProto = navigator.__proto__;
        delete newProto.webdriver;
        navigator.__proto__ = newProto;
      }''')
    await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {}, }; }''')

    await page.evaluate('''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
    await page.evaluate('''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')
    # await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    #                         'Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299')


def slide_list(total_length):
    '''
    拿到移动轨迹，模仿人的滑动行为，先匀加速后匀减速
    匀变速运动基本公式：
    ①v=v0+at
    ②s=v0t+½at²
    ③v²-v0²=2as
    :param total_length: 需要移动的距离
    :return: 每段移动的距离列表
    '''
    # 初速度
    v = 0
    # 单位时间为0.3s来统计轨迹，轨迹即0.3内的位移
    t = 1
    # 位移/轨迹列表，列表内的一个元素代表一个T时间单位的位移,t越大，每次移动的距离越大
    slide_result = []
    # 当前的位移
    current = 0
    # 到达mid值开始减速
    mid = total_length * 4 / 5

    while current < total_length:
        if current < mid:
            # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
            a = 2
        else:
            a = -3
        # 初速度
        v0 = v
        # 0.2秒时间内的位移
        s = v0 * t + 0.5 * a * (t ** 2)
        # 当前的位置
        current += s
        # 添加到轨迹列表
        slide_result.append(round(s))

        # 速度已经达到v,该速度作为下次的初速度
        v = v0 + a * t
    return slide_result


async def slide_move(page, iframe, slide_id):
    """
    模拟滑动滑块
    :param page:
    :param slide_id:
    :param iframe
    :return:
    """
    await iframe.hover(slide_id)  # 移动到元素上方
    await page.mouse.down()  # 按下
    slides = slide_list(640)
    x = page.mouse._x
    y = page.mouse._y
    for distance in slides:
        x += distance
        yy = random.choice([y + 1, y, y + 2, y + 3, y + 4])
        await page.mouse.move(x, 1, {'steps': 15})
    await page.mouse.up()


async def login():
    """

    备注选择器
        用户名：#fm-login-id
        密码：#fm-login-password
        滑块：#nc_1_n1z
        登录：#login-form > div.fm-btn > button
        获取验证码: //*[@id="J_GetCode"]
        输入验证码：#J_Checkcode
        验证码确定：//*[@id="btn-submit"]
    :param username:
    :param password:
    :return:
    """
    username = '水羊国际:apollo03'
    password = 'sygjapollo03'
    url = 'https://cnlogin.cainiao.com/login?isNewLogin=true&showae=true&showoa=true&showin=true&redirectURL=http%3A%2F%2Fg.cainiao.com%2Fdashboard'
    width, height = 1366, 768

    browser = await pyppeteer.launch({
        'headless': False,  # 关闭无头模式
        'args': [
            '--disable-extensions',
            '--hide-scrollbars',
            '--disable-bundled-ppapi-flash',
            '--mute-audio',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-gpu',
            # '--disable-infobars',
            f'--window-size={width},{height}',
            # f'--proxy-server={ip}:{port}'  # 代理
        ],
    })

    # context = await browser.createIncognitoBrowserContext()  # 无痕

    page = await browser.newPage()

    await page_evaluate(page)  # 修改特征
    await page.goto(url)
    frame = page.frames  # 获取所有的iframe
    iframe = frame[1]
    await page.click('#other-login-box > li:nth-child(1) > a')
    await page.waitFor(2000)
    # 模拟输入 账号密码  {'delay': rand_int()} 为输入时间
    await iframe.type('#fm-login-id', username, {'delay': random.randint(120, 161) - 50})
    await asyncio.sleep(5)
    await iframe.type('#fm-login-password', password, {'delay': random.randint(110, 161)})

    '''
    # 多层frame, 快速定位元素所在哪个frame中
    for i, b in enumerate(frame):
        for j in b.childFrames:
            slider = await j.xpath('/html/body/center')
            print(i, slider)
    '''
    await asyncio.sleep(2)

    # 登录
    # await iframe.click("#login-form > div.fm-btn > button")
    await asyncio.wait([
        iframe.click('#login-form > div.fm-btn > button'),
        page.waitForNavigation({'waitUntil': 'domcontentloaded'}),
    ])

    await iframe.waitFor(2000)
    await asyncio.sleep(5)
    time.sleep(5)

    try:
        for i, b in enumerate(frame):
            for j in b.childFrames:
                slider = await j.xpath('/html/body/center')
                print(i, slider)
                if slider:
                    # 滑块
                    iframe_slider = iframe.childFrames[0]
                    # slider = await iframe_slider.xpath('//*[@id="nc_1_n1z"]')
                    slider = await j.xpath('//*[@id="nc_1_n1z"]')
                    if slider:
                        await slide_move(slide_id='#nc_1_n1z', page=page, iframe=j)
    except IndexError:
        print('没有滑块!!')
    # else:
    #     if slider:

    # 登录
    # await iframe.click("#login-form > div.fm-btn > button")
    await asyncio.wait([
        iframe.click('#login-form > div.fm-btn > button'),
        page.waitForNavigation({'waitUntil': 'domcontentloaded'}),
    ])

    """
    # 查询神器
    for i, b in enumerate(frame):
        for j in b.childFrames:
            slider = await j.xpath('/html/body/center')
            print(i, slider)
    """
    # await iframe.waitFor(5000)
    try:
        frame = page.frames  # 获取所有的iframe
        iframe = frame[1]
        iframe_slider = iframe.childFrames[0]
        slider = await iframe_slider.xpath('//*[@id="J_Checkcode"]')

        await iframe_slider.click('#J_GetCode')  # 点击获取验证码
    except IndexError:
        ...
    else:
        if slider:
            # yzm = input('输入验证码:')

            yzm = get_note(phone='15388091192', task_type='SYCM')

            assert yzm

            await iframe_slider.type('#J_Checkcode', yzm)

            await iframe.waitFor(5000)

            # 确定
            await asyncio.wait([
                iframe_slider.click('#btn-submit'),
                page.waitForNavigation({'waitUntil': 'domcontentloaded'}),
            ])

    await iframe.waitFor(20000)

    await browser.close()


asyncio.get_event_loop().run_until_complete(login())
