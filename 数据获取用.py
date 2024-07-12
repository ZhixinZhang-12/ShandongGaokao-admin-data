from selenium import webdriver
from selenium.webdriver.common.keys import Keys  # 引用keys包
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver import FirefoxOptions  # 手机模式?¿

from bs4 import BeautifulSoup
import requests
import time

wd = webdriver.Firefox()
wd.implicitly_wait(10)  # 选课网站
wd.get('https://www.eol.cn/e_html/gk/sdxk/index.shtml')

wd.find_element(By.ID, "type").click() #选择的默认是本科
time.sleep(1)
wd.find_element(By.CSS_SELECTOR, "#type > option:nth-child(2)").click()  # 专科

col = []
for i in range(1, 33):  # 大陆地区招生的32个省市自治区
    wd.find_element(By.ID, "area").click()
    time.sleep(1)  # 学校地区
    wd.find_element(By.CSS_SELECTOR,
                    "#area > option:nth-child({0})".format(i)).click()
    time.sleep(1)
    zy = wd.find_element(By.CSS_SELECTOR, ".table")  # 表数据
    rows = zy.find_elements(By.TAG_NAME, "tr")

    for row in rows:
        s = (row.text).split()  # 分割
        col.append(s)

wd.quit()

# zyframe = pandas.DataFrame(data=col)

# zyframe.to_excel("{0}.xlsx".format(31),)
# area