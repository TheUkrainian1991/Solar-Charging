import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt
import requests
import os
from next_five_days import make_next_five_days_df


st.markdown("# Battery Charge Predictor")
st.markdown("Find the solar energy forecast for your area\
             on [VisualCrossing](https://www.visualcrossing.com/weather/weather-data-services).\
             Making an account is free if the page is restricted.")
st.markdown("My prediction is based on a 10.12KWh battery and over a year of data entry.\
            The graph below indicates what the model is based on. My median daily usage is 21.6KWh")

# All Data Graph
df = pd.read_csv("solar_data.csv")
fig = px.scatter(df, x="solar_energy", y="charge_to", labels={
                     "solar_energy": "Solar Energy",
                     "charge_to": "Charge to (%)"
                 })

st.plotly_chart(fig)

# Prediction Graph
st.markdown("## Next Five Days")
next_five_days = make_next_five_days_df()
fig = px.line(next_five_days, x="date", y=next_five_days.columns, labels={
                     "date": "Date",
                     "value": "Charge to (%) / Solar Energy"
                 })
st.plotly_chart(fig)
st.markdown(f"### Charge to :green[{next_five_days.iloc[1,2]}%] tonight | 95% prediction range: ({next_five_days.iloc[1,3]}-{next_five_days.iloc[1,4]}%)")


col1, col2 = st.columns(2)

with col1:
    with st.form("my_loc"):
        st.markdown("### My Area")
        st.markdown("Use this form only if you live in my area")
        date = st.date_input(label="Enter date for forecast", value=dt.date.today() + dt.timedelta(days=1))
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

    # The following are weights from analysis in the notebook
    t = 1.964887640611612
    std_error = 12.260422682230273
    x_mean = 7.664998453608248
    n = 485
    denominator = 20735.016186046512

    # Calcs
    predict_interval = t * std_error * (1 + 1/n + (solar_energy - x_mean)**2 / denominator)**.5

    battery_charge = (-0.001359*((solar_energy)**4)) + (0.08954*((solar_energy)**3)) - (1.781*((solar_energy)**2))\
    + (6.279*((solar_energy)**1)) + 95.53


    if battery_charge > 100:
        battery_bounded = 100
    elif battery_charge < 0:
        battery_bounded = 0
    else:
        battery_bounded = battery_charge

    battery_bounded = round(battery_charge, 1)
    low_95 = int(battery_charge - predict_interval)
    high_95 = int(battery_charge + predict_interval)
    st.markdown(f"### Charge to :green[{battery_bounded}%] tonight | 95% prediction range: ({low_95}-{high_95}%)")
