import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import copy
from matplotlib import *



def get_sma(prices, rate):
        return prices.rolling(rate).mean()

def get_bollinger_bands(prices, rate=20):
    sma = prices.rolling(rate).mean()
    std = prices.rolling(rate).std()
    bollinger_up = sma + std * 2 # Calculate top band
    bollinger_down = sma - std * 2 # Calculate bottom band
    return (bollinger_up, bollinger_down)

def app():
    close_data = st.session_state['close_data']
    columns=close_data.columns
    columns_list=columns.tolist()

    df = copy.deepcopy(close_data)
    st.write("Buy when close price below Bollinger region")
    st.write("Sell when close price above Bollinger region")

    stock = st.selectbox(
    'Choose a stock to display its Bollinger Band',
    columns_list)

    bollinger_up, bollinger_down = get_bollinger_bands(df[stock])
    df["bollinger_up"]=bollinger_up
    df["bollinger_down"]=bollinger_down
    #df['Buy_Signal'] = np.where(df.bollinger_down > df[stock], True, False)
    #df['Sell_Signal'] = np.where(df.bollinger_up < df[stock], True, False)
        
    '''
    open_position = False

    for i in range(len(df)):
        if df.bollinger_down[i] > df[stock][i]:
            if open_position == False:
                buys.append(i)
                open_position = True
        elif df.bollinger_up[i] < df[stock][i]:
            if open_position:
                sells.append(i)
                open_position = False
    '''

    def get_signal(data):
        buys = []
        sells = []

        for i in range(len(data[stock])):
            if data["bollinger_down"][i] > data[stock][i]:
                buys.append(data[stock][i])
                sells.append(np.nan)

            elif data["bollinger_up"][i] < data[stock][i]:
                sells.append(data[stock][i])
                buys.append(np.nan)
            else:
                sells.append(np.nan)
                buys.append(np.nan)
        return(buys,sells)

    df["Buy"]=get_signal(df)[0]
    df["Sell"]=get_signal(df)[1]
    
    fig=plt.figure(figsize=(12.2,6.4))
    x_axis=df.index
    plt.fill_between(x_axis,df['bollinger_up'],df['bollinger_down'],facecolor='blue', alpha=0.3,label="Bollinger")
    plt.scatter(df.index,df["Buy"],color="green",label="Buy",marker="^",s=100)
    plt.scatter(df.index,df["Sell"],color="red",label="Sell",marker="v",s=100)
    plt.plot(df[stock],label="Close Price",color="gold",alpha=0.5)
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.title("Bollinger Band")
    plt.legend()
    plt.xticks(rotation=45)
    plt.show()
    st.pyplot(fig)