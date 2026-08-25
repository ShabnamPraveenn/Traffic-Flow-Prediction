# 🚦 Traffic Flow Prediction System

An end-to-end **Machine Learning-based Traffic Flow Prediction System** that predicts traffic volume using historical traffic and environmental data and provides location-based real-time traffic information through APIs.

The project combines **Machine Learning, API integration, geolocation, weather data, and interactive map visualization** into a Streamlit web application.

---

## 📌 Features

- 🤖 Traffic flow prediction using Machine Learning
- 🌲 Random Forest Regression
- ⚡ XGBoost Regression
- 📊 Model evaluation using R² Score and Mean Squared Error
- 📍 Location detection using city name
- 🌦️ Live weather data using OpenWeatherMap API
- 🚗 Real-time traffic information using TomTom Traffic API
- 🗺️ Interactive map visualization using Folium
- ⏰ Automatic extraction of time-based features
- 🖥️ Interactive Streamlit dashboard
- 🚦 Traffic classification into Low, Medium, and High levels

---

## 🧠 Machine Learning

The system was trained using historical traffic data containing traffic and environmental features.

### Features Used

- Temperature
- Rainfall
- Snowfall
- Cloud coverage
- Hour of the day
- Day of the week
- Month
- Weekend indicator
- Weather-related encoded features

### Models Evaluated

Two regression models were trained and compared:

| Model | R² Score | MSE |
|---|---:|---:|
| Random Forest | 0.946 | 212032 |
| XGBoost | 0.950 | 199628 |

### Final Model

**XGBoost** performed slightly better than Random Forest based on both:

- Higher R² Score
- Lower Mean Squared Error

Therefore, XGBoost was selected as the preferred model for the prediction system.

---

## 📊 Model Performance

### R² Score

The models achieved approximately:

- **Random Forest:** R² = 0.946
- **XGBoost:** R² = 0.950

An R² score close to 1 indicates that the model explains a large proportion of the variation in the target traffic volume within the evaluated dataset.

---

## 🌦️ Live Weather Integration

The application uses the **OpenWeatherMap API** to retrieve weather information based on the selected location.

The application retrieves:

- Temperature
- Rainfall in the last hour
- Snowfall in the last hour
- Cloud coverage
- Current weather condition

Weather information is incorporated into the prediction input where applicable.

---

## 🚗 Real-Time Traffic Integration

The application also integrates the **TomTom Traffic API** to obtain current traffic-flow information for the selected location.

The API provides:

- Current road speed
- Free-flow speed
- Confidence value

The application calculates a traffic-speed ratio:

```text
Traffic Ratio = Current Speed / Free Flow Speed
