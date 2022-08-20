from multiapp import MultiApp
from apps import home, news_sentiment,MACD,BollingerBand,monte_carlo# import your app modules here

app = MultiApp()

# Add all your application here
app.add_app("Home", home.app)
app.add_app("Stocks News Sentiment Analysis", news_sentiment.app)
app.add_app("Movign average convergence divergence", MACD.app)
app.add_app("Bollinger Band", BollingerBand.app)
app.add_app("Monte Carlo", monte_carlo.app)
# The main app
app.run()
