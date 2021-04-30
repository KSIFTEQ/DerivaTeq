import win32com.client
import numpy as np
import pandas as pd
import time

OptionCode = win32com.client.Dispatch("CpUtil.CpOptionCode")
OptionMst = win32com.client.Dispatch("Dscbo1.OptionMst")

cnt = OptionCode.GetCount()
codes = []
k = []
tau = []
price = []
r = []
s = []
imvol = []
vol = []
print(cnt)
for i in range(cnt):
    codes.append(OptionCode.GetData(0, i))

for code in codes:
    OptionMst.SetInputValue(0, code)

    OptionMst.BlockRequest()

    k.append(OptionMst.GetHeaderValue(6))
    tau.append(OptionMst.GetHeaderValue(13))
    price.append(OptionMst.GetHeaderValue(93))
    r.append(OptionMst.GetHeaderValue(36))
    s.append(OptionMst.GetHeaderValue(106))
    if OptionMst.GetHeaderValue(108) != 0:
        imvol.append(OptionMst.GetHeaderValue(108)) # Greek IV
    else:
        imvol.append(OptionMst.GetHeaderValue(53)) # 내재변동성
    vol.append(OptionMst.GetHeaderValue(115)) # 변동성

    time.sleep(0.3)

dict = {"S":s, "K":k, "r":r, "tau":tau, "price":price, "vol":vol, "ImVol":imvol}

daily_opt_data = pd.DataFrame(data=dict, index=codes)

daily_opt_data.to_csv("daily_opt_data.csv")