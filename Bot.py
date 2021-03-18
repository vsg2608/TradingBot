import websocket, json, talib, numpy
import numpy as np
from datetime import datetime

from binance.enums import ORDER_TYPE_MARKET,KLINE_INTERVAL_1MINUTE,SIDE_BUY,SIDE_SELL
import TaskManager

import matplotlib.pyplot as plt
from matplotlib import dates, ticker
import matplotlib as mpl
from mpl_finance import candlestick_ohlc

mpl.style.use('default')


#%%

def plotGraph(data):
    ohlc_data=[]
    for line in data:
        ohlc_data.append((dates.datestr2num(line[0]), np.float64(line[1]), np.float64(line[2]), np.float64(line[3]), np.float64(line[4])))
    
    fig, ax1 = plt.subplots()
    candlestick_ohlc(ax1, ohlc_data, width = 0.5/(24*60), colorup = 'g', colordown = 'r', alpha = 0.8)
    
    ax1.xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%Y %H:%M'))
    ax1.xaxis.set_major_locator(ticker.MaxNLocator(10))
    
    plt.xticks(rotation = 30)
    plt.grid()
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title('Historical Data EURUSD')
    plt.tight_layout()
    plt.show()

#%%
class Bot():
    
    def __init__(self, userClient, configuration):
        self.in_position= False
        self.client= userClient
        self.RSI_PERIOD= configuration['RSI_PERIOD']
        self.RSI_PERIOD_5= configuration['RSI_PERIOD_5']
        self.RSI_OVERBOUGHT = configuration['RSI_OVERBOUGHT']
        self.RSI_OVERSOLD = configuration['RSI_OVERSOLD']
        self.TRADE_SYMBOL = configuration['TRADE_SYMBOL']
        self.TRADE_COIN = configuration['TRADE_COIN']
        self.TRADE_QUANTITY = configuration['TRADE_QUANTITY']
        self.SOCKET= configuration['SOCKET']
        
        self.opens= []
        self.highs= []
        self.closes= []
        self.lows= []
        self.timestamps= []
        self.data= []
        self.isInPosition()
        self.getHistorialData()
        
    def isInPosition(self):
        self.in_position= TaskManager.isInOrder(self.client, self.TRADE_COIN, self.TRADE_QUANTITY)
        print('IS IN POSITION: %s'%(self.in_position))
        
    def getHistorialData(self):
        histoicalData=self.client.get_historical_klines(self.TRADE_SYMBOL, KLINE_INTERVAL_1MINUTE, "2 hour ago UTC")
        
        for dataPoint in histoicalData:
            self.timestamps.append(datetime.fromtimestamp(dataPoint[0]/1000))
            self.closes.append(float(dataPoint[4]))
            self.opens.append(float(dataPoint[1]))
            self.highs.append(float(dataPoint[2]))
            self.lows.append(float(dataPoint[3]))
            
            self.data.append((str(datetime.fromtimestamp(dataPoint[0]/1000)),dataPoint[4],dataPoint[1],dataPoint[2],dataPoint[3]))
        #plotGraph(self.data)
        self.checkRsi()
    
    def start(self):
        print("bot started")
        ws = websocket.WebSocketApp(self.SOCKET, on_open=self.on_open, on_close=self.on_close, on_message=self.on_message)
        ws.run_forever()
    
        
    def on_open(ws):
        print('opened connection for: '+ str(ws.TRADE_SYMBOL))
    
    def on_close(ws):
        print('closed connection for: '+ str(ws.TRADE_SYMBOL))
    
    def checkRsi(ws):
        closes_5= []
        for i in range(4,len(ws.closes),5):
            closes_5.append(ws.closes[i])
        if len(ws.closes) > ws.RSI_PERIOD and len(closes_5) > ws.RSI_PERIOD_5:
            np_closes = numpy.array(ws.closes)
            rsi = talib.RSI(np_closes, ws.RSI_PERIOD)
            last_rsi = rsi[-1]
            
            np_closes_5 = numpy.array(closes_5)
            rsi_5 = talib.RSI(np_closes_5, ws.RSI_PERIOD_5)
            last_rsi_5 = rsi_5[-1]
            #print("the current rsi is {}".format(last_rsi))
            print('%s:\tClose:\t%s\t|\tRSI:\t%s\tRSI-5:\t%s'%(ws.TRADE_SYMBOL,ws.closes[-1], last_rsi,last_rsi_5))
            if last_rsi > ws.RSI_OVERBOUGHT:
                if ws.in_position:
                    print("Overbought! Sell! Sell! Sell!")
                    # put binance sell logic here
                    order_succeeded = TaskManager.order(ws.client,SIDE_SELL, ws.TRADE_QUANTITY, ws.TRADE_SYMBOL)
                    ws.isInPosition()
                else:
                    print("It is overbought, but we don't own any. Nothing to do.")
            
            if last_rsi < ws.RSI_OVERSOLD:
                if ws.in_position:
                    print("It is oversold, but you already own it, nothing to do.")
                else:
                    print("Oversold! Buy! Buy! Buy!")
                    # put binance buy order logic here
                    order_succeeded = TaskManager.order(ws.client,SIDE_BUY, ws.TRADE_QUANTITY, ws.TRADE_SYMBOL)
                    ws.isInPosition()
    
    
    def on_message(ws, message):
        json_message = json.loads(message)
    
        candle = json_message['k']
    
        is_candle_closed = candle['x']
        closePrice = candle['c']
        openPrice= candle['o']
        highPrice= candle['h']
        lowPrice= candle['l']
        dataTimeStamp= datetime.fromtimestamp(candle['t']/1000)
        #print("%s\t:\t%s\t:\t%s\t:\t%s\t:\t%s\t"%(dataTimeStamp,openPrice,highPrice,lowPrice,closePrice))
        if is_candle_closed:
            #print("candle closed at {}".format(closePrice))
            ws.closes.append(float(closePrice))
            ws.opens.append(float(openPrice))
            ws.highs.append(float(highPrice))
            ws.lows.append(float(lowPrice))
            ws.timestamps.append(dataTimeStamp)
            ws.data.append((str(dataTimeStamp),openPrice,highPrice,lowPrice,closePrice))
            # PLOTTING HERE
            #plotGraph(ws.data)
            ws.checkRsi()
            
            