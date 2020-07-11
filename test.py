# all built-in libraries at the top
import os
import datetime

# all third-party libraries in the middle
import backtrader as bt
import pandas as pd


datadir = './data' # data path
logdir = './log' # log path
reportdir = './report' # report path
datafile = 'BTC_USDT_1h_SMACross.csv' # data file
from_datetime = '2020-01-01 00:00:00' # start time 
to_datetime = '2020-04-01 00:00:00' # end time


data = pd.read_csv(os.path.join(datadir, datafile))
index=data.columns.drop(['Unnamed: 0','RankReturn', 'RankMaxDrawDown', 'RankWinRatio', 'RankAverageWinLossRatio', 'Score'])
print(index)





