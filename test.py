import pandas

dt=pandas.read_excel(io="报考要求信息/专业名称变化本科专科合并扁平表.xlsx",sheet_name="Sheet1",index_col="专业名称")
print(dt.head())
print(dt.at["设施园艺","大类名称"])