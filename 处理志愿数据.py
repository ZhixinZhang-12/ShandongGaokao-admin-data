
import numpy
import pandas
import datetime
import random
import multiprocessing
import threading
import re


'''
原则：以2024年数据作为基准，将其他年份的数据对齐到2024年的招生计划数据
对齐基准：院校名称和专业名称两个，院校代码以及专业代码存在变化无法作为基准
数据处理：替换为英文括号，在专业名称中，对齐仅按照第一个括号以及以前的内容进行对齐
特殊处理：
2023年数据中招生院校中有办学类别标识如（山东公办），需要提前切分删除
2022年数据中括号全部为中文，需要替换为英文

'''
allYear = ["2024", "2023", "2022", "2021", "2020"]


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

    for y in allYear:
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


def admitPlanAddExtra(args):
    planfn, mergerTagIdx = args
    # 在2024年的数据中基于专业代码进行对齐会比基于名称进行对齐多出越7000条，几乎可以全覆盖
    batchTag = ["专业编号", "专业名称"]  # 使用专业代号或者是专业名称进行合并
    infoFTag = ["专业代码", "专业名称"]
    # 院校名称，专业名称,之前已经完成合并的文件
    originInfo = pandas.read_excel(
        io=planfn, header=0, skiprows=0, sheet_name="Sheet1")
    originInfo["专业代码"] = originInfo["专业代码"].astype(str)
    originInfo["专业代码"] = originInfo["专业代码"].apply(
        lambda x: x if len(x) == 2 else "0"+x)

    for y in allYear:
        xlsxpath = "山东省各批次志愿录取数据年份合并\\{0}一二三批次合并.xlsx".format(y)
        extraInfo = pandas.read_excel(
            io=xlsxpath, header=0, sheet_name="Sheet1")

        extraInfo[batchTag[0]] = extraInfo[batchTag[0]].astype(str)
        extraInfo[batchTag[0]] = extraInfo[batchTag[0]].apply(
            lambda x: x if len(x) == 2 else "0"+x)

        # 合并名称或代码相同的

        if mergerTagIdx == 0:  # 基于代号,仅删除院校，名称直接保留
            # 合并名称或代码相同的
            originInfo = pandas.merge(left=originInfo, right=extraInfo, how="left", left_on=[
                "院校代码", infoFTag[mergerTagIdx]], right_on=["院校编号", batchTag[mergerTagIdx]], suffixes=(None, y))
            # originInfo.drop(columns=[ "专业编号"+y], inplace=True)
        elif mergerTagIdx == 1:  # 基于名称,删掉代号并额外加入当年名称作为后续拼接对齐用
            extraInfo["专业名称"+y] = extraInfo["专业名称"]
            # 合并名称或代码相同的
            originInfo = pandas.merge(left=originInfo, right=extraInfo, how="left", left_on=[
                "院校代码", infoFTag[mergerTagIdx]], right_on=["院校编号", batchTag[mergerTagIdx]], suffixes=(None, y))

        try:
            originInfo.drop(columns=["院校名称"+y, "院校编号"+y, "批次"+y], inplace=True)
        except KeyError as ke:
            print("keyerror", ke)
            pass
        else:
            print("合并完成", y)
    originInfo.drop_duplicates(subset=[
                               "专业名称2024", "专业名称2023", "专业名称2022", "专业名称2021", "专业名称2020"], inplace=True, keep="first")
    # originInfo.to_excel(excel_writer="{}{}.xlsx".format(planfn[-10:-1],mergerTagIdx), sheet_name="Sheet1", index=False, header=True)
    originInfo.to_csv(path_or_buf="{}{}.csv".format(
        planfn[-10:-1], mergerTagIdx), index=False, header=True, encoding="gbk")
    # with pandas.ExcelWriter(path=outfn, engine="openpyxl", mode="a", if_sheet_exists="replace") as xlsxwriter:

    #     originInfo.to_excel(excel_writer=xlsxwriter,
    #                         sheet_name="Sheet1", index=False, header=True)
    return originInfo
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


def majorCount(year: str):  # 统计不同专业的录取人数总数
    yearMerge = pandas.read_excel(
        io="山东省各批次志愿录取数据年份合并/{y}一二三批次合并.xlsx".format(y=year), header=0, sheet_name="Sheet1")
    yearMerge["majorMain"] = yearMerge["专业名称"].apply(
        lambda x: re.match(r'^([^()]+)', x).group())  # type: ignore 忽视括号内的修饰部分，仅提取最前面专业名称

    countDf1 = yearMerge[["majorMain", "批次", "投档计划数"]]
    majorMerge = countDf1.groupby(by=["majorMain", "批次"], as_index=False).sum()

    majorMerge.sort_values(by=["批次", "投档计划数"], inplace=True, ascending=False)

    majorMerge.to_csv(path_or_buf="{y}adminCount.csv".format(y=year),
                      header=True, index=False, encoding="utf8")

    return majorMerge


onKey1 = ["批次", "majorMain"]


def mergeLit(li: list):
    # 并行合并数据帧用
    dt = pandas.merge(left=li[0], right=li[1], how="outer", on=onKey1)
    print(dt.head())
    return dt


def majorCount2020():
    mc2020 = pandas.read_csv(
        filepath_or_buffer="2020adminCount.csv", sep=",", header=0, encoding="utf8")
    ma = pandas.read_excel(
        io="报考要求信息/仅更名.xlsx", header=0, sheet_name="Sheet1")
    # 专业代码	专业名称	原专业代码	原专业名称
    mc20201 = pandas.merge(left=mc2020, right=ma, how="left",
                           left_on="majorMain", right_on="原专业名称")
    mc20201 = mc20201[["majorMain", "专业名称", "批次", "投档计划数"]]  # 进行规整以序号重拍
    mc20201["专业名称"].fillna(value=mc20201["majorMain"], inplace=True)
    print(mc20201.head())
    mc20201.to_csv(path_or_buf="20201adminCount.csv",
                   header=True, index=False, encoding="utf8")
    return


def serialmerge():
    df1 = pandas.read_csv(filepath_or_buffer="024专科.xls0.csv",
                          sep=",", header=0, encoding="gbk")
    df2 = pandas.read_csv(filepath_or_buffer="024专科.xls1.csv",
                          sep=",", header=0, encoding="gbk")

    col = df1.columns.to_list()
    df1 = df1[col]
    df2 = df2[col]

    df3 = pandas.concat([df1, df2], axis="index")
    df3.drop_duplicates(inplace=True)
    print(df3.head())
    df3.to_csv(path_or_buf="zktest.csv", header=True,
               index=False, encoding="gbk")

    return


charIntRe = r'(\d+)([\u4e00-\u9fff]+)'  # 用于分割前面数字后面汉字的专业类别描述


def processMajorClass0():
    fn = "报考要求信息\\temp.xlsx"
    mc = pandas.read_excel(io=fn, header=0, sheet_name="Sheet1")
    mc["类别编号"] = mc["序号"].apply(lambda x: re.match(charIntRe, x).group(1))# type: ignore
    mc["类别名称"] = mc["序号"].apply(lambda x: re.match(charIntRe, x).group(2)) # type: ignore
    mc[["类别编号", "类别名称"]].to_csv(
        path_or_buf="专业序号分割.csv", encoding="utf8", index=False, header=True)

    return

def processMajorClass1():
    mc = pandas.read_excel(io="高校专业名称变化.xlsx", header=0, sheet_name="Sheet1")
    mcsplit = pandas.read_csv(filepath_or_buffer="专业序号分割.csv",header=0,encoding="utf8")
    mc["专业编号"]=mc["专业编号"].astype(str)
    mcsplit["类别编号"]=mcsplit["类别编号"].astype(str) # 6位编号，114514(K)
    mc["专业小类编号"]=mc["专业编号"].apply(lambda x : x[0:4]) #1145
    mc["专业大类编号"]=mc["专业编号"].apply(lambda x : x[0:2]) #11
    mc=pandas.merge(left=mc,right=mcsplit,how="left",left_on=["专业大类编号"],right_on=["类别编号"],suffixes=(None,"大类"))
    mc=pandas.merge(left=mc,right=mcsplit,how="left",left_on=["专业小类编号"],right_on=["类别编号"],suffixes=(None,"小类"))
    print(mc.head())
    mc.to_csv(path_or_buf="classifiedmajor.csv", encoding="gbk", index=False, header=True)
    return

if __name__ == "__main__":

    # bk = "山东省招生计划数据/山东_招生计划_2024本科.xlsx"
    # zk = "山东省招生计划数据/山东_招生计划_2024专科.xlsx"
    # ret1 = []
    # with multiprocessing.Pool(processes=4) as p:
    #     ret1 = p.map(admitPlanAddExtra, [(bk, 0), (bk, 1), (zk, 0), (zk, 1)])

    processMajorClass1()
    pass
