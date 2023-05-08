# Load ThingSpeak
from pathlib import Path
import pandas as pd

"""
比對記錄：DATA_0503
        Step1: 2055-03-18 05:03 (0216.csv) -> 2023-03-15T16:26:00+08:00 (ThingSpeak), 
        Step2: row 2 (0101.CSV) -> 2023-03-26T04:49:34+08:00 (ThingSpeak, row 2321),
"""
# 資料夾路徑
CSV_DIR = "RawData"
SourceDir = Path(CSV_DIR)

# CSV檔案
RawData_ThingSpeak = SourceDir / 'ThingSpeak_Data.csv'
RawData_0503 = SourceDir / 'DATA_0503'

"""
    # Step1.資料夾整理：正常時間
    csv_list = list()
    DF = pd.DataFrame(columns=['Date', 'Temp', 'EC', 'Turbidity'])
    # 建立資料夾中CSV清單
    for _f in RawData_0503.glob('*.CSV'):
        csv_list.append(_f.name)
    csv_list.sort()
    csv_list.remove("0101.CSV")  # 先移除時間日期有問題的 0101.csv
    print(csv_list)

    # 讀取CSV檔案，併入DF當中
    for _f in csv_list:
        _df = pd.read_csv(RawData_0503 / _f, encoding='utf-8')
        DF = pd.concat([DF, _df], axis=0, ignore_index=True)
        print(f"{_f}: {_df.shape[0]}")
    # print(f"Total:{DF.shape[0]}")


    DF['Date'] = pd.to_datetime(DF['Date'])
    DF["AlignDate"] = DF["Date"] + pd.Timedelta(minutes=-(1440 * 2 + 801))  # 2天, 13 小時, 21 分鐘
    DF['AlignDate'] = DF['AlignDate'] - pd.DateOffset(years=32)  # 調整年份錯誤
    print(DF.head())
    DF.to_csv(RawData_0503 / 'DATA_0503.csv', index=False, encoding='utf-8')  # 儲存調整時間後的DATA
"""

if __name__ == '__main__':
    # Step2.RTC錯誤對時：0101.CSV
    DF = pd.read_csv(RawData_0503 / '0101.CSV', encoding='utf-8')

