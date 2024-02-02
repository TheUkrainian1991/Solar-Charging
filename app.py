import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
import json
import os


st.markdown("# Battery Charge Predictor")
st.markdown("Find the solar energy forecast for your area\
             on [VisualCrossing](https://www.visualcrossing.com/weather/weather-data-services).\
             Making an account is free if the page is restricted.")
st.markdown("My prediction is based on a 10.12KWh battery and over a year of data entry.\
            The graph below indicates what the model is based on. My median daily usage is 21.6KWh")

df = pd.read_csv("solar_data.csv")
fig = px.scatter(df, x="solar_energy", y="charge_to", labels={
                     "solar_energy": "Solar Energy",
                     "charge_to": "Charge to (%)"
                 })

# Show the figure
st.plotly_chart(fig)

col1, col2 = st.columns(2)

with col1:
    with st.form("my_loc"):
        st.markdown("### My Area")
        st.markdown("Use this form only if you live in my area")
        date = st.date_input(label="Enter date for forecast")
        my_submit_date = st.form_submit_button("Calculate")
with col2:
    with st.form("their_loc"):
        st.markdown("### Your Area")
        st.markdown("Use this form by first finding your solar energy from [VisualCrossing](https://www.visualcrossing.com/weather/weather-data-services)")
        solar_energy = st.text_input(label="Enter solar energy if you know it")
        your_submit_date = st.form_submit_button("Calculate")

YOUR_API_KEY = os.environ['VISUALCROSSING']
LOCATION = os.environ['LOCATION']

if my_submit_date:
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{LOCATION}/{date}?key={YOUR_API_KEY}&include=days"
    # Fetch data from the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse JSON data into a dictionary
        data_dict = response.json()

        # Now 'data_dict' contains the data as a Python dictionary
        solar_energy = data_dict['days'][0]['solarenergy']
        st.markdown(f"Solar energy forecast for {date} is {solar_energy}")
        solar_energy = float(solar_energy)

    else:
        st.markdown(f"Failed to retrieve data. Status code: {response.status_code}")

if your_submit_date:
    solar_energy = float(solar_energy)

if isinstance(solar_energy, float):
    battery_charge = (-0.001359*((solar_energy)**4)) + (0.08954*((solar_energy)**3)) - (1.781*((solar_energy)**2))\
    + (6.279*((solar_energy)**1)) + 95.53

    if battery_charge > 100:
        battery_charge = 100
    elif battery_charge < 0:
        battery_charge = 0
    else:
        battery_charge = battery_charge

    battery_charge = round(battery_charge, 1)
    st.markdown(f"### Charge to {battery_charge}% tonight")
