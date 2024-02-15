import os
from datetime import datetime

import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
from fastdtw import fastdtw
from sklearn.metrics import f1_score, recall_score, precision_score

import Utils

script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in

# rel_path = f"Results/" #DataBases/Barthi/active_phases
# abs_file_path = os.path.join(script_dir, rel_path)
# df = Utils.load_csv_from_folder(rel_path, 'timestamp', axis=1).loc["2022-12-19 00:00:00":"2023-01-01 23:59:59"] #"2023-01-01 23:59:59" "2022-12-19 00:29:59"

rel_path = f"Results/collection/evaluation_nn_III.csv"
abs_file_path = os.path.join(script_dir, rel_path)
df_1 = pd.read_csv(abs_file_path)
df_1 = df_1.set_index(pd.DatetimeIndex(df_1['timestamp']))
df_1 = df_1.drop(['timestamp'], axis=1)

rel_path = f"DataBases/Barthi/active_phases/hund.csv"
abs_file_path = os.path.join(script_dir, rel_path)
df_2 = pd.read_csv(abs_file_path)
df_2 = df_2.set_index(pd.DatetimeIndex(df_2['timestamp']))
df_2 = df_2.drop(['timestamp'], axis=1)

df = pd.concat([df_1, df_2], axis=1)

# df['dt'] = pd.to_datetime(df.index, format='%Y-%m-%d %H:%M:%S')
# df.set_index(pd.DatetimeIndex(df['dt']))
# df = df.drop(['dt'], axis=1)
#df = df.interpolate(method='linear', limit_direction='forward', axis=0)
# df = df.fillna(0)
#df = pd.read_csv(rel_path+"\evaluation_plausibility.csv")

df = df.dropna()

df[df < 0.2] = 0
df[df >= 0.2] = 1


#df.index = pd.to_datetime(df['time_stamp'], unit='ms')
#df.index = pd.to_datetime(df['time_reply']).apply(lambda x: x.datetime())
#df = df['kettle']
#df = df.loc["2019-11-01 00:00:00":"2019-11-14 23:59:59"]

dtw_value, dtw_path = fastdtw(df.loc[:, 'kettle'], df.loc[:, '0'])

f1 = f1_score(df.loc[:, 'kettle'], df.loc[:, '0'])
recall = recall_score(df.loc[:, 'kettle'], df.loc[:, '0'], )
precision = precision_score(df.loc[:, 'kettle'], df.loc[:, '0'])

print('F1: ' + str(f1))
print('Recall: ' + str(recall))
print('Precision: ' + str(precision))
print('DTW: ' + str(dtw_value))
plt.gcf().autofmt_xdate()
plt.plot(matplotlib.dates.num2date(matplotlib.dates.date2num(df.index)), df)
plt.legend(df.columns)
plt.show()