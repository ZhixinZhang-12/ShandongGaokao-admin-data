import pandas
import pyecharts
import pyecharts.options as opts

import jieba
import re
import numpy
import pandas
import multiprocessing
import collections

from sqlalchemy import label
from sympy import prime


# 试图找出符合专业/院校条件的组合,专业列表,学校列表,名次范围,最终要拿到的组合单位个数


def admList(yearAdm: pandas.DataFrame, reqDict: dict, limitNum=32) -> pandas.DataFrame | None:
    ret = yearAdm[(yearAdm["专业名称"].isin(reqDict["专业名称"])) &
                  (yearAdm["院校名称"].isin(reqDict["院校名称"]))]

    return None


def adminOrigdata(year: str):
    xlsxPath = "山东省各批次志愿录取数据年份合并/{ti}一二三批次合并.xlsx".format(ti=year)
    adminSingleBatch = pandas.read_excel(
        io=xlsxPath, sheet_name="Sheet1", header=0)
    # 默认视为一批次为本科数据，二批次为专科数据，三批次以及后续补录暂不考虑

    for deg in ["一批次", "二批次"]:
        # undergraduate/vocational
        undergraduate = adminSingleBatch[adminSingleBatch["批次"] == deg]
        ugAdminCount = undergraduate["投档计划数"].sum()

        undergraduate["专业名称分词"] = undergraduate["专业名称"].apply(
            lambda x: jieba.lcut(x))
        flatug = undergraduate["专业名称分词"].to_list()
        ugMajorCut = undergraduate[["院校名称", "专业名称", "专业名称分词", "投档计划数"]]
        print("{}{}录取人数为:{}".format(year, deg, ugAdminCount))
        wcfile = "majorWord{y}{d}.csv".format(y=year, d=deg)
        ugMajorCut.to_csv(path_or_buf=wcfile, index=False,
                          header=False, encoding="utf8")

    # vocational=adminSingleBatch[adminSingleBatch["批次"]=="二批次"]#

    return


year = ['2020', '2021', '2022', '2023', '2024']
# 报考人数
applicantDict = {
    "春季、夏季总报考人数": [769325, 795000, 867000, 977560, 998000],
    "夏季高考人数": [619820, 630000, 657000, 718818, 722000],
    "夏季高考统一考试人数": [530381, 555810, 598810, 668601, 674000],
    "春季、夏季总计本科录取人数": [286766, 294373, 311993, 320020, 329510],
    "春季、夏季总计专科录取人数": [368058, 394136, 431754, 470694, 489221],
    "夏季高考本科录取人数":  [265999, 271406, 288893, 296967, 307832],
    "夏季高考专科录取人数": [209075, 222028, 242568, 272411, 314622],
    "夏季高考普通类常规批一批次录取": [202747, 210611, 230738, 236967, 247832],
    "夏季高考普通类常规批二批次录取":  [231280, 223084, 223345, 252411, 294622],
}
applyInfoList = ["春季、夏季总报考人数", "夏季高考人数", "夏季高考统一考试人数"]
admitInfoList = ["春季、夏季总计本科录取人数", "春季、夏季总计专科录取人数", "夏季高考本科录取人数",
                 "夏季高考专科录取人数", "夏季高考普通类常规批一批次录取", "夏季高考普通类常规批二批次录取"]
admitInfoList1 = ["春季、夏季总计本专科录取人数", " ", "夏季高考本专科录取人数",
                  "", "夏季高考普通类常规批一批次及二批次录取人数", ""]
stackNum = ["1", "2", "3", "4", "4", "5", "5", "6", "6"]
# 72.33 25.03 2.64

# 基本信息图表


def drawBar1():
    # 设置柱状图
    bar = (pyecharts.charts.Bar(
        init_opts=opts.InitOpts(width="2000px", height="1000px", bg_color="#FFFFFF"))  # 设置大小
        .add_xaxis(xaxis_data=year)  # 这三年的数据
        # 设置折线图的y轴，设置可以不从0开始以更方便的看变化
        .extend_axis(yaxis=opts.AxisOpts(
            name="高考报考人数", type_="value", position="right", is_show=True, offset=0, min_=100000, max_=1000000))  # is_scale=True,

        .set_global_opts(title_opts=opts.TitleOpts(title="新高考改革以来各类人数变化"),
                         toolbox_opts=opts.ToolboxOpts(is_show=True,),
                         tooltip_opts=opts.TooltipOpts(
                             trigger="none", axis_pointer_type="cross"),
                         yaxis_opts=opts.AxisOpts(
                             name="高考录取人数", min_=100000, max_=500000),
                         legend_opts=opts.LegendOpts(
                             pos_bottom="0%", orient="horizontal"),  # 将图例置于底部

                         )  # 设置标题和坐标轴信息

    )
    # 添加录取人数数据
    for i in admitInfoList:
        bar.add_yaxis(series_name=i,
                      y_axis=applicantDict[i], yaxis_index=0)

    # 折线图由于是重叠加上的，所以基本没有设置，设置都在柱状图
    line = (
        pyecharts.charts.Line()
        .add_xaxis(xaxis_data=year)

    )
    # 添加报名人数数据
    for j in applyInfoList:
        line.add_yaxis(
            series_name=j, y_axis=applicantDict[j], yaxis_index=1, z_level=1)
    # 重叠二者
    bar.overlap(line).render("regular.html")
    return None  # 返回柱状图和折线图


a1 = [[2.652685464804056, 5.9856032992156205, 2.5728141336504344, 2.9654396600212487],
      [7.0852963391639365, 9.544421215012077,
          9.019024722411373, 3.9361028608820168],
      [2.0327144087007847, 6.443114743226015,
          2.7948063816014925, 3.6586556755464414],
      [6.19538443142413, 9.251085448682147, 12.3029418554797, 15.495336091420683],
      [3.8787257024764856, 9.556480905555741,
          2.699598679021227, 4.5850266070803105],
      [-3.5437564856451056, 0.11699628839360958, 13.013947032617699, 16.723122209412427]]

# 增长率图表


def drawLine2():
    bar = (pyecharts.charts.Bar(
        init_opts=opts.InitOpts(width="2000px", height="1000px", bg_color="#FFFFFF"))  # 设置大小
        .add_xaxis(xaxis_data=year[1:])  # 这三年的数据
        # 设置折线图的y轴，设置可以不从0开始以更方便的看变化
        .extend_axis(yaxis=opts.AxisOpts(
            name="人数增长率折线图", type_="value", position="right", is_show=True, offset=0, min_=-10, max_=25))  # is_scale=True,

        .set_global_opts(title_opts=opts.TitleOpts(title="新高考改革以来各类人数增长变化"),
                         toolbox_opts=opts.ToolboxOpts(is_show=True,),
                         tooltip_opts=opts.TooltipOpts(
                             trigger="none", axis_pointer_type="cross"),
                         yaxis_opts=opts.AxisOpts(
                             name="人数数量增加柱状图", min_=0),
                         legend_opts=opts.LegendOpts(
                             pos_bottom="0%", orient="horizontal"),  # 将图例置于底部

                         )  # 设置标题和坐标轴信息
    )

    # 折线图由于是重叠加上的，所以基本没有设置，设置都在柱状图
    line = (
        pyecharts.charts.Line()
        .add_xaxis(xaxis_data=year[1:])

    )
    j = 0
    for k, v in applicantDict.items():

        growthNum = [0 for _ in range(0, len(v)-1)]  # 增长量
        growthRate = [0.0 for _ in range(0, len(v)-1)]  # 增长率

        for i in range(0, len(v)-1):
            growthNum[i] = v[i+1] - v[i]
            growthRate[i] += (v[i+1] - v[i]) / v[i] * 100

        # 添加数据
        bar.add_yaxis(series_name=k+"增长量",
                      y_axis=growthNum, yaxis_index=0, stack=stackNum[j])
        if j <= 2:
            line.add_yaxis(
                series_name=k+"增长率", y_axis=growthRate, yaxis_index=1, z_level=1)
        j += 1

    for i in range(0, 6, 2):
        line.add_yaxis(
            series_name=admitInfoList1[i]+"增长率", y_axis=[a1[i][j]+a1[i+1][j] for j in range(0, 4)], yaxis_index=1, z_level=1)

    bar.overlap(line).render("growthStack.html")

    return


if __name__ == "__main__":
    # li2=[['1'],['2'],['12']]
    # print([*i  for i in li2])
    # y = ["2020", "2021", "2022", "2023", "2024"]
    # mp = multiprocessing.Pool()
    # mp.map(adminOrigdata, y)

    # mp.join()
    # mp.close()
    drawLine2()

    pass

''''''
