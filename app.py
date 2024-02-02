import streamlit as st

st.markdown("# Battery Charge Predictor")

with st.form("solar_energy"):
    solar_energy = st.text_input(label="Enter solar energy")
    submit = st.form_submit_button("Calculate")

if submit:
    solar_energy = int(solar_energy)
    battery_charge = (-0.001359*solar_energy) + 0.08954*((solar_energy)**4) - 1.781*((solar_energy)**3)\
    + 6.279*((solar_energy)**2) + 95.53
    battery_charge = round(battery_charge, 1)
    st.markdown(f"### Charge to {battery_charge}% tonight")