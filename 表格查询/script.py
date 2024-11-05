import sys
import pandas
import pyecharts
import multiprocessing
from pyecharts.charts import Page
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts
import pyecharts.render


# 从命令行参数中获取输入文本1
inputParam = sys.argv[1] #用于接受前端的参数
#或者本地手动输入
# inputParam = "济南大学"

allYear = ["2024", "2023", "2022", "2021", "2020"]  # 5年的录取数据

def singleTable(year: str):
    singleYear = pandas.read_excel(  # 每一年的录取数据
        io="../山东省各批次志愿录取数据年份合并/{y}一二三批次合并.xlsx".format(y=year), header=0, sheet_name="Sheet1")
    targetUniAdmit = singleYear[singleYear["院校名称"]
                                == inputParam]  # 筛选出指定学校的条目
    tableHead = targetUniAdmit.columns.to_list()  # 将表头和内容分别转换为列表来绘制表格
    tableContent = targetUniAdmit.to_numpy().tolist()
    if len(tableContent) > 0:  # 查询出结果
        echartsTable = (pyecharts.components.Table()  # 绘制单张表格
                        .add(headers=tableHead, rows=tableContent)
                        .set_global_opts(title_opts=ComponentTitleOpts(title="{uni}{y}年录取情况".format(uni=inputParam, y=year))))
        print("{uni}{y}年录取情况查询完成".format(uni=inputParam, y=year))
    else:  # 名称错误查询为空值则返回空表
        echartsTable = (pyecharts.components.Table()  # 绘制单张表格
                        .set_global_opts(title_opts=ComponentTitleOpts(title="{uni}学校不存在".format(uni=inputParam))))
        print("院校信息有误,{uni}学校不存在".format(uni=inputParam))
    return echartsTable


def mergeAdmitTable():# 查询链接的表格
    
    
    return

def uniInfoTable(): #查询学校信息表格
    fullUniInfo = pandas.read_excel(  # 每一年的录取数据
        io="../报考要求信息/高校信息.xlsx", skiprows=2, header=0, sheet_name="Sheet1")
    targetUniInfo = fullUniInfo[fullUniInfo["学校名称"] == inputParam].T
    tableHead = ["字段名称", "详细信息"]  # 将表头和内容分别转换为列表来绘制表格
    tableT = fullUniInfo.columns.to_list()
    tableC0 = targetUniInfo.to_numpy().tolist()
    if tableC0[0] != []: #查询值不为空列表则返回正确值
        tableC = [i[0] for i in tableC0]
        tableContent = list(zip(tableT, tableC))
        echartsTable = (pyecharts.components.Table()  # 绘制单张表格
                        .add(headers=tableHead, rows=tableContent)#加入表格信息
                        .set_global_opts(title_opts=ComponentTitleOpts(title="{uni}院校信息".format(uni=inputParam)))) 
        print("{uni}院校信息查询成功".format(uni=inputParam))
    else: #查询为空则返回空表并给出信息。、
        echartsTable = (pyecharts.components.Table()  # 绘制单张表格
                        .set_global_opts(title_opts=ComponentTitleOpts(title="院校信息有误,{uni}学校不存在".format(uni=inputParam))))#空表格，无add的表格内容
        print("{uni}院校信息查询失败".format(uni=inputParam))
    return echartsTable



if __name__ == '__main__':
    p = multiprocessing.Pool(processes=6)
    asyncRes1 = p.map_async(func=singleTable, iterable=allYear)
    asyncRes2 = p.apply_async(func=uniInfoTable)
    li1 = asyncRes1.get()
    li2 = [asyncRes2.get()]

    # SimplePageLayout布局以压缩空间
    tablePage = pyecharts.charts.Page(
    layout=pyecharts.charts.Page.SimplePageLayout)

    for tab1 in li2+li1:  # 加入表格
        tablePage.add(tab1)
    # script1.run(debug=True,port=5001)    
    tablePage.render("tableResult.html")
    print("本地html渲染完成，请到文件夹下tableResult.html查看")
    # tablePage.render_embed("templates/simple_page.html")
    #print(tablePageHTMLCode)
