# all built-in libraries at the top
import os
import datetime

# all third-party libraries in the middle
import backtrader as bt
import pandas as pd

import matplotlib as plt

datadir = './data' # data path
logdir = './log' # log path
reportdir = './report' # report path
datafile = 'BTC-USDT-1h.csv' # data file
from_datetime = '2020-01-01 00:00:00' # start time 
to_datetime = '2020-04-01 00:00:00' # end time


class SMACross(bt.Strategy):
    
    params = (
        ('pfast', 10),
        ('pslow', 20),
    )

    def __init__(self):
        pass
	
    def next(self):
        pass

cerebro = bt.Cerebro()

data = pd.read_csv(
    os.path.join(datadir, datafile), index_col='datetime', parse_dates=True)
data = data.loc[
    (data.index >= pd.to_datetime(from_datetime)) &
    (data.index <= pd.to_datetime(to_datetime))]
datafeed = bt.feeds.PandasData(dataname=data)
cerebro.adddata(datafeed)

cerebro.addstrategy(SMACross)

cerebro.addsizer(bt.sizers.PercentSizer, percents=99)
cerebro.broker.set_cash(10000)
cerebro.broker.setcommission(commission=0.001)


logfile=datafile.split(sep=".")[0]+'_'+cerebro.strats[0][0][0].__name__+'_'+str(cerebro.strats[0][0][0].params.__dict__['pfast'])+'_'+str(cerebro.strats[0][0][0].params.__dict__['pslow'])+'_'+from_datetime.split()[0]+'_'+to_datetime.split()[0]+'.csv'

figfile=datafile.split(sep=".")[0]+'_'+cerebro.strats[0][0][0].__name__+'_'+str(cerebro.strats[0][0][0].params.__dict__['pfast'])+'_'+str(cerebro.strats[0][0][0].params.__dict__['pslow'])+'_'+from_datetime.split()[0]+'_'+to_datetime.split()[0]+'.png'

cerebro.addwriter(
	bt.WriterFile, 
	out=os.path.join(logdir, logfile),
	csv=True)

cerebro.run()

plt.rcParams['figure.figsize'] = [13.8, 10]
fig = cerebro.plot(style='candlestick', barup='green', bardown='red')
fig[0][0].savefig(
	os.path.join(reportdir, figfile),
	dpi=480)