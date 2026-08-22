import streamlit as st
import joblib
import pandas as pd
import requests
from geopy.geocoders import Nominatim
from datetime import datetime
import folium
from streamlit_folium import st_folium
import time

st.set_page_config(layout="wide")

# ---------------- SESSION STATE ----------------
if "prediction_done" not in st.session_state:
    st.session_state.prediction_done = False

if "map_obj" not in st.session_state:
    st.session_state.map_obj = None

# ---------------- LOAD MODEL ----------------
@st.cache_resource
def load_model():
    model = joblib.load("traffic_model.pkl")
    feature_columns = joblib.load("feature_columns.pkl")
    return model, feature_columns

model, feature_columns = load_model()

# ---------------- SAFE LOCATION FUNCTION (FIXED) ----------------
@st.cache_data
def get_location(city):
    geolocator = Nominatim(user_agent="traffic_app", timeout=10)

    for _ in range(3):  # retry 3 times
        try:
            location = geolocator.geocode(city)
            if location:
                return location.latitude, location.longitude
        except:
            time.sleep(2)

    return None, None   # fallback trigger

# ---------------- WEATHER ----------------
@st.cache_data(ttl=300)
def get_weather(lat, lon):
    try:
        api_key = "YOUR_OPENWEATHER_API_KEY"
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        data = requests.get(url, timeout=10).json()

        return (
            data['main']['temp'],
            data['clouds']['all'],
            data.get('rain', {}).get('1h', 0),
            data.get('snow', {}).get('1h', 0),
            data['weather'][0]['main']
        )
    except:
        return 20, 50, 0, 0, "Unknown"

# ---------------- TRAFFIC ----------------
@st.cache_data(ttl=120)
def get_traffic(lat, lon):
    try:
        api_key = "YOUR_TOMTOM_API_KEY"
        url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={lat},{lon}&key={api_key}"
        data = requests.get(url, timeout=10).json()

        flow = data.get("flowSegmentData", {})

        return (
            flow.get("currentSpeed", 0),
            flow.get("freeFlowSpeed", 1),
            flow.get("confidence", 0)
        )
    except:
        return None

# ---------------- UI ----------------
st.title("🚦 Traffic Flow Prediction System")

city = st.text_input("📍 Enter City Name")

if city:
    # 🔥 SAFE LOCATION CALL
    lat, lon = get_location(city)

    # 🔥 FALLBACK (NO ERROR EVER)
    if lat is None or lon is None:
        st.warning("⚠️ Location service failed, using default (Bhubaneswar)")
        lat, lon = 20.2961, 85.8245

    st.success(f"📍 Location: {city}")
    st.write(f"Latitude: {lat}, Longitude: {lon}")

    # ---------------- WEATHER ----------------
    temp, clouds, rain, snow, weather = get_weather(lat, lon)

    st.subheader("🌦 Weather")
    st.write(f"Temperature: {temp} °C")
    st.write(f"Clouds: {clouds}%")
    st.write(f"Weather: {weather}")

    # ---------------- TRAFFIC ----------------
    traffic_data = get_traffic(lat, lon)

    if traffic_data:
        current_speed, free_speed, _ = traffic_data

        ratio = current_speed / free_speed if free_speed != 0 else 0

        if ratio > 0.75:
            real_level, real_color = "Low", "green"
        elif ratio > 0.4:
            real_level, real_color = "Medium", "orange"
        else:
            real_level, real_color = "High", "red"

        st.subheader("🚗 Real Traffic")
        st.write(f"Traffic Level: {real_level}")
    else:
        real_level, real_color = None, None

    # ---------------- TIME ----------------
    now = datetime.now()

    input_dict = {
        "temp": temp,
        "rain_1h": rain,
        "snow_1h": snow,
        "clouds_all": clouds,
        "hour": now.hour,
        "day_of_week": now.weekday(),
        "month": now.month,
        "is_weekend": 1 if now.weekday() >= 5 else 0
    }

    input_df = pd.DataFrame([input_dict])

    for col in feature_columns:
        if col not in input_df.columns:
            input_df[col] = 0

    input_df = input_df[feature_columns]

    # ---------------- FORM ----------------
    with st.form("predict_form"):
        submit = st.form_submit_button("🚦 Predict Traffic")

        if submit:
            prediction = model.predict(input_df)[0]

            st.session_state.prediction_done = True
            st.session_state.prediction = prediction

            if prediction < 2000:
                st.session_state.level = "Low"
                st.session_state.color = "green"
            elif prediction < 4000:
                st.session_state.level = "Medium"
                st.session_state.color = "orange"
            else:
                st.session_state.level = "High"
                st.session_state.color = "red"

            # CREATE MAP ONCE
            m = folium.Map(location=[lat, lon], zoom_start=12)

            folium.Circle(
                [lat, lon],
                radius=700,
                color=st.session_state.color,
                fill=True,
                fill_opacity=0.4
            ).add_to(m)

            if real_level:
                folium.Circle(
                    [lat, lon],
                    radius=400,
                    color=real_color,
                    fill=True,
                    fill_opacity=0.7
                ).add_to(m)

            st.session_state.map_obj = m

    # ---------------- SHOW RESULT ----------------
    if st.session_state.prediction_done:
        st.success(f"🚗 Predicted Traffic: {int(st.session_state.prediction)} vehicles")
        st.write(f"Traffic Level: {st.session_state.level}")

        st_folium(
            st.session_state.map_obj,
            width=700,
            height=500,
            key="stable_map"
        )

# ---------------- RESET ----------------
if st.session_state.prediction_done:
    if st.button("🔄 Reset"):
        st.session_state.clear()