import pandas
import pyecharts
import pyecharts.options as opts
import pyecharts.charts
import pyecharts.render
import jieba
import re
import numpy
import multiprocessing
import collections


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


def KindsCountChangeBar(chartTitle: str):
    # 设置柱状图
    bar = (pyecharts.charts.Bar(
        init_opts=opts.InitOpts(width="1600px", height="800px", bg_color="#FFFFFF"))  # 设置大小
        .add_xaxis(xaxis_data=year)  # 这三年的数据
        # 设置折线图的y轴，设置可以不从0开始以更方便的看变化
        .extend_axis(yaxis=opts.AxisOpts(
            name="高考报考人数", type_="value", position="right", is_show=True, offset=0, min_=100000, max_=1000000))  # is_scale=True,

        .set_global_opts(title_opts=opts.TitleOpts(title=chartTitle),
                         toolbox_opts=opts.ToolboxOpts(is_show=True,),
                         tooltip_opts=opts.TooltipOpts(
                             trigger="none", axis_pointer_type="cross"),
                         yaxis_opts=opts.AxisOpts(
                             name="高考录取人数", min_=100000, max_=500000),
                         legend_opts=opts.LegendOpts(
                             pos_bottom="0%", orient="horizontal"),  # 将图例置于底部
                         datazoom_opts=[opts.DataZoomOpts()]
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
            series_name=j, y_axis=applicantDict[j], yaxis_index=1, z_level=1)  # type: ignore
    # 重叠二者
    return bar.overlap(line)  # 返回柱状图和折线图


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


def IncreaseRateChangeLine(chartTitle: str):
    bar = (pyecharts.charts.Bar(
        init_opts=opts.InitOpts(width="1600px", height="800px", bg_color="#FFFFFF"))  # 设置大小
        .add_xaxis(xaxis_data=year[1:])  # 这三年的数据
        # 设置折线图的y轴，设置可以不从0开始以更方便的看变化
        .extend_axis(yaxis=opts.AxisOpts(
            name="人数增长率折线图", type_="value", position="right", is_show=True, offset=0, min_=-10, max_=25))  # is_scale=True,

        .set_global_opts(title_opts=opts.TitleOpts(title=chartTitle),
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

    return bar.overlap(line)


allYear = ["2020", "2021", "2022", "2023", "2024"]
# 绘制每年招收人数最多的几个专业，绘制时间轮播图


def MajorMostAdmitBar(adminBatch: str, chartTitle: str):
    mc = pandas.read_excel(io="各专业招收人数总和统计.xlsx",
                           sheet_name="Sheet1", header=0)
    mc1batch = mc[mc["批次"] == adminBatch]  # ,index_col="专业名称"
    # dt = pandas.read_excel(
    #     io="报考要求信息/专业名称变化本科专科合并扁平表.xlsx", sheet_name="Sheet1")
    # dt = dt[["专业名称", "大类名称"]]
    # mc1batch = pandas.merge(left=mc1batch, right=dt, left_on=[
    #                          "专业名称2024"], right_on=["专业名称"], how="left")
    
    tl = pyecharts.charts.Timeline(
        init_opts=opts.InitOpts(width="1600px", height="1600px",))

    for y in allYear:  # 需要加入专业所属大类
        mc1batchLar = mc1batch.nlargest(n=50, columns="投档计划数"+y)
        mc1batchLar.sort_values(by="投档计划数"+y, ascending=True, inplace=True)
        singleBar = (
            pyecharts.charts.Bar(init_opts=opts.InitOpts(
                width="800px", height="1600px",))
            .add_xaxis(mc1batchLar["专业名称2024"].to_list())
            .add_yaxis(series_name="总计录取人数", y_axis=mc1batchLar["投档计划数"+y].to_list(), yaxis_index=0)
            .reversal_axis()
            .set_series_opts(label_opts=opts.LabelOpts(position="right"))
            .set_global_opts(title_opts=opts.TitleOpts(title=chartTitle))
        )
        

        tl.add(chart=singleBar, time_point=y+"年")
    return tl

# 绘制每年招收人数最少的几个专业，绘制词云图


def MajorLeastAdmitWordcloud(adminBatch: str, chartTitle: str):
    mc = pandas.read_excel(io="各专业招收人数总和统计.xlsx",
                           sheet_name="Sheet1", header=0)
    mc1batch = mc[mc["批次"] == adminBatch]
    tl = pyecharts.charts.Timeline(
        init_opts=opts.InitOpts(width="1800px", height="800px",))

    for y in allYear:
        mc1batch1 = mc1batch[mc1batch["投档计划数"+y] > 0]
        mc1batchSma = mc1batch1.nsmallest(n=150, columns="投档计划数"+y)
        datapa = list(zip(mc1batchSma["专业名称2024"],
                      20-mc1batchSma["投档计划数"+y]))

        singleWc = (
            pyecharts.charts.WordCloud(opts.InitOpts(
                width="1800px", height="800px",))
            .add(series_name="最冷门专业", shape="pentagon", data_pair=datapa, word_size_range=[10, 50], rotate_step=0, )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title=chartTitle, subtitle="用20减去标签显示数值即为真实人数"),
                tooltip_opts=opts.TooltipOpts(is_show=True)
            )
        )
        # singleWc.render(y+"年词云图.html")
        tl.add(chart=singleWc, time_point=y+"年")
    return tl


def BatchAdmitRatePie():

    p = (pyecharts.charts.Pie(opts.InitOpts(
        width="1200px", height="600px",))
        .add(
        series_name="志愿投出命中全体考生平均概率",
        data_pair=[("0-30条", 72.33), ("31-70条", 25.03), ("71-96条", 2.64)],
        radius=["30%", "75%"],
        center=["25%", "50%"],
        rosetype="radius",
        label_opts=opts.LabelOpts(is_show=False),
    )
        .add(
        series_name="志愿投出命中范围比重所占整个96条志愿比重",
        data_pair=[("0-30条", 31.25), ("31-70条", 41.67), ("71-96条", 27.08)],
        radius=["30%", "75%"],
        center=["75%", "50%"],
        rosetype="radius",
    )
        .set_global_opts(title_opts=opts.TitleOpts(title="志愿命中饼图")))
    # p.render("pie.html")
    return p

def MajorIncreaseRateLine():
    
    
    
    
    
    return


def Page():
    page = pyecharts.charts.Page(
        layout=pyecharts.charts.Page.DraggablePageLayout)
    page.add(
        KindsCountChangeBar("新高考改革以来各类人数变化"),
        IncreaseRateChangeLine("新高考改革以来各类人数增长变化"),
        MajorMostAdmitBar("一批次", "本科批次每年录取人数最多的50个专业"),
        MajorMostAdmitBar("二批次", "专科科批次每年录取人数最多的50个专业"),
        MajorLeastAdmitWordcloud("一批次", "本科科批次每年录取人数最少的150个专业"),
        MajorLeastAdmitWordcloud("二批次", "专科科批次每年录取人数最少的150个专业"),
        BatchAdmitRatePie(),
    )
    page.render("可视化图表.html")
    return




if __name__ == "__main__":
    # li2=[['1'],['2'],['12']]
    # print([*i  for i in li2])
    #
    # mp = multiprocessing.Pool()
    # mp.map(adminOrigdata, y)

    # mp.join()
    # mp.close()
    Page()
    # Wordcloud4("二批次", "专科科批次每年录取人数最少的50个专业")
    # Pie()
    pass

''''''
