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
indfile = 'BTC_USDT_1h_SMACross.csv'
from_datetime = '2020-01-01 00:00:00' # start time 
to_datetime = '2020-04-01 00:00:00' # end time


class DoubleSMACross(bt.Strategy):
    
    params = (
        ('maperiod1', 5),
        ('maperiod2', 90),
    )

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a MovingAverageSimple indicator
        self.sma1 = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod1)
        self.sma2 = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod2)

        # Indicators for the plotting show
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
                                            subplot=True)
        bt.indicators.StochasticSlow(self.datas[0])
        bt.indicators.MACDHisto(self.datas[0])
        rsi = bt.indicators.RSI(self.datas[0])
        bt.indicators.SmoothedMovingAverage(rsi, period=self.params.maperiod1)
        bt.indicators.SmoothedMovingAverage(rsi, period=self.params.maperiod2)
        bt.indicators.ATR(self.datas[0], plot=False)        
    
    def start(self):
        self.start_val = self.broker.get_value()    
	
    def stop(self):
        self.stop_val = self.broker.get_value()
        self.roi = (self.broker.get_value() / self.start_val) - 1.0
        # print('Start Value: ${}'.format(self.start_val))
        # print('End Value: ${}'.format(self.broker.getvalue()))
        # print('ROI:        {:.2f}%'.format(100.0 * self.roi))

    def next(self):

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.sma1[0] > self.sma2[0]:

                # BUY, BUY, BUY!!! (with all possible default parameters)
                #self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            if self.sma1[0] < self.sma2[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                # self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()


def printTradeAnalysis(analyzer):
    '''
    Function to print the Technical Analysis results in a nice format.
    '''
    #Get the results we are interested in
    total_open = analyzer.total.open
    total_closed = analyzer.total.closed
    total_won = analyzer.won.total
    total_lost = analyzer.lost.total
    win_streak = analyzer.streak.won.longest
    lose_streak = analyzer.streak.lost.longest
    pnl_net = round(analyzer.pnl.net.total,4)
    strike_rate = '{:.2f}%'.format((total_won / total_closed) * 100)
    aver_won = round(analyzer.won.pnl.average,4)
    aver_los = round(analyzer.lost.pnl.average,4)
    aver_w_l_rat = round(-aver_won/aver_los,4)

    #Designate the rows
    h1 = ['Total Open', 'Total Closed', 'Win Trades', 'Loss Trades']
    h2 = ['Win Ratio','Longest Win Streak', 'Longest Loss Streak', 'PnL Net']
    h3 = ['Average Win','Average Loss','AverageWinLossRatio','']
    r1 = [total_open, total_closed,total_won,total_lost]
    r2 = [strike_rate, win_streak, lose_streak, pnl_net]
    r3 = [aver_won, aver_los, aver_w_l_rat,'']
    #Check which set of headers is the longest.
    if len(h1) > len(h2):
        header_length = len(h1)
    else:
        header_length = len(h2)
    #Print the rows
    # print_list = [h1,r1,h2,r2,h3,r3]
    # row_format ="{:<23}" * (header_length + 1)
    # print("Trade Analysis Results:")
    # for row in print_list:
    #     print(row_format.format('',*row))
    return total_closed,total_won,total_lost,round(total_won / total_closed,4),aver_won,aver_los,win_streak,lose_streak,aver_w_l_rat


if __name__ == '__main__':
    cerebro = bt.Cerebro()

    data = pd.read_csv(
        os.path.join(datadir, datafile), index_col='datetime', parse_dates=True)
    data = data.loc[
        (data.index >= pd.to_datetime(from_datetime)) &
        (data.index <= pd.to_datetime(to_datetime))]
    datafeed = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(datafeed)

    cerebro.optstrategy(DoubleSMACross,maperiod1=range(5, 11),maperiod2=range(50, 91)) 


    cerebro.addsizer(bt.sizers.PercentSizer, percents=99)
    cerebro.broker.set_cash(10000)
    cerebro.broker.setcommission(commission=0.001)
    #cerebro.addobserver(bt.observers.Value)
    cerebro.addanalyzer(bt.analyzers.Returns, _name = 'r')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name = 'sr') 
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='dw')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
    #logfile=datafile.split(sep=".")[0]+'_'+cerebro.strats[0][0][0].__name__+'_'+str(cerebro.strats[0][0][0].params.__dict__['maperiod1'])+'_'+str(cerebro.strats[0][0][0].params.__dict__['maperiod2'])+'_'+from_datetime.split()[0]+'_'+to_datetime.split()[0]+'.csv'

    #figfile=datafile.split(sep=".")[0]+'_'+cerebro.strats[0][0][0].__name__+'_'+str(cerebro.strats[0][0][0].params.__dict__['maperiod1'])+'_'+str(cerebro.strats[0][0][0].params.__dict__['maperiod2'])+'_'+from_datetime.split()[0]+'_'+to_datetime.split()[0]+'.png'

    # cerebro.addwriter(
    # 	bt.WriterFile, 
    # 	out=os.path.join(logdir, logfile),
    # 	csv=True)



    # plt.rcParams['figure.figsize'] = [13.8, 10]
    # fig = cerebro.plot(style='candlestick', barup='green', bardown='red')
    # fig[0][0].savefig(
    # 	os.path.join(reportdir, figfile),
    # 	dpi=480)

    # print('Final Balance: %.2f' % cerebro.broker.getvalue())
    # for e in strat.analyzers:
    #     e.print()
    # print(strat.analyzers)

    strats=cerebro.run()

    data = pd.read_csv(os.path.join(datadir, indfile))
    index=data.columns.drop(['Unnamed: 0','RankReturn', 'RankMaxDrawDown', 'RankWinRatio', 'RankAverageWinLossRatio', 'Score'])
    #print(list(index))
    stname = 'DoubleSMACross' #cerebro.strats[0][0][0].__name__
    
    data_list=[]
    for run in strats:
        for strat in run:
            # print the analyzers
            # for e in strat.analyzers:
            #     e.print()
            # print('Returns: {}'.format(round(strat.analyzers.r.get_analysis()['rtot'],2)))
            p=printTradeAnalysis(strat.analyzers.ta.get_analysis())
            # print('Sharpe Ratio: ',strat.analyzers.sr.get_analysis()['sharperatio'])
            # print('MaxDrawDown Ratio: {}'.format(round(strat.analyzers.dw.get_analysis().max.drawdown,2)))
            # print('MaxDrawDown Money: {}'.format(round(strat.analyzers.dw.get_analysis().max.moneydown,2)))
            # print('SQN: {}'.format(round(strat.analyzers.sqn.get_analysis().sqn,2)))

            #Finally plot the end results
            #cerebro.plot(style='candlestick')
        
            data = [stname, strat.params.maperiod1,strat.params.maperiod2,\
                round(strat.analyzers.r.get_analysis()['rtot'],2),round(strat.analyzers.dw.get_analysis().max.drawdown,2)]
            data.extend(list(p))
            data_list.append(data)

    data2 = pd.DataFrame(columns=list(index),data=data_list)
    data2['RankReturn']= data2['Return'].rank(ascending=False)
    data2['RankMaxDrawDown']= data2['MaxDrawDown'].rank(ascending=True)
    data2['RankWinRatio']= data2['WinRatio'].rank(ascending=False)
    data2['RankAverageWinLossRatio']= data2['AverageWinLossRatio'].rank(ascending=False)
    data2['Score']=data2[['RankReturn','RankMaxDrawDown','RankWinRatio','RankAverageWinLossRatio']].mean(1)
    
    datafile="BTC_USDT_1h_%s.csv"%(stname)
    data2.to_csv(os.path.join(reportdir, datafile),index=False, header=True) 
    print(data2.sort_values(by='Score')[0:5])


    print("Best parameters: ma_pfast: %s; ma_pslow: %s;"%(int(data2.sort_values(by='Score')[0:1]['sma_pfast']),int(data2.sort_values(by='Score')[0:1]['sma_pslow'])))
