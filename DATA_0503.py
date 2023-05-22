# Load ThingSpeak
from pathlib import Path
import pandas as pd
import numpy as np

"""
比對記錄：DATA_0503
        Step1: 2055-03-18 05:03 (0216.csv) -> 2023-03-15T16:26:00+08:00 (ThingSpeak), 
        Step2: row   2 (0101.CSV) -> 2023-03-26T04:49:34+08:00 (ThingSpeak, row 2321),
               row 728 (0101.CSV) -> 2023-04-05T10:43:47+08:00 (ThingSpeak, row 2937),
"""
# 資料夾路徑
CSV_DIR = "RawData"
SourceDir = Path(CSV_DIR)

# CSV檔案
RawData_ThingSpeak = SourceDir / 'ThingSpeak_Data.csv'
RawData_0503 = SourceDir / 'DATA_0503'

# ThingSpeak 設定
ThingSpeak_ColumnName = {'created_at': 'Date',
                         'field1': 'Voltage',
                         'field2': 'Current',
                         'field3': 'Temp',
                         'field4': 'EC',
                         'field5': 'Turbidity'}

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
    DF['Date'] = pd.to_datetime(DF['Date'])
    print(DF.head())

    TS_DF = pd.read_csv(RawData_ThingSpeak, encoding='utf-8', parse_dates=['created_at'])
    TS_DF['created_at'] = TS_DF['created_at'].dt.tz_convert('Asia/Taipei')
    # print(TS_DF.head())

    # 用定位時間把資料切出來
    SplitDate = pd.to_datetime('2023-03-26T04:49:34+08:00')  # 2023-03-26T04:49:34+08:00 (ThingSpeak, row 2321)
    ref_TS_DF = TS_DF.loc[
        TS_DF['created_at'] >= SplitDate, ['created_at', 'field1', 'field2', 'field3', 'field4', 'field5']].copy()
    ref_TS_DF.rename(columns=ThingSpeak_ColumnName, inplace=True)

    ref_TS_DF['Intervals'] = ref_TS_DF['Date'].diff().dt.total_seconds() / 60  # 計算ThingSpeak上的時間間隔
    ref_TS_DF['Intervals'] = ref_TS_DF['Intervals'].fillna(0)  # 補上第一筆資料的時間間隔
    ref_TS_DF['DataNum'] = round(ref_TS_DF['Intervals'] / 20, 0)  # 計算每20分鐘的資料數量
    ref_TS_DF['DataNum'] = ref_TS_DF['DataNum'].astype(int)
    ref_TS_DF = ref_TS_DF.copy().reset_index(drop=True)  # 複製一份後，重設 index
    ref_TS_DF['idx_0101'] = ref_TS_DF['DataNum'].cumsum()  # 計算累計的資料數量
    # print(ref_TD_DF.head())

    # 從0101.CSV中取出對應的資料
    # 第一筆資料 index
    idx_SD_0101 = 1
    idx_ThingSpeak = 0
    idx_last = {'ref': 0, 'source': 0}  # ref 為Thingspeak 最後一筆資料的idx, source 為0101.csv 最後一筆資料的idx

    ref_TS_DF['CSV_Check'] = False
    DF['align'] = None
    DF['align'] = DF['align'].astype(object)

    for _idx in range(ref_TS_DF.shape[0]):
        if _idx < 562:
            _souce_idx = idx_SD_0101 + ref_TS_DF['idx_0101'][_idx]
        elif _idx >= 562 and _idx < 616:
            _souce_idx = idx_SD_0101 + ref_TS_DF['idx_0101'][_idx] + 2
        else:
            _souce_idx = idx_SD_0101 + ref_TS_DF['idx_0101'][_idx] + 2

        _source = DF['Turbidity'][_souce_idx]
        _ref = ref_TS_DF['Turbidity'][_idx]
        _date = ref_TS_DF['Date'][_idx].strftime("%Y-%m-%d %H:%M:%S")

        if _source == _ref:
            ref_TS_DF['CSV_Check'][_idx] = True
            DF['align'][_souce_idx] = _date
            idx_last['ref'] = _idx  # 更新ThingSpeak的最後一次對齊資料的index
            idx_last['source'] = _souce_idx  # 更新0101.csv的最後一次對齊資料的index

        # 看一下為什麼錯誤
        # if _source != _ref:
        #     print(f"SD:{_source:4.2f} /\tTS:{_ref:4.2f}\t"
        #           f"{ref_TD_DF['Date'][_idx]}\t"
        #           f"S:{_souce_idx}\t ref_T:{_idx}")

    # print(ref_TD_DF['CSV_Check'].value_counts())
    print(idx_last)
    # 先儲存第一階段對齊結果
    # DF.to_csv(RawData_0503 / '0101_align.csv', index=False, encoding='utf-8')

    ## 下一階段資料對齊的方法
    # 從 ref_TD_DF(ThingSpeak) 的最後一次的比對資料，用Temp, EC, Turbidity 在 0101.csv 中找出最後一筆資料
    # 再從最後一筆資料的index開始，往後比對，直到找到一筆資料相同，就把該筆資料的index記錄下來

    print(ref_TS_DF.loc[idx_last['ref']])
    print(DF.loc[idx_last['source']])

    for _idx in range(idx_last['ref'], ref_TS_DF.shape[0]):
        _Temp = ref_TS_DF['Temp'][_idx]
        _EC = ref_TS_DF['EC'][_idx]
        _Turbidity = ref_TS_DF['Turbidity'][_idx]
        _Date = ref_TS_DF['Date'][_idx].strftime("%Y-%m-%d %H:%M:%S")

        # 在 0101.csv 中找出比對資料，找到後就跳出繼續以ThingSpeak下筆資料為基準
        for _souce_idx in range(idx_last['source'], DF.shape[0]):
            if _Temp == DF['Temp'][_souce_idx] and \
                    _EC == DF['EC'][_souce_idx] and \
                    _Turbidity == DF['Turbidity'][_souce_idx]:
                # 更新 idx_last，下次從新的資料範圍開始找
                idx_last['source'] = _souce_idx

                # 註記ref_TD_DF結果
                ref_TS_DF['CSV_Check'][_idx] = True

                # 註記對齊日期
                DF['align'][_souce_idx] = _Date
                print(f"Temp:{_Temp:4.2f} /\tEC:{_EC:4.2f} /\tTurbidity:{_Turbidity:4.2f} /\t{_Date}")
                break

    # 完成ThingSpeak與0101.csv的資料對齊
    print(f"最後一筆資料的index: {idx_last['source']}, 上傳日期: {DF['align'][idx_last['source']]}")
    print(ref_TS_DF.value_counts('CSV_Check'))  # 檢查ThingSpeak比對結果
    # DF.to_csv(RawData_0503 / '0101_align.csv', index=False, encoding='utf-8') # 檢查用
    ref_TS_DF.to_csv(RawData_0503 / 'ref_TS_DF.csv', index=False, encoding='utf-8') # 檢查用

    # 把0101.csv剩下的資料，確認缺少比數，並補上內差時間
    DF['align'] = pd.to_datetime(DF['align'])
    DF_align = DF[DF['align'].notnull()]  # 把已經對到時間的資料另外撈出來，計算資料之間的時間差
    DF_align['diff'] = DF_align['align'].diff()
    DF_align['diff'] = DF_align['diff'].dt.total_seconds() / 1200  # 換算成20分鐘的資料筆數
    DF_align['diff'] = DF_align['diff'].round()  # 四捨五入
    DF['diff_dcount'] = DF_align['diff']  # 把時間差填回原本的DF

    # 對於沒有完成時間定位的資料，檢查是跟前一資料重複
    # 先把沒有被定位ThingSpeak的資料，在DuplicateData欄位中設定為False
    DF['DuplicateData'] = DF[DF['align'].isnull()].apply(lambda x: False, axis=1)

    # DuplicateData欄位中，不是null的部分，檢查是否跟前一筆資料重複
    for _idx in range(DF.shape[0]):
        if pd.notnull(DF['DuplicateData'][_idx]) and _idx > 0:
            if DF['Temp'][_idx] == DF['Temp'][_idx - 1] and \
                    DF['EC'][_idx] == DF['EC'][_idx - 1] and \
                    DF['Turbidity'][_idx] == DF['Turbidity'][_idx - 1]:
                DF['DuplicateData'][_idx] = True

    DF['DuplicateData'] = DF['DuplicateData'].fillna(False)  # 把null填回False
    DF_Removed = DF[DF['DuplicateData'] == False].copy()  # 把不重複的資料另外撈出來，先放在DF_Removed裏面
    DF_Removed = DF_Removed.drop(['DuplicateData'], axis=1)  # 刪除'DuplicateData' 欄位

    DF_Removed['align_interpolate'] = DF_Removed['align'].interpolate(method='linear', limit_area='inside')  # 內差時間
    DF_Removed['align_interpolate'] = DF_Removed['align_interpolate'].dt.strftime("%Y-%m-%d %H:%M:%S")  # 轉換成字串

    # 對齊ThingSpeak時間的最後一筆資料位置
    # 把晚於最後一比對齊資料的其他資料都設為null(沒有意義)
    last_valid_idx = DF_Removed['align'].last_valid_index()
    print(f"最後一比對齊資料位置為{last_valid_idx}")
    DF_Removed.loc[DF_Removed.index > last_valid_idx, "align_interpolate"] = np.nan

    # 儲存第二階段對齊結果
    DF_Removed.to_csv(RawData_0503 / '0101_align2.csv', index=False, encoding='utf-8')
