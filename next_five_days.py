import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime as dt
import requests
import json
import os

with open('model_params.json', 'r') as file:
    model_params = json.load(file)

YOUR_API_KEY = os.environ['VISUALCROSSING']
LOCATION = os.environ['LOCATION']

@st.cache_data
def retrieve_data(date):
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{LOCATION}/{date}?key={YOUR_API_KEY}&include=days"
    # Fetch data from the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse JSON data into a dictionary
        data_dict = response.json()

        # Now 'data_dict' contains the data as a Python dictionary
        solar_energy = data_dict['days'][0]['solarenergy']
        solar_energy = float(solar_energy)
        return solar_energy

    else:
        st.markdown("## :red[problem with api call]")
        return 0

@st.cache_data
def calc_prediction(solar_energy, model_param_sub):
    # The following are weights from analysis in the notebook
    t = model_param_sub['t']
    std_error = model_param_sub['std_error']
    x_mean = model_param_sub['x_mean']
    n = model_param_sub['n']
    denominator = model_param_sub['denominator']

    # Calcs
    predict_interval = t * std_error * (1 + 1/n + (solar_energy - x_mean)**2 / denominator)**.5

    battery_charge = (model_param_sub['x4']*((solar_energy)**4)) + (model_param_sub['x3']*((solar_energy)**3))\
          + (model_param_sub['x2']*((solar_energy)**2))\
    + (model_param_sub['x']*((solar_energy)**1)) + model_param_sub['c']


    if battery_charge > 100:
        battery_bounded = 100
    elif battery_charge < 0:
        battery_bounded = 0
    else:
        battery_bounded = battery_charge

    battery_bounded = round(battery_charge, 1)
    low_95 = round(battery_charge - predict_interval, 1)
    high_95 = round(battery_charge + predict_interval, 1)
    return battery_bounded, low_95, high_95


def make_next_five_days_df():
    date_list = []
    solar_energy_list = []
    charge_to_list = []
    low_list = []
    high_list = []
    for num in range(5):
        date = dt.date.today() + dt.timedelta(days=num)
        solar_energy = retrieve_data(date)
        if date.month >= 10 or date.month <= 3:
            battery_bounded, low_95, high_95 = calc_prediction(solar_energy, model_params['GMT'])
        else:
            battery_bounded, low_95, high_95 = calc_prediction(solar_energy, model_params['DST'])

        date_list.append(date)
        solar_energy_list.append(solar_energy)
        charge_to_list.append(battery_bounded)
        low_list.append(low_95)
        high_list.append(high_95)

    days_and_perc_dict = {
        "date" : date_list,
        "solar_energy" : solar_energy_list,
        "charge_to" : charge_to_list,
        "95_low" : low_list,
        "95_high" : high_list
    }

    days_and_perc_df = pd.DataFrame(days_and_perc_dict)
    days_and_perc_df["95_low"] = days_and_perc_df["95_low"].astype(float)
    days_and_perc_df["95_high"] = days_and_perc_df["95_high"].astype(float)


    return days_and_perc_df
