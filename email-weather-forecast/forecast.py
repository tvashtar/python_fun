#! /home/pi/miniconda3/bin/python
# -*- coding: utf-8 -*-
"""
Created on Fri May  6 23:17:15 2016

@author: conor
"""

import requests
import datetime
import matplotlib.pyplot as plt
import pandas as pd

import smtplib
from os.path import basename
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

from email.utils import formatdate
from creds import cdict

plt.style.use('tableau10')

def get_raw_weather(lat='40.674766',lon='-73.978959'):
    data = requests.get("https://api.forecast.io/forecast/cdict['forecastio_api_key']/{},{}".format(lat,lon)).json()
    return data

def convert_time(x):
    return datetime.datetime.fromtimestamp(x)

def doi_func():
    ''' Day of Interest '''
    now = datetime.datetime.now()
    if now.hour < 20:
        return now.date().strftime('%Y-%m-%d')
    else:
        return (now.date() + datetime.timedelta(1)).strftime('%Y-%m-%d')

if __name__ == '__main__':
    data = get_raw_weather()
    hourly_df = pd.DataFrame.from_dict(data['hourly']['data'])
    hourly_df["time"] = hourly_df.time.apply(convert_time)
    hourly_df.set_index('time',inplace=True)
    hourly_df['expected_precip'] = hourly_df.precipIntensity*hourly_df.precipProbability

    daily_df = pd.DataFrame.from_dict(data['daily']['data'])
    timecols=['sunriseTime','sunsetTime','time','apparentTemperatureMinTime']
    for col in timecols:
        daily_df[col] = daily_df[col].apply(convert_time)
    daily_df.set_index('time',inplace=True)

    doi = doi_func()
    today_slice = hourly_df[doi+' 08:00:00':doi+' 22:00:00']
    sunrise = daily_df.ix[doi,'sunriseTime']
    sunset = daily_df.ix[doi,'sunsetTime']


    #Plotting
    filename = 'forecast.png'
    rain_color = 'royalblue'
    temp_color = 'seagreen'
    plain_color = 'slategrey'
    size = 24

    plt.close('all')
    fig,ax = plt.subplots()
    today_slice.apparentTemperature.plot(fig=fig, style=temp_color, label='°F', zorder=10)
    ax2 = today_slice.expected_precip.plot('area', secondary_y=True, zorder=1, style=rain_color, fig=fig, sharex=True, label='Rain')

    ax.axvline(sunrise,ls='-.',c='goldenrod')
    ax.axvline(sunset,ls='-.',c='goldenrod')
    ax.set_ylim([30, 100])
    ax.tick_params(axis='y', colors=temp_color,size=size)
    ax.set_ylabel('°F',rotation=0,labelpad=20,color=temp_color,size=size)

    ax2.set_ylim([0.0, 0.5])
    rain_ticks = [0.0,0.017,0.1,0.4]
    rain_ticknames = ['','Light','Medium','Heavy']
    ax2.yaxis.set_ticks(rain_ticks)
    ax2.yaxis.set_ticklabels(rain_ticknames, color = rain_color, size=size)

    ax.xaxis.set_ticklabels(['8am','10am','Noon','2pm','4pm','6pm','8pm','10pm'],minor=True, color=plain_color,size=size)
    ax.xaxis.set_ticklabels(['8am','10pm'], color=plain_color, size=size)
    ax.set_xlabel(doi)
    ax.annotate('Max: {:.0f}°F'.format(today_slice.apparentTemperature.max()),xy=(doi+' 09:00:00', 95), color=plain_color, size=size)
    ax.annotate('Min: {:.0f}°F'.format(today_slice.apparentTemperature.min()),xy=(doi+' 09:00:00', 90), color=plain_color, size=size)
    # To put the line graph on top
    ax.set_zorder(ax2.get_zorder()+1)
    ax.patch.set_visible(False)

    fig.savefig(filename)

    #Emailing
    coat = "No Coat" if today_slice.apparentTemperature.min() > 55 else "Yes Coat"
    umbrella = "No Umbrella" if today_slice.expected_precip.max() < 0.005 else "Yes Umbrella"
    subject = coat+", "+umbrella

    msg = MIMEMultipart(
        From="conorlaver@gmail.com",
        To="conorlaver@gmail.com",
        Date=formatdate(localtime=True),
        Subject=subject
        )
    msg['Subject'] = subject

    my_html = '''
    <img src="{}" />
    '''.format(filename)
    msg.attach(MIMEText(my_html,'html'))

    with open(filename, "rb") as fil:
        msg.attach(MIMEApplication(
            fil.read(),
            Content_Disposition='attachment; filename="{}"'.format(basename(filename)),
            Name=basename(filename)
        ))
    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(cdict["emailuser"], cdict["emailpass"])
    server.sendmail(cdict["emailuser"], 'conorlaver@gmail.com', msg.as_string())
    server.quit()
