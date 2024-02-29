import pandas
import numpy

d = pandas.DataFrame(data=(("j1", 2, "a001s"),("0", 4, "c123ds"), ["1t", 12, "2223d"] )
                     , columns=["a", "b", "c"])
e = pandas.DataFrame(data=(("j1", 2, "a001s"),("0", 4, "c123ds"), ["1t", 12, "2223d"] )
                     , columns=["a", "b", "d"])

f=pandas.merge(left=d,right=e,on=["a","b"],how="outer")
g=pandas.concat(   [d,e],axis=0,ignore_index=True)
print(g)
#c = d[(d["a"].isin(numpy.arange(10,20))) & (d["c"].isin(["2", "3"]) )]
cs=d["c"].apply(lambda x : ord(x[0])*1000+int(x[1:4]))
ct=d["c"].apply(lambda x :x[4:])

ca=d["a"].apply(lambda x :  ord(x[0])*1000+ord(x[1]) if len(x)==2 else ord(x[0]) )
s="A101"

for a,b in d.items():
    print(type(a),b.to_list())


print(ct)


# for idx, row in d.iterrows():
#     if row["b"] > 3:
#         print(row)

