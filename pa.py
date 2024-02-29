import numpy
import pandas
import datetime
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys  # 引用keys包
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver import FirefoxOptions# 手机模式?¿

from bs4 import BeautifulSoup
import requests
import time


# sheet0 = pandas.read_excel(io="武汉站.xlsx", sheet_name="武汉站")  # 车次及始发终到信息
# print(sheet0.head())

station = "济南西"




def getTrain(wd, station=""):
    # 时刻表路径信息
    TrainTable = wd.find_element(
        By.CSS_SELECTOR, ".table-inner > table:nth-child(1)")
    rows = TrainTable.find_elements(By.TAG_NAME, "tr")
    # 爬取的表格数据
    colName = ['车次', '列车类型', '始发站', '始发时间',
               '经过站', '到达时间', '发车时间', '终点站', '终到时间']
    listInfo = []
    for row in rows:
        traintext = row.text
        # 字符串操作
        listInfo1 = traintext.replace(" (当日)", "").split(" ")
        listInfo.append(listInfo1)
    # 转化为数据框
    tframe = pandas.DataFrame(data=listInfo, columns=colName)
    tframe.drop([0, 1], inplace=True)  # 删去原数据的前两行列名
    print(tframe.head())
    tframe.drop(columns=['始发时间', '经过站', '终到时间'],inplace=True)  # 去掉不需要的信息
    print(tframe.head())

    tframe.to_excel("{0}站.xlsx".format(station))
    
    return


def getEntance(wd, station, checi):
    # 输入车次并确认
    element1 = wd.find_element(By.XPATH, '//*[@id="ticket_check_trainNum"]')

    element1.clear()
    element1.send_keys(checi+'\n')
    time.sleep(1)
    element1.send_keys(Keys.ENTER)  # 回车键Enter

    # 点击下拉框以获得停站选项
    time.sleep(1)
    wd.find_element(By.XPATH, '//*[@id="ticketEntranceSel"]').click()

    # 选择停站
    time.sleep(1)
    elements = wd.find_elements(By.CSS_SELECTOR, '.model-select-option > li')
    for ele in elements:  # 在所有停站中遍历信息
        if ele.text == station:
            ele.click()  # 点击下拉框对应选项确认
            # 如果查询到
            btn = wd.find_element(By.CSS_SELECTOR, ".btn")
            btn.click()  # 点击查询按钮
            checkin = wd.find_elements(By.CSS_SELECTOR, ".check-numnew")
            time.sleep(0.5)
            entrance = checkin[0].text  # 得到检票口文本信息
            print("车次:{0},检票口:{1}".format(checi, entrance))
            return entrance
    # 没有查询到则为终到车次
    print("车次:{0} ,{1}站无检票口信息".format(checi, station))
    return 0

# for index, row in sheet0.iterrows():
#     getEntance(wd,station,row["车次"])
#     #print(row["车次"])

# wd = webdriver.Firefox()
# wd.implicitly_wait(10)
# wd.get('https://qq.ip138.com/train/shandong/jinanxi.htm')
# getTrain(wd,station)
# wd.quit()
