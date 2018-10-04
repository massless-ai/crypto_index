from cqt.strats.strategy import Strategy
import cqt
from cqt.env.mkt_env import MktEnv
from cqt.ledger.ledger import Ledger
from cqt.error_msg import error
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import copy
import pandas as pd
import numpy as np
import sys
from talib.abstract import *

class StrategyATR(Strategy):
    
 
    def __init__(self, mdl, ini_prtf, rules):
        self.asset_model = mdl
        self.initial_portfolio = ini_prtf
        self.rules = rules.copy()
        
        self.env = mdl
        self.initial = ini_prtf
        
 
        # convert data to  open        high         low       close        volume
        btc = 'btc'
        if self.asset_model.has_section(btc):
            self.prices = copy.deepcopy(self.asset_model.get_section(btc).data)
            self.prices.rename(columns={'price_open': 'open', 'price_high': 'high', 'price_low': 'low', 'price_close': 'close', 'volume_traded': 'volume'}, inplace=True)
            self.upperbw=rules['bandwidth'][1]
            self.lowerbw=rules['bandwidth'][0]
            self.smaperiod=rules['timeperiod'][0]
            self.atrperiod=rules['timeperiod'][1]
            self.close = self.prices['close'].values
            self.sma = SMA(self.prices, timeperiod=self.smaperiod)
            self.atr= ATR(self.prices, timeperiod=self.atrperiod)
            self.signal=self.close*0
            
    def apply_event_logic(self, time, prtf):
        btc = 'btc'
        if self.asset_model.has_section(btc):
            comp_btc = self.asset_model.get_section(btc)
            time_step = self.prices.index.get_loc(time)
            action = 0
            if (self.close[time_step]-self.sma[time_step]>self.upperbw*self.atr[time_step]):
                action=-1
            elif(self.close[time_step]-self.sma[time_step]<self.lowerbw*self.atr[time_step]):
                action=1
            else:
                action=0
                
            self.signal[time_step]=action 
            price_btc = comp_btc.get_price_close(time)

            if action == 1:
                prtf.buy(btc, price_btc)
            elif action == -1:
                prtf.sell(btc, price_btc)

        return prtf

