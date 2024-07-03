import pandas
import pyecharts
import pyecharts.options as opts
import numpy

import numpy
import pandas
import datetime
import random
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

zyframe = pandas.DataFrame(data=col)
wd.quit()
zyframe.to_excel("{0}.xlsx".format(31),)
# area

def drawLine(yearAdm: pandas.DataFrame, major: str, schoolList: list, years=["2020", "2021", "2022"]) -> pyecharts.charts.Bar:
    # 设置柱状图
    bar = (pyecharts.charts.Bar(
        init_opts=opts.InitOpts(width="1000pt", height="500pt"))  # 设置大小
        .add_xaxis(xaxis_data=years)  # 这三年的数据
        .set_global_opts(title_opts=opts.TitleOpts(title=major, subtitle="aa"),
                         toolbox_opts=opts.ToolboxOpts(is_show=True),
                         yaxis_opts=opts.AxisOpts(name="投档计划数"),
                         )  # 设置标题和坐标轴信息
        # 设置折线图的y轴，设置可以不从0开始以更方便的看变化
        .extend_axis(yaxis=opts.AxisOpts(
            name="投档最低位次", position="right",  is_scale=True))
    )
    # 折线图由于是重叠加上的，所以基本没有设置，设置都在柱状图
    line = (
        pyecharts.charts.Line()
        .add_xaxis(xaxis_data=years)
    )
    # 只有这三年的数据，这个用于连接合并
    fullyear = pandas.DataFrame(
        data=[[int(i)] for i in years], columns=["年份"])
    # 开始添加数据
    for sch in schoolList:  # 对于可能获取的每一个学校来添加数据
        # 按照这三年来补全，防止错位
        fullInfo = pandas.merge(
            left=fullyear, right=yearAdm[yearAdm["院校名称"] == sch], how="left", on="年份")
        # 分别对于柱状图和折线图添加数据，注意坐标轴不同
        bar.add_yaxis(series_name=sch,
                      y_axis=fullInfo["投档计划数"].to_list(), yaxis_index=0)
        line.add_yaxis(series_name=sch,
                       y_axis=fullInfo["投档最低位次"].to_list(), yaxis_index=1)
    bar.overlap(line)  # 叠加到一起

    return bar  # 返回柱状图和折线图

# 试图找出符合专业/院校条件的组合,专业列表,学校列表,名次范围,最终要拿到的组合单位个数


def admList(yearAdm: pandas.DataFrame, reqDict: dict, limitNum=32) -> pandas.DataFrame:
    ret = yearAdm[(yearAdm["专业名称"].isin(reqDict["专业名称"])) &
                  (yearAdm["院校名称"].isin(reqDict["院校名称"]))]

    return None


def admMerge() -> pandas.DataFrame:
    # 读取数据
    jd2022 = pandas.read_csv(filepath_or_buffer="济大2022.csv",
                             sep=",", encoding="utf-8")
    jd2021 = pandas.read_csv(filepath_or_buffer="济大2021.csv",
                             sep=",", encoding="utf-8")
    jd2020 = pandas.read_csv(filepath_or_buffer="济大2020.csv",
                             sep=",", encoding="utf-8")

    # 纵向拼接位一个，并去重
    jd2 = pandas.concat(objs=[jd2020, jd2021, jd2022],
                        axis=0, ignore_index=True)
    jd2.drop_duplicates(inplace=True)
    return jd2


def admDraw():
    am = admMerge()

    # 按照专业名称来分类，因为当前只有少量数据所以按照单专业来分析
    dfg = am.groupby(by=["专业名称"])

    # 用时间轴图来一次标识多个
    tl = pyecharts.charts.Timeline(
        init_opts=opts.InitOpts(width="1200pt", height="600pt"))
    for k, v in dfg:
        if len(v) >= 2:
            b = drawLine(v, k, ["A427济南大学", "Y016济南大学"])
            tl.add(chart=b, time_point=k)
    tl.render("a2.html")
    return


def drawScoreRank():
    cr2022 = pandas.read_excel(io="2022一分一段.xlsx")
    bar = (
        pyecharts.charts.Bar(init_opts=opts.InitOpts(
            width="1200pt", height="600pt"))
        .add_xaxis(cr2022["分数段"])
        .set_global_opts(title_opts=opts.TitleOpts(title="2022一分一段", subtitle="aa"),
                         datazoom_opts=opts.DataZoomOpts(),
                         toolbox_opts=opts.ToolboxOpts(is_show=True),
                         yaxis_opts=opts.AxisOpts(name="本段人数"),
                         )  # 设置标题和坐标轴信息

        # 设置折线图的y轴，设置可以不从0开始以更方便的看变化
        .extend_axis(yaxis=opts.AxisOpts(
            name="累计人数", position="right",  is_scale=True))
    )

    for colu, ser in cr2022.items():
        if "本段人数" in colu:
            bar.add_yaxis(series_name=colu,
                          y_axis=ser.to_list(), yaxis_index=0)

    bar.render("11.html")
    return None


drawScoreRank()
