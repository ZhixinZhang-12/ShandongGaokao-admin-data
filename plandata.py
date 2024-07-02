'''
原则：以2024年数据作为基准，将其他年份的数据对齐到2024年的招生计划数据
对齐基准：院校名称和专业名称两个，院校代码以及专业代码存在变化无法作为基准
数据处理：替换为英文括号，在专业名称中，对齐仅按照第一个括号以及以前的内容进行对齐
特殊处理：
2023年数据中招生院校中有办学类别标识如（山东公办），需要提前切分删除
2022年数据中括号全部为中文，需要替换为英文
'''


import numpy
import pandas
import datetime
import random
import re

from sqlalchemy import true


def adminPlan():
    # 院校名称，专业名称
    plan2024Year = pandas.read_excel(
        io="山东省招生计划数据\\山东_招生计划_2024.xlsx", header=0, sheet_name="2024")
    plan2024Year["专业名称简版"] = plan2024Year["专业名称"].apply(
        lambda x: (x.split(sep="("))[0])

    # 招生院校，专业名称
    collegekind = r"\([^()]*[\b民办|公办|独立学院|合作办学\b][^()]*\)"

    for y in ["2023", "2022", "2021", "2020"]:
        xlsxpath = "山东省各批次志愿录取数据\\{0}一二三批次合并.xlsx".format(y)
        planOtherYear = pandas.read_excel(
            io=xlsxpath, header=0, sheet_name="Sheet1")

        # planOtherYear["院校名称"] = planOtherYear["招生院校"].apply(
        #     lambda x: re.sub(pattern=collegekind, repl="", string=x))
        planOtherYear.drop(labels=["院校编号", "专业编号"],
                           axis="columns", inplace=True)
        planOtherYear["专业名称简版"] = planOtherYear["专业名称"].apply(
            lambda x: (x.split(sep="("))[0])

        plan2024Year = pandas.merge(left=plan2024Year, right=planOtherYear, how="left", left_on=[
            "院校名称", "专业名称简版"], right_on=["院校名称", "专业名称简版"], suffixes=(None, y))
        print(plan2024Year.head(n=2))
    plan2024Year.to_excel(excel_writer="out1.xlsx",
                          sheet_name="Sheet1", index=False, header=True)


# 专业代号及名称	院校代号及名称	投档计划数	投档最低位次


def EachBatch():
    batchlist = []
    for batch0 in ["一批次", "二批次"]:
        xlsxpath = "山东省各批次志愿录取数据\\2020{0}.xlsx".format(batch0)
        batchPlan = pandas.read_excel(
            io=xlsxpath, header=0, sheet_name="Sheet1")
        batchPlan["批次"] = [batch0 for _ in range(0, len(batchPlan))]
        # 分割并把院校/专业编号
        batchPlan["院校编号"] = batchPlan["院校代号及名称"].apply(lambda x: x[0:4])
        batchPlan["院校名称"] = batchPlan["院校代号及名称"].apply(lambda x: x[4:])

        batchPlan["专业编号"] = batchPlan["专业代号及名称"].apply(lambda x: x[0:2])
        batchPlan["专业名称"] = batchPlan["专业代号及名称"].apply(lambda x: x[2:])

        # 删去合并使用的重复名称 以及原先在一起的名称编号
        batchPlan.drop(columns=[
            "专业代号及名称", "院校代号及名称"], inplace=True, axis=1)
        batchlist.append(batchPlan)
        print(batchPlan.head(n=2))

    mergeBatch = pandas.concat(objs=batchlist, axis="index", ignore_index=True)
    print(mergeBatch.head())
    mergeBatch.to_excel(excel_writer="一二三批次合并.xlsx",
                        sheet_name="Sheet1", index=False, header=True)
    return


def mergePlanandVote():
    collegekind = r"\([^()]*[\b民办|公办|独立学院|合作办学\b][^()]*\)"

    for y in ["2023", ]:  # "2022", "2021", "2020"

        # 批次	院校代码	招生院校	专业代码	专业名称	选科要求	招生人数
        planpath = "山东省招生计划数据\\山东_招生计划_{0}.xlsx".format(y)
        planplan = pandas.read_excel(
            io=planpath, header=0, sheet_name="Sheet1")
        planplan["院校名称"] = planplan["招生院校"].apply(
            lambda x: re.sub(pattern=collegekind, repl="", string=x))
        planplan.drop(labels="招生院校", axis="columns")

        # 投档计划数  投档最低位次   批次  院校编号  院校名称 专业编号 专业名称
        votepath = "山东省各批次志愿录取数据\\{0}一二三批次合并.xlsx".format(y)
        planvote = pandas.read_excel(
            io=votepath, header=0, sheet_name="Sheet1")

        plan2024Year = pandas.merge(left=planplan, right=planvote, how="left", left_on=[
            "院校名称", "专业名称"], right_on=["院校名称", "专业名称"], suffixes=(None, y))

    print(plan2024Year.head(n=2))
    plan2024Year.to_excel(excel_writer="out3.xlsx",
                          sheet_name="Sheet1", index=False, header=True)

    return


def filterTargetMajor():
    collegeMajor = ["道路与桥梁工程技术", "电气工程及自动化", "电气工程及其自动化", "电气类", "电气自动化技术", "车辆工程",
                    "智能车辆工程", "物流管理", "现代物流管理", "交通运输", "交通运输类", "口腔医学", "眼视光医学", "医学检验技术",
                    "医学实验技术", "测绘工程", "测绘工程技术", "测绘类",  "测控工程", "测绘技术与仪器", "现代测控工程技术"]
    subjectLimit = ["物理", "化学", "生物", "不限", "物理或化学或生物",
                    "物理和化学和生物", "物理和化学", "物理和生物", "化学和生物",]

    xlsxpath = "专业名称仅括号前一致匹配版本.xlsx"
    mergePlan = pandas.read_excel(
        io=xlsxpath, header=0, sheet_name="Sheet1")
    # 符合专业和选课条件标准
    mergePlan1 = mergePlan[(mergePlan["专业名称简版"].isin(
        collegeMajor)) & (mergePlan["选科要求"].isin(subjectLimit))]

    maxadmin = 150000
    # 名次限制，大于15万或者是新开专业
    mergePlan2 = mergePlan1[((mergePlan1["投档最低位次2023"] > maxadmin) | (mergePlan1["投档最低位次2022"] >
                             maxadmin) | (mergePlan1["投档最低位次2021"] > maxadmin) | (mergePlan1["投档最低位次2020"] > maxadmin)) |
                            (pandas.isna(mergePlan1["投档最低位次2023"]) & pandas.isna(mergePlan1["投档最低位次2022"]) &
                             pandas.isna(mergePlan1["投档最低位次2021"]) & pandas.isna(mergePlan1["投档最低位次2020"]))]

    with pandas.ExcelWriter(path="初步筛选1.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as xlsxwriter:
        mergePlan1.to_excel(excel_writer=xlsxwriter,
                            sheet_name="无排名仅专业选课限制", index=False, header=True)
        mergePlan2.to_excel(excel_writer=xlsxwriter,
                            sheet_name="排名15万后及专业选课限制", index=False, header=True)

    return


def filterduple():
    xlsxpath = "初步筛选1.xlsx"
    filter1 = pandas.read_excel(
        io=xlsxpath, header=0, sheet_name="排名15万后及专业选课限制")

    filter1.drop_duplicates(
        subset=["院校名称", "专业名称"], keep="first", inplace=True)
    with pandas.ExcelWriter(path="初步筛选1.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as xlsxwriter:
        filter1.to_excel(excel_writer=xlsxwriter,
                         sheet_name="学校及专业过滤", index=False, header=True)
    return
filterduple()