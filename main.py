from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import random as rn
from statistics import mean
import pandas as pd
from datetime import date, timedelta, datetime
import requests

app = FastAPI()

templates = Jinja2Templates(directory="templates")
dfaapl = pd.read_csv('aapl.csv', index_col=7, parse_dates=True)
dfaapl = dfaapl.iloc[15:].copy() #skip first 15 rows RSI empty

dfspy = pd.read_csv('spy.csv', index_col=7, parse_dates=True)
dfspy = dfspy.iloc[15:].copy() #skip first 15 rows RSI empty

dfmsft = pd.read_csv('msft.csv', index_col=7, parse_dates=True)
dfmsft = dfspy.iloc[15:].copy() #skip first 15 rows RSI empty

with open('contest.csv') as f:
    lenContest = sum(1 for _ in f)

def getTarget(t, df):
  target = t # 10 %
  r = rn.randint(0,len(df)-150)
  buy = {'dateOpen':df.index[r], 
         'open':df.iloc[r,0], 
         'dateClose':df.index[0], 
         'close':0,
         'rsi':df.iloc[r,6]
         }
  while r<len(df):
    close = df.iloc[r,3]
    if close >= buy['open']*(1+target):
      buy['dateClose'] = df.index[r]
      buy['close'] = df.iloc[r,3]
      #print(buy)
      return buy
    r = r + 1

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    data = {
        "request": request,
        "message": "Hello, World!",
    }
    return templates.TemplateResponse("index.html", data)

@app.get("/contest", response_class=HTMLResponse)
def contest(request: Request):
        a = rn.randint(1, lenContest-5)
        b = 1
        with open('contest.csv') as f:
            while b<=a:
                f.readline()
                b = b + 1
            lines = [f.readline(), f.readline(), f.readline()]
        res = {}
        for x in lines:
            a = x.strip('\n')
            a= a.split(',')
            res[a[0]] = {"avgDays": a[1], 
                         "annualYield":float(a[2])} 
        res = dict(sorted(res.items()))
        data = {
            "request": request,
            "results": res
        }
        return templates.TemplateResponse("contest.html", data)

@app.get("/api/{ticker}")
def api(ticker: str):
   tickers = {'aapl':dfaapl, 'spy':dfspy,'msft':dfmsft}
   if ticker not in tickers:
      return {
         "message": "Ticker not found"
         }
   orders = []
   avgDays = []
   target = 0.10 # 10 %
   for x in range(50):
       buy = getTarget(target, tickers[ticker])
       if buy is not None:
          deltaDays = (buy['dateClose'] - buy['dateOpen']).days
          buy['deltaDays'] = deltaDays
          buy['timestampOpen'] = buy['dateOpen']
          buy['dateOpen'] = datetime.strftime(buy['dateOpen'],'%d-%b-%y')
          buy['dateClose'] = datetime.strftime(buy['dateClose'],'%d-%b-%y')
          orders.append(buy)
          avgDays.append(deltaDays)
   annualYield = (1+target)**(365/mean(avgDays)) - 1 
   data = {
        "avgDays": mean(avgDays),
        "target": target,
        "annualYield": annualYield
    }
   return data

@app.get("/rand/{ticker}", response_class=HTMLResponse)
def rand(request: Request, ticker: str):
    tickers = {'aapl':dfaapl, 'spy':dfspy,'msft':dfmsft}
    if ticker not in tickers:
      data = { 
        "request": request, 
        "message": "Ticker not found" 
        }
      return templates.TemplateResponse("error.html", data)
    orders = []
    avgDays = []
    target = 0.10 # 10 %
    for x in range(50):
        buy = getTarget(target, tickers[ticker])
        if buy is not None:
           deltaDays = (buy['dateClose'] - buy['dateOpen']).days
           buy['deltaDays'] = deltaDays
           buy['timestampOpen'] = buy['dateOpen']
           buy['dateOpen'] = datetime.strftime(buy['dateOpen'],'%d-%b-%y')
           buy['dateClose'] = datetime.strftime(buy['dateClose'],'%d-%b-%y')
           orders.append(buy)
           avgDays.append(deltaDays)
    annualYield = (1+target)**(365/mean(avgDays)) - 1 
    orders = sorted(orders, key=lambda x: x['timestampOpen'])
    data = {
        "request": request,
        "orders": orders,
        "avgDays": mean(avgDays),
        "target": target,
        "annualYield": annualYield
    }
    return templates.TemplateResponse("rand.html", data)