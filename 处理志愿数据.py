from calendar import c
import numpy
import pandas
import datetime
import random
import multiprocessing
import threading
import re

from sympy import true

'''
原则：以2024年数据作为基准，将其他年份的数据对齐到2024年的招生计划数据
对齐基准：院校名称和专业名称两个，院校代码以及专业代码存在变化无法作为基准
数据处理：替换为英文括号，在专业名称中，对齐仅按照第一个括号以及以前的内容进行对齐
特殊处理：
2023年数据中招生院校中有办学类别标识如（山东公办），需要提前切分删除
2022年数据中括号全部为中文，需要替换为英文

'''


def collegeInfo():
    # 基于今年2024年专业选课限制中的学校名称为基准
    college2024 = pandas.read_excel(
        io="报考要求信息\\院校名单2024.xlsx", header=0, sheet_name="Sheet1")
    # 基于2020年第一版专业选课限制中的学校名称为基准
    college2020 = pandas.read_excel(
        io="报考要求信息\\院校名单2020.xlsx", header=0, sheet_name="Sheet1")
    # 院校名称
    collegenamechange = pandas.read_excel(
        io="报考要求信息\\高校名称变化.xlsx", header=0, sheet_name="往年院校名称")
    c1 = pandas.merge(left=college2024, right=college2020,
                      how="outer", on=["学校名称"])
    c2 = pandas.merge(left=c1, right=collegenamechange,
                      how="left", left_on=["学校名称"], right_on=["院校名称"])

    with pandas.ExcelWriter(path="报考要求信息\\高校信息.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as xlsxwriter:

        c1.to_excel(excel_writer=xlsxwriter,
                    sheet_name="Sheet1", index=False, header=True)
        c2.to_excel(excel_writer=xlsxwriter,
                    sheet_name="Sheet2", index=False, header=True)

    return


def nameChange():

    allname = pandas.read_excel(
        io="名称变化.xlsx", header=0, sheet_name="Sheet1")
    allname["namechange"] = allname.apply(lambda x: set([
        x["院校名称2024"], x["院校名称2023"], x["院校名称2022"], x["院校名称2021"], x["院校名称2020"]]), axis=1)  # type: ignore
    allname["changetimes"] = allname["namechange"].apply(lambda x: len(x))

    allname = allname[allname["changetimes"] > 1]
    print(allname.head())
    with pandas.ExcelWriter(path="名称变化.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as xlsxwriter:
        allname.to_excel(excel_writer=xlsxwriter,
                         sheet_name="名称变化", index=False, header=True)
    return


def admitPlan():
    filepath1 = "山东省招生计划数据\\山东_招生计划_2024.xlsx"
    filepath2 = "本科专业名称精确匹配.xlsx"
    # 院校名称，专业名称
    plan2024Year = pandas.read_excel(
        io=filepath2, header=0, skiprows=0, sheet_name="Sheet1")
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
        planOtherYear.drop(labels=["院校名称", "专业编号"],
                           axis="columns", inplace=True)
        # 去到括号以进行模糊匹配扩大对比时覆盖的数量
        planOtherYear["专业名称简版"] = planOtherYear["专业名称"].apply(
            lambda x: (x.split(sep="("))[0])

        plan2024Year = pandas.merge(left=plan2024Year, right=planOtherYear, how="left", left_on=[
            "院校代码", "专业名称简版"], right_on=["院校编号", "专业名称简版"], suffixes=(None, y))
        print(plan2024Year.head(n=2))
    plan2024Year.to_excel(excel_writer="本科1.xlsx",
                          sheet_name="Sheet1", index=False, header=True)


def admitPlanAddExtra(fn="本科1.xlsx"):
    # 在2024年的数据中基于专业代码进行对齐会比基于名称进行对齐多出越7000条，几乎可以全覆盖
    majorCode = "专业编号"  # 使用专业名称或者是专业名称简版(仅有括号前)
    
    # 院校名称，专业名称,之前已经完成合并的文件
    originInfo = pandas.read_excel(
        io=fn, header=0, skiprows=0, sheet_name="Sheet1")
    originInfo["专业代码"] = originInfo["专业代码"].astype(str)
    originInfo["专业代码"] = originInfo["专业代码"].apply(
        lambda x: x if len(x) == 2 else "0"+x)


    for y in ["2023","2022","2021","2020"]:
        xlsxpath = "山东省各批次志愿录取数据年份合并\\{0}一二三批次合并.xlsx".format(y)
        extraInfo = pandas.read_excel(
            io=xlsxpath, header=0, sheet_name="Sheet1")

        extraInfo[majorCode] = extraInfo[majorCode].astype(str)
        extraInfo[majorCode] = extraInfo[majorCode].apply(
            lambda x: x if len(x) == 2 else "0"+x)

        # 合并代码相同的
        originInfo = pandas.merge(left=originInfo, right=extraInfo, how="left", left_on=[
            "院校代码", "专业代码"], right_on=["院校编号", majorCode], suffixes=(None, y))
        originInfo.drop(columns=["院校编号"+y, majorCode+y],inplace=True)
        originInfo.drop_duplicates(inplace=True, keep="first")

    with pandas.ExcelWriter(path=fn, engine="openpyxl", mode="a", if_sheet_exists="replace") as xlsxwriter:

        originInfo.to_excel(excel_writer=xlsxwriter,
                           sheet_name="Sheet2", index=False, header=True)

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
    # 纵向拼接三个批次的志愿录取数据
    mergeBatch = pandas.concat(objs=batchlist, axis="index", ignore_index=True)
    print(mergeBatch.head())
    mergeBatch.to_excel(excel_writer="一二三批次合并.xlsx",
                        sheet_name="Sheet1", index=False, header=True)
    return


def mergePlanandVote():
    # 对于2023年的数据需要筛选出括号内的办学类型信息
    collegekind = r"\([^()]*[\b民办|公办|独立学院|合作办学\b][^()]*\)"

    for y in ["2023", ]:  # "2022", "2021", "2020"

        # 批次	院校代码	招生院校	专业代码	专业名称	选科要求	招生人数
        planpath = "山东省招生计划数据\\山东_招生计划_{0}.xlsx".format(y)
        planplan = pandas.read_excel(
            io=planpath, header=0, sheet_name="Sheet1")
        # 删掉办学类型信息便于后续合并对比
        planplan["院校名称"] = planplan["招生院校"].apply(
            lambda x: re.sub(pattern=collegekind, repl="", string=x))
        planplan.drop(labels="招生院校", axis="columns")

        # 投档计划数  投档最低位次   批次  院校编号  院校名称 专业编号 专业名称
        votepath = "山东省各批次志愿录取数据\\{0}一二三批次合并.xlsx".format(y)
        planvote = pandas.read_excel(
            io=votepath, header=0, sheet_name="Sheet1")
        # 合并多年的数据，按照学校和专业合并
        plan2024Year = pandas.merge(left=planplan, right=planvote, how="left", left_on=[
            "院校名称", "专业名称"], right_on=["院校名称", "专业名称"], suffixes=(None, y))

    print(plan2024Year.head(n=2))

    plan2024Year.to_excel(excel_writer="out3.xlsx",
                          sheet_name="Sheet1", index=False, header=True)

    return


def filterTargetMajor():
    # 目标选考科目限制和目标专业
    collegeMajor = ["道路与桥梁工程技术", "电气工程及自动化", "电气工程及其自动化", "电气类", "电气自动化技术",
                    "车辆工程", "智能车辆工程", "物流管理", "现代物流管理",
                    "交通运输", "交通运输类", "口腔医学", "眼视光医学", "医学检验技术", "医学实验技术",
                    "测绘工程", "测绘工程技术", "测绘类",  "测控工程", "测绘技术与仪器", "现代测控工程技术"]
    subjectLimit = ["物理", "化学", "生物", "不限", "物理或化学或生物",
                    "物理和化学和生物", "物理和化学", "物理和生物", "化学和生物",]

    xlsxpath = "out1.xlsx"
    mergePlan = pandas.read_excel(
        io=xlsxpath, header=0, sheet_name="Sheet1")
    # 符合专业和选课条件标准
    mergePlan1 = mergePlan[(mergePlan["专业名称简版"].isin(
        collegeMajor)) & (mergePlan["选科要求"].isin(subjectLimit))]

    maxadmit = 150000
    # 名次限制，大于15万或者是新开专业
    mergePlan2 = mergePlan1[((mergePlan1["投档最低位次2023"] > maxadmit) | (mergePlan1["投档最低位次2022"] >
                             maxadmit) | (mergePlan1["投档最低位次2021"] > maxadmit) | (mergePlan1["投档最低位次2020"] > maxadmit)) |
                            (pandas.isna(mergePlan1["投档最低位次2023"]) & pandas.isna(mergePlan1["投档最低位次2022"]) &
                             pandas.isna(mergePlan1["投档最低位次2021"]) & pandas.isna(mergePlan1["投档最低位次2020"]))]
    # 仅保留单一学校专业以便于查看
    mergePlan3 = mergePlan2.drop_duplicates(
        subset=["院校名称", "专业名称"], keep="first")
    # 向xlsx中写入多张工作表
    with pandas.ExcelWriter(path="初步筛选专科.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as xlsxwriter:
        mergePlan1.to_excel(excel_writer=xlsxwriter,
                            sheet_name="无排名仅专业选课限制", index=False, header=True)
        mergePlan2.to_excel(excel_writer=xlsxwriter,
                            sheet_name="排名15万后及专业选课限制", index=False, header=True)
        mergePlan3.to_excel(excel_writer=xlsxwriter,
                            sheet_name="排名15万后学校及专业去重(往年排名不全)", index=False, header=True)

    return


def filterduple():
    xlsxpath = "仅录取计划2.xlsx"
    mergePlan1 = pandas.read_excel(
        io=xlsxpath, header=0, sheet_name="Sheet1")

    mergePlan2 = mergePlan1[(pandas.isna(mergePlan1["投档计划数2023"]) & pandas.isna(
        mergePlan1["投档计划数2022"]) & pandas.isna(mergePlan1["投档计划数2021"]) & pandas.isna(mergePlan1["投档计划数2020"]))]

    with pandas.ExcelWriter(path="仅录取计划2.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as xlsxwriter:
        mergePlan2.to_excel(excel_writer=xlsxwriter,
                            sheet_name="Sheet2", index=False, header=True)
    return


def finalVote():

    finalVote = pandas.read_excel(
        io="最终报考1.xlsx", header=0, sheet_name="Sheet1")

    infoFileFine = pandas.read_excel(
        io="本科专业名称精确匹配.xlsx", header=0, sheet_name="Sheet1")
    finalVoteFine = pandas.merge(left=finalVote, right=infoFileFine, left_on=[
        "院校代码", "专业名称"], right_on=["院校代码", "专业名称"], how="left", suffixes=(None, "准确"))

    infoFileObscure = pandas.read_excel(
        io="本科专业名称模糊匹配.xlsx", header=0, sheet_name="Sheet1")
    finalVote["专业名称简版"] = finalVote["专业名称"].apply(
        lambda x: (x.split(sep="("))[0])
    finalVoteObscure = pandas.merge(left=finalVote, right=infoFileObscure, left_on=[
        "院校代码", "专业名称简版"], right_on=["院校代码", "专业名称简版"], how="left", suffixes=(None, "模糊"))

    with pandas.ExcelWriter(path="最终报考1.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as xlsxwriter:

        finalVoteFine.to_excel(excel_writer=xlsxwriter,
                               sheet_name="精确匹配", index=False, header=True)
        finalVoteObscure.to_excel(excel_writer=xlsxwriter,
                                  sheet_name="模糊匹配", index=False, header=True)
    return


if __name__ == "__main__":
    p1 = multiprocessing.Process(
        target=admitPlanAddExtra, args=("本科1.xlsx",))
    p2 = multiprocessing.Process(
        target=admitPlanAddExtra, args=("专科1.xlsx",))

    p1.start()
    p2.start()

    p2.join()
    p1.join()

    pass
