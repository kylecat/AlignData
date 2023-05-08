# Load ThingSpeak
from pathlib import Path
import pandas as pd


"""
比對記錄
    DATA_0315
        2055-02-16 01:04(0216.csv) -> 2023-02-13T11:43:39+08:00(ThingSpeak), 
"""
# 資料夾路徑
CSV_DIR = "RawData"
SourceDir = Path(CSV_DIR)

# CSV檔案
RawData_ThingSpeak = SourceDir / 'ThingSpeak_Data.csv'
RawData_0315 = SourceDir / 'DATA_0315'
RawData_0503 = SourceDir / 'DATA_0503'

csv_list = list()
DF = pd.DataFrame(columns=['Date', 'Temp', 'EC', 'Turbidity'])

if __name__ == '__main__':
    # 建立資料夾中CSV清單
    for _f in RawData_0315.glob('*.CSV'):
        csv_list.append(_f.name)
    csv_list.sort()
    # print(csv_list)

    # 讀取CSV檔案，併入DF當中
    for _f in csv_list:
        _df = pd.read_csv(RawData_0315 / _f, encoding='utf-8')
        DF = pd.concat([DF, _df], axis=0,ignore_index=True)
        # print(f"{_f}: {_df.shape[0]}")

    print(f"Total:{DF.shape[0]}")
    DF['Date'] = pd.to_datetime(DF['Date'])
    DF["AlingDate"] = DF["Date"]+pd.Timedelta(minutes=-(1440*2+801))    # 2天, 13 小時, 21 分鐘
    DF.to_csv(RawData_0315 / 'DATA_0315.csv', index=False, encoding='utf-8')
