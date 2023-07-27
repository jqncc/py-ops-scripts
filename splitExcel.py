#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pandas as pd
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE


def splitExcelByRow(excelPath, sheetIndex=0, rowLimit=65535, encoding='utf-8'):
    """
    横向拆分excel
    :param excelPath: excel文件路径
    :param sheetIndex: 要拆分的sheet索引
    :param rowLimit: 每个文件行数
    :param encoding: 文件编码
    :return:
    """
    excelPathSplit = os.path.splitext(excelPath)
    if excelPathSplit[1] == 'xls' and rowLimit >= 65534:
        rowLimit = 65534
    df = pd.read_excel(excelPath, sheet_name=sheetIndex)
    nrows, ncols = df.shape  # 获取总行和列

    sheets = nrows / rowLimit
    if not sheets.is_integer():
        sheets = sheets + 1

    title_row = df.head(1)

    for i in range(0, int(sheets)):
        startIndex = i * rowLimit + 1
        endIndex = (i + 1) * rowLimit + 1
        splitdata = df.iloc[startIndex:endIndex, :]
        splitdata.replace(ILLEGAL_CHARACTERS_RE, '', inplace=True, regex=True)
        newexcelPath = excelPathSplit[0] + "_" + str(i) + '.xlsx'
        splitdata.to_excel(newexcelPath, sheet_name='sheet0', index=False)
        print("新文件"+newexcelPath)


splitExcelByRow('C:\\Users\\Administrator\\Desktop\\新建文件夹\\分类训练数据集\\网上商品库\\原始商品2.xlsx', rowLimit=63000)
