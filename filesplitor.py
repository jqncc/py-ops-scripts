from filesplit.split import Split

fp=Split(inputfile="D:\\datacenter\\prod_dict.txt",outputdir="D:\\datacenter")
# 按行拆分
# fp.bylinecount(500)
# 按大小拆分
fp.bysize(size=15*1024,newline=True)