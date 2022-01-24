# Labtrade with RandomForestRegressor - Machine-Learning
import pickle
import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error
from labtrade import labtrade

"""Essa estrategia deve ser utilizada apenas para fins de demonstração e teste do labtrade, portanto não utilizá-la 
para tomada de decisão no mercado real. Operações mal sucedidas podem levar a prejuísos financeiros incalculáveis."""

"""This strategy should only be used for labtrade demonstration and testing purposes, so do not use it
for decision making in the real market. Unsuccessful operations can lead to incalculable financial losses"""

# Load DataFrame (Bitmex OHLCV)
df = pd.read_csv('../dataset/OHLCV_BTCUSD_1D_2015_2021.csv')

# Features
df['feature_1'] = df.c / df.c.rolling(7).mean()
df['feature_2'] = df.c / df.c.rolling(17).mean()
df['feature_3'] = df.c / df.c.rolling(27).mean()
df['feature_4'] = df.c / df.c.rolling(117).mean()
df['feature_5'] = df.c / df.c.rolling(177).mean()

# Target
time_ref = 1
df['target'] = df.c.pct_change(time_ref).shift(-time_ref)
df.drop(['time', 'o', 'h', 'l', 'vol'], axis=1, inplace=True)
df = df[:-time_ref]
df = df.dropna()

features = df.iloc[:, 1:-1]
target = df.target

# Amount reference
amount = 1000

print("\nFeatures: {}".format(features.columns.values))

# Train and Test split
train_size = int(0.8 * target.shape[0])
#train_size = int(0.1 * target.shape[0])
X_train = features[:train_size].values
y_train = target[:train_size].values
X_test = features[train_size:].values
y_test = target[train_size:].values

# Modeling
SEED = 123456
model = RandomForestRegressor(n_estimators=1000, max_depth=100, random_state=SEED)
model.fit(X_train, y_train)
# save the model to disk
pickle.dump(model, open('rf_model.sav', 'wb'))

# Load the model from disk
model = pickle.load(open('rf_model.sav', 'rb'))
# Prediction
y_pred = model.predict(X_test)

# Regression metrics
train_preds = model.predict(X_train)
test_preds = model.predict(X_test)
print("\nR2_SCORE:")
print(r2_score(y_train, train_preds))
print(r2_score(y_test, test_preds))
print("\nMSE:")
print(mean_squared_error(y_train, train_preds))
print(mean_squared_error(y_test, test_preds))

# Data preparation for LabTrade
data = pd.DataFrame()
data['true'] = y_test
data['pred'] = y_pred
data['c'] = df.c[train_size:].values

work = labtrade.labtrade()
work.plot(data,
          pct_rate=3,  # Percentage threshold rate "3%"
          logic="long-short",
          stop_rate=None,
          gain_rate=None,
          amount=amount,
          maker_fee=None,
          risk_free=10,
          period=365)
