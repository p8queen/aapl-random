from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import random as rn
from statistics import mean
import pandas as pd
from datetime import date, timedelta, datetime
import requests

app = FastAPI()

@app.get("/")
async def root():
  return {"message": "Hello World"}