import sys
import jinja2
import pandas
import pyecharts
import multiprocessing

from pyecharts.options import ComponentTitleOpts
import pyecharts.render

# 从命令行参数中获取输入文本1
inputParam = sys.argv[1]  # 用于接受前端的参数
# 或者本地手动输入
# inputParam = "济南大学"

allYear = ["2024", "2023", "2022", "2021", "2020"]  # 5年的录取数据
admitLevel = ["本科", "专科"]


def drawTable(tableHead: list[str], tableContent: list[list], adiInfo=""):
    echartsTable = pyecharts.components.Table()  # 绘制单张表格
    titleMsg = ""  # 记录标题信息
    if len(tableContent) > 0:  # 查询出结果
        echartsTable.add(headers=tableHead, rows=tableContent)
        titleMsg = "{uni}{info}录取情况".format(uni=inputParam, info=adiInfo)
        # sys.stdout.write("{uni}{info}录取情况查询完成".format(uni=inputParam, info=adiInfo))
    else:  # 名称错误查询为空值则返回空表
        titleMsg = "{uni}学校不存在".format(uni=inputParam)
        sys.stdout.write("院校信息有误,{uni}学校不存在".format(uni=inputParam))
    echartsTable.set_global_opts(title_opts=ComponentTitleOpts(
        title=titleMsg))
    return echartsTable


def singleTable(year: str):
    singleYear = pandas.read_excel(  # 每一年的录取数据
        io="../山东省各批次志愿录取数据年份合并/{y}一二三批次合并.xlsx".format(y=year), header=0, sheet_name="Sheet1")
    targetUniAdmit = singleYear[singleYear["院校名称"]
                                == inputParam]  # 筛选出指定学校的条目
    tableHead = targetUniAdmit.columns.to_list()  # 将表头和内容分别转换为列表来绘制表格
    tableContent = targetUniAdmit.to_numpy().tolist()

    echartsTable = drawTable(tableHead, tableContent, adiInfo=year)
    return echartsTable


def mergeAdmitTable(level: str):  # 查询链接的表格,本科专科分布在两个文件中
    singleYear = pandas.read_excel(  # 每一年的录取数据
        io="../山东省本专科招生变化/{l}录取年际变化.xlsx".format(l=level), skiprows=1, header=0, sheet_name="Sheet1")
    targetUniAdmit = singleYear[singleYear["院校名称"]
                                == inputParam]  # 筛选出指定学校的条目
    tableHead = targetUniAdmit.columns.to_list()  # 将表头和内容分别转换为列表来绘制表格
    tableContent = targetUniAdmit.to_numpy().tolist()

    echartsTable = drawTable(tableHead, tableContent,adiInfo="{l}类专业录取年际变化信息,表格比较长不太方便看可以缩小浏览器或者直接在excel里查询".format(l=level))
    return echartsTable


def uniInfoTable():  # 查询学校信息表格
    fullUniInfo = pandas.read_excel(  # 每一年的录取数据
        io="../报考要求信息/高校信息.xlsx", skiprows=2, header=0, sheet_name="Sheet1")
    targetUniInfo = fullUniInfo[fullUniInfo["学校名称"] == inputParam].T
    tableHead = ["字段名称", "详细信息"]  # 将表头和内容分别转换为列表来绘制表格
    tableT = fullUniInfo.columns.to_list()
    tableC0 = targetUniInfo.to_numpy().tolist()
    if tableC0[0] != []:  # 查询值不为空列表则返回正确值
        tableC = [i[0] for i in tableC0]

    else:
        tableC = ["" for _ in range(len(tableC0))]  # 使用空值填充
    tableContent = list(zip(tableT, tableC))
    echartsTable = drawTable(tableHead, tableContent,adiInfo="学校信息")  # type: ignore
    return echartsTable


if __name__ == '__main__':
    p = multiprocessing.Pool(processes=8)
    asyncRes1 = p.map_async(func=singleTable, iterable=allYear)
    asyncRes2 = p.apply_async(func=uniInfoTable)
    asyncRes3 = p.map_async(func=mergeAdmitTable, iterable=admitLevel)

    li1 = asyncRes1.get()
    li2 = [asyncRes2.get()]
    li3 = asyncRes3.get()
    # SimplePageLayout布局以压缩空间
    tablePage = pyecharts.charts.Page(
        layout=pyecharts.charts.Page.SimplePageLayout)

    for tab1 in li1+li2+li3:  # 加入表格
        tablePage.add(tab1)
    #反正不换行他就能成功渲染
    tablePageHTMLCode=tablePage.render_embed()#获得echarts的html表格
    sys.stdout.write(tablePageHTMLCode)



