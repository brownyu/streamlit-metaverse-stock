import streamlit as st
from pandas_datareader import data
import pandas as pd
import numpy as np
from datetime import date 
import datetime 
from math import floor
import plotly.express as px 


def get_wr(high, low, close, lookback):
    highh = high.rolling(lookback).max() 
    lowl = low.rolling(lookback).min()
    wr = -100 * ((highh - close) / (highh - lowl))
    return wr

def get_macd(price, slow, fast, smooth):
    exp1 = price.ewm(span = fast, adjust = False).mean()
    exp2 = price.ewm(span = slow, adjust = False).mean()
    macd = pd.DataFrame(exp1 - exp2).rename(columns = {'Close':'macd'})
    signal = pd.DataFrame(macd.ewm(span = smooth, adjust = False).mean()).rename(columns = {'macd':'signal'})
    hist = pd.DataFrame(macd['macd'] - signal['signal']).rename(columns = {0:'hist'})
    return macd, signal, hist

def get_bollinger_bands(prices, rate=20):
    sma = prices.rolling(rate).mean()
    std = prices.rolling(rate).std()
    bollinger_up = sma + std * 2 # Calculate top band
    bollinger_down = sma - std * 2 # Calculate bottom band
    return bollinger_up, bollinger_down

def implement_wr_macd_bb_strategy(prices, wr, macd, macd_signal, bollinger_up, bollinger_down):    
    buy_price = []
    sell_price = []
    wr_macd_bb_signal = []
    signal = 0

    for i in range(len(wr)):
        if wr[i-1] > -50 and wr[i] < -50 and macd[i] > macd_signal[i] and bollinger_down[i] > prices[i]:
            if signal != 1:
                buy_price.append(prices[i])
                sell_price.append(np.nan)
                signal = 1
                wr_macd_bb_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                wr_macd_bb_signal.append(0)
                
        elif wr[i-1] < -50 and wr[i] > -50 and macd[i] < macd_signal[i] and bollinger_up[i] < prices[i]:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(prices[i])
                signal = -1
                wr_macd_bb_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                wr_macd_bb_signal.append(0)
        
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            wr_macd_bb_signal.append(0)
            
    return buy_price, sell_price, wr_macd_bb_signal


def app():
    ## upload title and image 
    st.title("MetaVerse Stock")   
    st.image('./meta.jpg')
    today=date.today()
    
    ## let user choose stock and date
    st.write(""" 
    ### Choose one or multiple metaverse stock from the list
    """)
    tickers = st.multiselect("",
        ['FSLY','IMMR', 'FB', 'U','NVDA','AAPL','MSFT',"METV"],
        ["METV"])
    start_date=st.date_input(label="Starting Date",value=datetime.date(2021,7,1))
    end_date=st.date_input("End Date",value=datetime.date(today.year,today.month,today.day))
   

    if start_date >= end_date:
        st.error('Error: End date must fall after start date.')
    elif end_date>today:
        st.error("Error: End date can not after today ")

    start_date=start_date.strftime('%Y-%m-%d')
    end_date=end_date.strftime('%Y-%m-%d')

    ## Get data for stock
    panel_data = data.DataReader(tickers,'yahoo', start_date, end_date)
    # data = panel_data[['Close', 'Adj Close']]
    close_data = panel_data['Close']
    adj_close_data = panel_data['Adj Close']
    fig_close_price=px.line(close_data,x=close_data.index,y=tickers)
    st.plotly_chart(fig_close_price)
    

    st.session_state['close_data'] = close_data
    st.session_state['adj_close_data'] = adj_close_data

    # generate return series diagram    
    st.write("""
    ### Return series for the selected stock(s) in table form
    """)
    return_series_adj = (adj_close_data.pct_change()+ 1).cumprod() - 1
    st.write(return_series_adj)
    fig_return_series =px.line(return_series_adj,x=return_series_adj.index,y=tickers)
    st.plotly_chart(fig_return_series)
    


    total_invest_list=[]
    profit_percent_list=[]
    st.title("Investment return  based on MACD, Bollinger Bond and Williams % R")
    investment_value=st.slider("Investment Value in $",min_value=10000,max_value=999999,value=10000,step=50000)

    for stock in tickers:
        panel_data = data.DataReader(stock,'yahoo', start_date, end_date)
        high_data=panel_data["High"]
        low_data=panel_data["Low"]
        close_data_copy=panel_data["Close"]
        frames =[low_data,close_data_copy,high_data]

        df=pd.concat(frames,axis=1,join="inner")
        df['wr_14'] = get_wr(df['High'], df['Low'], df['Close'], 14)
        df['macd'] = get_macd(df['Close'], 26, 12, 9)[0]
        df['macd_signal'] = get_macd(df['Close'], 26, 12, 9)[1]
        df['macd_hist'] = get_macd(df['Close'], 26, 12, 9)[2]
        bollinger_up, bollinger_down = get_bollinger_bands(df['Close'])
        df['bollinger_up'] = bollinger_up
        df['bollinger_down'] = bollinger_down
        df = df.dropna()
        buy_price, sell_price, wr_macd_bb_signal = implement_wr_macd_bb_strategy(df['Close'], df['wr_14'], df['macd'], df['macd_signal'], df['bollinger_up'], df['bollinger_down'])
        position = []
        for i in range(len(wr_macd_bb_signal)):
            if wr_macd_bb_signal[i] > 1:
                position.append(0)
            else:
                position.append(1)
                
        for i in range(len(df['Close'])):
            if wr_macd_bb_signal[i] == 1:
                position[i] = 1
            elif wr_macd_bb_signal[i] == -1:
                position[i] = 0
            else:
                position[i] = position[i-1]
                
        close_price = df['Close']
        wr = df['wr_14']
        macd_line = df['macd']
        signal_line = df['macd_signal']
        bollinger_up_line = df['bollinger_up']
        bollinger_down_line = df['bollinger_down']
        wr_macd_bb_signal = pd.DataFrame(wr_macd_bb_signal).rename(columns = {0:'wr_macd_bb_signal'}).set_index(df.index)
        position = pd.DataFrame(position).rename(columns = {0:'wr_macd_bb_position'}).set_index(df.index)

        frames = [close_price, wr, macd_line, signal_line, wr_macd_bb_signal, bollinger_up_line, bollinger_down_line, position]
        strategy = pd.concat(frames, join = 'inner', axis = 1)
        df_ret = pd.DataFrame(np.diff(df['Close'])).rename(columns = {0:'returns'})
        wr_macd_bb_strategy_ret = []

        for i in range(len(df_ret)):
            try:
                returns = df_ret['returns'][i] * strategy['wr_macd_bb_position'][i]
                wr_macd_bb_strategy_ret.append(returns)
            except:
                pass
            
        wr_macd_bb_strategy_ret_df = pd.DataFrame(wr_macd_bb_strategy_ret).rename(columns = {0:'wr_macd_bb_returns'})

        number_of_stocks = floor(investment_value / df['Close'][0])
        wr_macd_bb_investment_ret = []

        for i in range(len(wr_macd_bb_strategy_ret_df['wr_macd_bb_returns'])):
            returns = number_of_stocks * wr_macd_bb_strategy_ret_df['wr_macd_bb_returns'][i]
            wr_macd_bb_investment_ret.append(returns)

        wr_macd_bb_investment_ret_df = pd.DataFrame(wr_macd_bb_investment_ret).rename(columns = {0:'investment_returns'})
        total_investment_ret = round(sum(wr_macd_bb_investment_ret_df['investment_returns']), 2)
        profit_percentage = floor((total_investment_ret / investment_value) * 100)
        total_invest_list.append(total_investment_ret)
        profit_percent_list.append(profit_percentage)
    
    if total_invest_list:
        d_data={
            "Total Investment Return":total_invest_list,
            "Profit_Percentage in %":profit_percent_list}
        display_df=pd.DataFrame(d_data,index=tickers)
        st.table(display_df)
