# Load ThingSpeak
from pathlib import Path
import pandas as pd

"""
比對記錄:DATA_0315
        Step1: 2055-02-16 01:04(0216.csv) -> 2023-02-13T11:43:39+08:00(ThingSpeak), 
        Step2: 比對資料
"""
# 資料夾路徑
CSV_DIR = "RawData"
SourceDir = Path(CSV_DIR)

# CSV檔案
RawData_ThingSpeak = SourceDir / 'ThingSpeak_Data.csv'
RawData_0315 = SourceDir / 'DATA_0315'
RawData_0503 = SourceDir / 'DATA_0503'
Data0315 = RawData_0315 / 'DATA_0315.csv'

"""
    # Step1.資料夾整理
    csv_list = list()
    DF = pd.DataFrame(columns=['Date', 'Temp', 'EC', 'Turbidity'])
    # 建立資料夾中CSV清單
    for _f in RawData_0315.glob('*.CSV'):
        csv_list.append(_f.name)
    csv_list.sort()
    # print(csv_list)

    # 讀取CSV檔案，併入DF當中
    for _f in csv_list:
        _df = pd.read_csv(RawData_0315 / _f, encoding='utf-8')
        DF = pd.concat([DF, _df], axis=0, ignore_index=True)
        # print(f"{_f}: {_df.shape[0]}")

    print(f"Total:{DF.shape[0]}")
    DF['Date'] = pd.to_datetime(DF['Date'])
    DF["AlignDate"] = DF["Date"] + pd.Timedelta(minutes=-(1440 * 2 + 801))  # 2天, 13 小時, 21 分鐘
    DF['AlignDate'] = DF['AlignDate'] - pd.DateOffset(years=32)  # 調整年份錯誤
    DF.to_csv(RawData_0315 / 'DATA_0315.csv', index=False, encoding='utf-8')  # 儲存調整時間後的DATA

"""
if __name__ == '__main__':
    # Step2.資料比對
    DF = pd.read_csv(Data0315, encoding='utf-8')
    DF_ThingSpeak = pd.read_csv(RawData_ThingSpeak, encoding='utf-8')
    DF_ThingSpeak.columns = ['Date', 'C2',
                             'BatteryVolate', 'BatteryCurrent',
                             'Temperature', 'EC', 'Turbidity',
                             'GPSTimeTag', 'Longitude', 'Latitude',
                             'C11', 'C12', 'C13', 'C14', ]

    DF['AlignDate'] = pd.to_datetime(DF['AlignDate'])

    DF_ThingSpeak['Date'] = pd.to_datetime(DF_ThingSpeak['Date'], format='%Y-%m-%dT%H:%M:%S+08:00')
    DF_ThingSpeak['Date'] = DF_ThingSpeak['Date'].dt.strftime('%Y-%m-%d %H:%M')  # 轉成文字並去除秒數
    DF_ThingSpeak['Date'] = pd.to_datetime(DF_ThingSpeak['Date'])  # 再轉換回時間格式

    # print(DF['AlignDate'].min())  # 檢查時間格式
    # print(DF_ThingSpeak['Date'].min())  # 檢查時間格式

    # if DF['AlignDate'][1] == DF_ThingSpeak['Date'][102]: # 檢查是否可以比對
    #     print("OK")

    DF.pop('AlignCheck')  # 清除 AlignCheck 欄位

    # 從ThingSpeak 的Date資料和  CSV上AlignDate 時間的資料 進行比對
    for _date in DF_ThingSpeak['Date']:
        if _date in DF['AlignDate'].values:
            # 找出CSV上的值
            _CSV = DF.loc[DF['AlignDate'] == _date, ['Temp', 'EC', 'Turbidity']]
            _TS = DF_ThingSpeak.loc[DF_ThingSpeak['Date'] == _date, ['Temperature', 'EC', 'Turbidity']]

            # 比對該時間 CSV的數值和ThingSpeak數值是否相同
            _ck_Temp = _CSV['Temp'].values[0] == _TS['Temperature'].values[0]
            _ck_EC = _CSV['EC'].values[0] == _TS['EC'].values[0]
            _ck_Turbidity = _CSV['Turbidity'].values[0] == _TS['Turbidity'].values[0]
            # print(f"{_date} : Temp:{_ck_Temp}, EC:{_ck_EC}, Turbidity:{_ck_Turbidity}")

            # 將數值比對結果放到 AlignCheck 當中
            DF.loc[DF['AlignDate'] == _date, 'AlignCheck'] = _ck_Temp & _ck_EC & _ck_Turbidity

    print(DF['AlignCheck'].value_counts())

    # 儲存資料
    DF.to_csv(RawData_0315 / 'DATA_0315.csv', index=False, encoding='utf-8')  # 儲存調整時間後的DATA
