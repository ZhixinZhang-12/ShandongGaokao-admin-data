import numpy
import pandas
import datetime
import random
import multiprocessing
import threading
import re


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


'''
原则：以2024年数据作为基准，将其他年份的数据对齐到2024年的招生计划数据
对齐基准：院校名称和专业名称两个，院校代码以及专业代码存在变化无法作为基准
数据处理：替换为英文括号，在专业名称中，对齐仅按照第一个括号以及以前的内容进行对齐
特殊处理：
2023年数据中招生院校中有办学类别标识如（山东公办），需要提前切分删除
2022年数据中括号全部为中文，需要替换为英文
'''


def nameChange():

    allname = pandas.read_excel(
        io="名称变化.xlsx", header=0, sheet_name="Sheet1")
    allname["namechange"] = allname.apply(lambda x: set([
        x["院校名称2024"], x["院校名称2023"], x["院校名称2022"], x["院校名称2021"], x["院校名称2020"]]), axis=1) # type: ignore
    allname["changetimes"] = allname["namechange"].apply(lambda x: len(x))

    allname=allname[allname["changetimes"]>1]
    print(allname.head())
    with pandas.ExcelWriter(path="名称变化.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as xlsxwriter:
        allname.to_excel(excel_writer=xlsxwriter,sheet_name="名称变化", index=False, header=True)
    return





def adminPlan():
    # 院校名称，专业名称
    plan2024Year = pandas.read_excel(
        io="山东省招生计划数据\\山东_招生计划_2024.xlsx", header=0, sheet_name="Sheet1")
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

    maxadmin = 150000
    # 名次限制，大于15万或者是新开专业
    mergePlan2 = mergePlan1[((mergePlan1["投档最低位次2023"] > maxadmin) | (mergePlan1["投档最低位次2022"] >
                             maxadmin) | (mergePlan1["投档最低位次2021"] > maxadmin) | (mergePlan1["投档最低位次2020"] > maxadmin)) |
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
                             "院校代码", "专业名称简版"], right_on=["院校代码", "专业名称简版"], how="left",suffixes=(None,"模糊"))

    with pandas.ExcelWriter(path="最终报考1.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as xlsxwriter:

        finalVoteFine.to_excel(excel_writer=xlsxwriter,
                               sheet_name="精确匹配", index=False, header=True)
        finalVoteObscure.to_excel(excel_writer=xlsxwriter,
                            sheet_name="模糊匹配", index=False, header=True)
    return

finalVote()

'''
青岛理工大学专业名称可能存在问题
济南大学 自动化类-->自动化
浙江科技学院-->浙江科技大学
长春工程学院 测绘工程2024年山东未招生
滨州学院-->山东航空学院

'''
if __name__=="__main__":
    p = multiprocessing.Process(
        target=finalVote, args=())
    pass

