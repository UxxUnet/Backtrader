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


class KAMApMACross(bt.Strategy):
    
    params = (
        ('period', 30),
        ('fast', 2),
        ('slow', 30),
        ('perc', 2.5),
    )

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a MovingAverageSimple indicator
        self.kama = bt.indicators.KAMA()
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=90)

        # Indicators for the plotting show
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
                                            subplot=True)
        bt.indicators.StochasticSlow(self.datas[0])
        bt.indicators.MACDHisto(self.datas[0])
        rsi = bt.indicators.RSI(self.datas[0])
        bt.indicators.SmoothedMovingAverage(rsi, period=15)
        bt.indicators.ATR(self.datas[0], plot=False)        
        
	
    def next(self):

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] < self.kama[0] and self.sma[0] < self.kama[0]:

                # BUY, BUY, BUY!!! (with all possible default parameters)
                #self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            if self.dataclose[0] > self.kama[0] and self.sma[0] > self.kama[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                # self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

cerebro = bt.Cerebro()

data = pd.read_csv(
    os.path.join(datadir, datafile), index_col='datetime', parse_dates=True)
data = data.loc[
    (data.index >= pd.to_datetime(from_datetime)) &
    (data.index <= pd.to_datetime(to_datetime))]
datafeed = bt.feeds.PandasData(dataname=data)
cerebro.adddata(datafeed)

cerebro.addstrategy(KAMApMACross)

cerebro.addsizer(bt.sizers.PercentSizer, percents=99)
cerebro.broker.set_cash(10000)
cerebro.broker.setcommission(commission=0.001)


logfile=datafile.split(sep=".")[0]+'_'+cerebro.strats[0][0][0].__name__+'_'+from_datetime.split()[0]+'_'+to_datetime.split()[0]+'.csv'

figfile=datafile.split(sep=".")[0]+'_'+cerebro.strats[0][0][0].__name__+'_'+from_datetime.split()[0]+'_'+to_datetime.split()[0]+'.png'

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