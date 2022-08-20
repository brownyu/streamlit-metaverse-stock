import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import pandas as pd
from urllib.request import urlopen, Request
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def app():
    st.title('Stock News Sentiment Analysis')
    # st.write(st.session_state.close_data)
    st.write("This is the Sentiment Analysis for selected stock")

    tickers = st.multiselect(
        'Choose one or multiple stock to display the return series and other technical indicators',
        ['FSLY','IMMR', 'FB', 'U','NVDA','AAPL','MSFT',"METV"],
        ["METV"])

    web_url = 'https://finviz.com/quote.ashx?t='

    news_tables = {}

    for tick in tickers:
        url = web_url + tick
        req = Request(url=url,headers={"User-Agent": "Chrome"}) 
        response = urlopen(req)    
        html = BeautifulSoup(response,"html.parser")
        news_table = html.find(id='news-table')
        news_tables[tick] = news_table

    news_list = []

    for file_name, news_table in news_tables.items():
        for i in news_table.findAll('tr'):
            text = i.a.get_text() 
            date_scrape = i.td.text.split()
            if len(date_scrape) == 1:
                time = date_scrape[0]
            else:
                date = date_scrape[0]
                time = date_scrape[1]
            tick = file_name.split('_')[0]
            news_list.append([tick, date, time, text])

    vader = SentimentIntensityAnalyzer()
    columns = ['ticker', 'date', 'time', 'headline']
    news_df = pd.DataFrame(news_list, columns=columns)
    scores = news_df['headline'].apply(vader.polarity_scores).tolist()
    scores_df = pd.DataFrame(scores)
    news_df = news_df.join(scores_df, rsuffix='_right')
    news_df['date'] = pd.to_datetime(news_df.date).dt.date

    #st.write(news_df.head())

    mean_scores = news_df.groupby(['ticker','date']).mean()
    mean_scores = mean_scores.unstack()
    mean_scores = mean_scores.xs('compound', axis="columns").transpose()

    #st.write(mean_scores)

    for tick in tickers:
        dfName = tick + "_sentiment"
        dfName = news_df[news_df["ticker"]==tick]
        dfName.groupby('date')['compound'].agg("mean")
        fig=plt.figure(figsize=(16,8))
        plt.plot(dfName.groupby('date')['compound'].agg("mean"),label=tick,color="red")
        #dfName.plot(x="date",y="compound")
        plt.title("Stock News Sentiment Analysis of  "+ tick)
        st.pyplot(fig)
    