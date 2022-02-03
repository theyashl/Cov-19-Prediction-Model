import json
import csv
from web import static
from django.shortcuts import render
import pandas as pd
import numpy as np

from django.http import JsonResponse


# Create your views here.
def d_es(data, days=2, alp=0.4, bet=0.4):
    d = np.array(data)
    cols = len(d)

    d = np.append(d, [np.nan] * days)
    f = np.full(cols + days, np.nan)

    f[1] = d[0]

    level = d[0]
    trend = d[1] - d[0]

    for t in range(2, cols + 1):
        cur_level = alp * d[t - 1] + (1 - alp) * f[t - 1]
        trend = bet * (cur_level - level) + (1 - bet) * trend
        level = cur_level
        f[t] = level + trend

    # f[cols+1:] = f[t]
    for t in range(cols + 1, len(f)):
        cur_level = f[t - 1]
        trend = bet * (cur_level - level) + (1 - bet) * trend
        level = cur_level
        f[t] = level + trend

    df = pd.DataFrame.from_dict({"Data": d, "Forecast": f, "Error": d - f})
    df.index.name = "Days"
    # df[["Data", "Forecast"]].plot(figsize=(8, 3), title="Double Smoothing", style=["-", "--"])
    return f


def home(request):
    confirmed_csv = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
    deaths_csv = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
    recovered_csv = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
    # confirmed_csv = pd.read_csv("C:\\Users\\YASH\\Downloads\\time_series_covid19_confirmed_global.csv")
    # deaths_csv = pd.read_csv("C:\\Users\\YASH\\Downloads\\time_series_covid19_deaths_global.csv")
    # recovered_csv = pd.read_csv("C:\\Users\\YASH\\Downloads\\time_series_covid19_recovered_global.csv")
    # print(data.head())
    # print(data.describe())
    ind = confirmed_csv[confirmed_csv['Country/Region'] == "India"]
    indd = list(deaths_csv[deaths_csv['Country/Region'] == "India"].values)[0][4:]
    indr = list(recovered_csv[recovered_csv['Country/Region'] == "India"].values)[0][4:]
    death_x = ""
    death_y = ""
    recovered_x = ""
    recovered_y = ""
    print(ind.head())
    dx = ""
    dy = ""
    x = ind.columns[4:].tolist()
    val = list(ind.values)[0][4:]
    dpd = rpd = expd = [["", "Date", "Value"]]
    data = []
    y = []
    for i in range(len(x)):
        expd.append([i, x[i], val[i]])
        dx += str(x[i]) + ' '
        dy += str(val[i]) + ' '
        death_x += str(indd[i]) + ' '
        dpd.append([i, indd[i], val[i]])
        recovered_x += str(indr[i]) + ' '
        y.append(val[i])
        data.append({"Date": x[i], "Value": val[i]})

    me_data = {
        'Date': dx.strip().split(' '),
        'Value': dy.strip().split((' '))
    }
    df = pd.DataFrame(me_data)
    print(df.head())
    df.to_csv('web/static/csv/cdata.csv')

    # Predictions
    pred = ""
    predl = d_es(val, days=10, alp=0.4, bet=0.4)
    predd = d_es(indd, days=10, alp=0.4, bet=0.4)
    predr = d_es(indr, days=10, alp=0.4, bet=0.4)
    for p in predl:
        pred += str(p) + ' '
    for d in predd:
        death_y += str(d) + ' '
    for r in predr:
        recovered_y += str(r) + ' '
    return render(request, 'web/index.html', {'x': dx.strip(), 'val': dy.strip(), 'leng': len(x), 'preds': pred.strip(), 'death_x': death_x, 'death_y': death_y, 'recovered_x': recovered_x, 'recovered_y': recovered_y})
    # return JsonResponse(list(data), safe=False)
