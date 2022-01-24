# Labtrade with Tecnhical Analysis - Demo1
import numpy as np
import pandas as pd
from labtrade import labtrade

"""Essa estrategia deve ser utilizada apenas para fins de demonstração e teste do labtrade, portanto não utilizá-la 
para tomada de decisão no mercado real. Operações mal sucedidas podem levar a prejuísos financeiros incalculáveis."""

"""This strategy should only be used for labtrade demonstration and testing purposes, so do not use it
for decision making in the real market. Unsuccessful operations can lead to incalculable financial losses"""

# Load DataFrame (Bitmex OHLCV)
df = pd.read_csv('../dataset/OHLCV_BTCUSD_1D_2015_2021.csv')

# Features - Rolling mean
df['SMA5'] = df['c'].rolling(5).mean()
df['SMA20'] = df['c'].rolling(20).mean()
df['SMA100'] = df['c'].rolling(100).mean()

# Drop all nan
df = df.dropna()

# Amount reference
amount = 100

# Start y_test with zeros (not used with technical analysis strategy)
y_test = np.zeros(df.shape[0], )

# Start y_pred (Estratégia - cross mean 5 with 100 periods - Long:100 e Out:0)
y_pred = np.where(df.SMA5 > df.SMA100, amount, 0)

# Data preparation for LabTrade
data = pd.DataFrame()
data['true'] = y_test
data['pred'] = y_pred
data['c'] = df.c.values
# Features plot definition
data["SMA5_PLT2_BLUE"] = df.SMA5.values
data["SMA20_PLT2_RED"] = df.SMA20.values
data["SMA100_PLT2_YELLOW"] = df.SMA100.values

work = labtrade.labtrade()
work.plot(data,
          pos_true=y_test,
          pos_pred=y_pred,
          logic="long",
          stop_rate=10,  # Stop loss above 10%
          gain_rate=None,
          amount=amount,
          maker_fee=None,
          risk_free=10,
          period=365)
