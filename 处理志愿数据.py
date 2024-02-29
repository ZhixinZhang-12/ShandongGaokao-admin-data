import numpy
import pandas
import datetime
import random

# 合并录取计划和选课要求，要求始终是不全的


def lqMerge(lqjh_list):  # 录取投档线表格
    xkyqbk = pandas.read_excel(io="本科要求.xlsx")  # 基于20年的本科要求
    xkyqzk = pandas.read_excel(io="专科要求.xlsx")  # 基于20年的专科要求
    # 原方法为删去地区列并修改合并字段，已弃用，现改为直接合并为上方学科要求
    MajorReq = pandas.concat(objs=[xkyqbk, xkyqzk], axis=0, ignore_index=True)
    # MajorReq.sort_index()
    # print(MajorReq.head())

    for lqjh in lqjh_list:
        admin = pandas.read_excel(io="{0}.xlsx".format(lqjh))  # 录取投档线

        # 分割并把院校/专业编号字符改数字，名称保持不变，这部分数字编号是给数据库用的
        admin["院校编号"] = admin["院校代号及名称"].apply(
            lambda x: ord(x[0])*1000+int(x[1:4]))
        admin["院校名称"] = admin["院校代号及名称"].apply(lambda x: x[4:])

        admin["专业编号"] = admin["专业代号及名称"].apply(
            lambda x:  ord(x[0])*1000+ord(x[1]))
        admin["专业名称"] = admin["专业代号及名称"].apply(lambda x: x[2:])

        # 合并部分，只按照当年录取计划已经有的部分
        res = pandas.merge(left=admin, right=MajorReq, left_on=["院校名称", "专业名称"], right_on=[
                           "学校名称", "专业名称"], how="left")
        # 删去合并使用的重复名称 以及原先在一起的名称编号
        res.drop(columns=["学校名称", "Unnamed: 5",
                 "专业代号及名称", "院校代号及名称"], inplace=True, axis=1)

        print(res[5000:5050])  # 列顺序重排
        res = res[["院校编号", "院校名称", "专业编号", "专业名称",
                   "投档计划数",	"投档最低位次", "学校地区", "学历类型", "选科要求"]]

        # res.to_csv(path_or_buf="{0}合并.csv".format(
        #     lqjh), sep="|", index=False, encoding="utf-8")
        # 写入表格
        res.to_excel(excel_writer="{0}合并.xlsx".format(
            lqjh), index=False)
    return None

# 合并不同年份的数据，整理各个专业的名次变化


def lqChange(lqjh_list):  # 录取投档线表格

    res = pandas.DataFrame()  # 空数据框来承接结果
    i = 0
    for ye in lqjh_list:
        # 录取投档线,表格是下面函数处理过的
        admin = pandas.read_excel(io="{0}一二批次处理.xlsx".format(ye))

        admin.rename(columns={"投档计划数": "{0}投档计划数".format(ye),
                              "投档最低位次": "{0}投档最低位次".format(ye)}, inplace=True)

        if i == 0:  # 开始时接受第一个结果
            res = admin
        else:  # 用自身merge方法会报错？
            # 按照年份分开，合并的键使用名称，编号会因年份变化，不便作为标识
            admin.drop(columns=["院校编号", "专业编号"], inplace=True)
            res = pandas.merge(left=res, right=admin, on=[
                               "院校名称", "专业名称"], how="outer")
            print(res.head())  # 按照专业外合并

        i += 1

    res.to_excel("年份变化.xlsx", index=False)
    return  # 写入表格

# 用于合并一二批次的数据,传入的是整数年份2020.。。


def lqYearMerege(yearlist):

    for ye in yearlist:
        # 读取表格
        y1 = pandas.read_excel(io="{0}一批次.xlsx".format(ye))
        y2 = pandas.read_excel(io="{0}二批次.xlsx".format(ye))
        YearAdmin = pandas.concat(
            [y1, y2], axis=0, ignore_index=True)  # 直接纵向拼接

        # 分割并把院校/专业编号字符改数字，名称保持不变，这部分数字编号是给数据库用的
        YearAdmin["院校编号"] = YearAdmin["院校代号及名称"].apply(
            lambda x: ord(x[0])*1000+int(x[1:4]))
        YearAdmin["院校名称"] = YearAdmin["院校代号及名称"].apply(lambda x: x[4:])

        YearAdmin["专业编号"] = YearAdmin["专业代号及名称"].apply(
            lambda x:  ord(x[0])*1000+ord(x[1]))
        YearAdmin["专业名称"] = YearAdmin["专业代号及名称"].apply(lambda x: x[2:])

        # 删去合并使用的重复名称 以及原先在一起的名称编号
        YearAdmin.drop(columns=[
            "专业代号及名称", "院校代号及名称"], inplace=True, axis=1)
        # 按照学校重新排序，暂时不区分批次
        YearAdmin.sort_values(by="院校编号", inplace=True, ascending=True)
        print(YearAdmin.head())
        # 写入表格
        YearAdmin.to_excel("{0}一二批次处理.xlsx".format(
            ye), index=False)
    return None


tl = ["2020一二批次", "2021一二批次", "2022一二批次"]  # ,
lqChange([2020, 2021, 2022])

# lqMerge(tl)
# collegeID,collegeName,majorID,majorName,adminPlan,adminRank,drop1,majorReq,drop2
