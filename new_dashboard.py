import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px


# Function to get the user's current location based on IP
def get_current_location():
    ip_url = "https://ipinfo.io/json"
    response = requests.get(ip_url).json()
    city = response.get("city", "Hoboken")  # Default to "Hoboken" if city is not found
    loc = response.get("loc", "").split(",")  # Get latitude, longitude
    lat, lon = float(loc[0]), float(loc[1])
    return city, lat, lon


# Function to get the coordinates for a given city
def get_coordinates(city_name):
    url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
    headers = {"User-Agent": "WeatherDashboardApp/ (noahjacobkurian@gmail.com)"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        location_data = response.json()
        if location_data:

            # Ensure that the result is actually a city and not a region or street
            location = location_data[0]

            # Check if the type of location is a city or town
            if location['addresstype'] in ['city', 'town']:
                full_address = location['display_name']
                return float(location['lat']), float(location['lon']), full_address
            else:
                st.warning(f"City '{city_name}' not found. Please try a valid city.")
                return None, None, None
    else:
        st.error(f"API request failed with status code {response.status_code}: {response.text}")
        return None, None, None


# Function to get the current weather data for a given lat, lon
def get_weather(lat, lon, unit='fahrenheit'):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,apparent_temperature&wind_speed_unit=mph&temperature_unit={unit}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to retrieve current weather data.")
        return None


# Function to get the hourly weather data for a given lat, lon
def get_hourly_weather(lat, lon, unit='fahrenheit'):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m&temperature_unit={unit}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["hourly"]
    else:
        st.error("Failed to retrieve hourly forecast data.")
        return None


# Function to display current weather metrics
def display_current_weather(current, unit):
    unit = unit[0].upper()
    temp = f"{current['temperature_2m']}°{unit}"
    wind = f"{current['wind_speed_10m']} mph"
    humidity = f"{current['relative_humidity_2m']}%"
    feels_like = f"{current['apparent_temperature']}°{unit}"

    a, b = st.columns(2)
    c, d = st.columns(2)

    a.metric("Temperature", temp, border=True)
    b.metric("Wind", wind, border=True)
    c.metric("Humidity", humidity, border=True)
    d.metric("Feels Like", feels_like, border=True)


# Function to display hourly weather trends
def display_hourly_weather(hourly_weather, unit):
    # Convert data to DataFrame for visualization
    df = pd.DataFrame({
        "Time": pd.to_datetime(hourly_weather["time"]),  # Convert timestamps
        "Temperature": hourly_weather["temperature_2m"],
        "Humidity": hourly_weather["relative_humidity_2m"]
    })
    current_time = datetime.now()
    future_time = current_time + timedelta(hours=12)

    # Filter the DataFrame to only include data within the next 12 hours
    df = df[(df["Time"] >= current_time) & (df["Time"] <= future_time)]

    # Split 'Time' into 'Date' and 'Hour' for easier use in the tooltip
    df["Date"] = df["Time"].dt.strftime("%b %d, %Y")
    df["Hour"] = df["Time"].dt.strftime("%I:%M %p")  # Format as Hour:Minute

    # Plot the chart using Plotly
    fig = px.line(df, x="Time", y=["Temperature", "Humidity"], title="Hourly Temperature & Humidity Trend")

    # Update hovertemplate for Temperature
    unit = unit[0].upper()
    df["Unit"] = unit
    fig.update_traces(
        hovertemplate="Temperature: <b>%{y}°%{customdata[1]}</b><br>Date: %{customdata[0]}<br>",
        selector=dict(name="Temperature"),

        customdata=df[["Date", "Unit"]],

    )

    # Update hovertemplate for Humidity
    fig.update_traces(
        hovertemplate="Humidity: <b>%{y}%</b><br>Date: %{customdata[0]}<br>",
        selector=dict(name="Humidity"),
        customdata=df[["Date"]]
    )
    fig.update_layout(
        xaxis=dict(
            tickformat="%H:%M",
            title="Time"
        ),
        yaxis=dict(
            title="Weather Metrics"
        ),
        legend_title="Legend",
        hovermode="x"
    )

    st.plotly_chart(fig)


def get_5_day_forecast(lat, lon, unit='fahrenheit'):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max&temperature_unit={unit}&timezone=auto"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch forecast data.")
        return None


def display_5_day_forecast(forecast_data):
    # Extract necessary data
    days_data = []
    for i in range(len(forecast_data['daily']['temperature_2m_max'])):
        date = pd.to_datetime(forecast_data['daily']['time'][i]).strftime('%A, %b %d')
        weather_code = forecast_data['daily']['weathercode'][i]
        min_temp = forecast_data['daily']['temperature_2m_min'][i]
        max_temp = forecast_data['daily']['temperature_2m_max'][i]
        precip_prob = forecast_data['daily']['precipitation_sum'][i] * 100  # Convert precipitation sum to percentage

        days_data.append({
            'Date': date,
            'Weather Code': weather_code,
            'Min Temp (°C)': min_temp,
            'Max Temp (°C)': max_temp,
            'Precipitation (%)': precip_prob
        })


# Function to get sunrise and sunset times
def get_sunrise_sunset(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=sunrise,sunset&timezone=auto"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()  # Return the response in JSON format
    else:
        st.error("Failed to fetch sunrise and sunset data.")  # Error handling
        return None  # Return None in case of failure

# Function to display sunrise and sunset times with Streamlit components
def display_sunrise_sunset(sunrise_sunset_data):
    try:
        # Extract sunrise and sunset times from the API response
        sunrise_time = sunrise_sunset_data["daily"]["sunrise"][0]
        sunset_time = sunrise_sunset_data["daily"]["sunset"][0]

        # Convert the sunrise and sunset times to datetime objects
        sunrise_time_obj = datetime.fromisoformat(sunrise_time)
        sunset_time_obj = datetime.fromisoformat(sunset_time)

        # Format the times as strings for display
        sunrise_time_str = sunrise_time_obj.strftime('%I:%M %p')
        sunset_time_str = sunset_time_obj.strftime('%I:%M %p')

        # Define a consistent image size for both images
        image_size = (700, 400)  # You can adjust the size to fit your needs

        # Display sunrise and sunset cards side by side
        col1, col2 = st.columns(2)

        with col1:
            # Display Sunrise with st.image
            st.metric(f"**🌅 Sunrise:**", sunrise_time_str, border=True)

        with col2:
            # Display Sunset with st.image
            # st.image('https://i.imgur.com/RNgabm3.jpeg', use_container_width=True)
            st.metric(f"**🌇 Sunset:**", sunset_time_str, border=True)

    except KeyError as e:
        st.error(f"KeyError: Missing key {e}. Please check the structure of the API response.")
    except Exception as e:
        st.error(f"An error occurred: {e}")


# Main execution
def main():
    city_name, lat, lon = get_current_location()

    # Set page layout
    st.set_page_config(page_title="Weather Dashboard", layout="centered")

    # Page header
    st.markdown("<h1 style='text-align: center;'>Weather Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>{datetime.now().strftime('%A, %B %d, %Y')}</h4>", unsafe_allow_html=True)

    # Sidebar for city search and more features
    st.sidebar.header("🔍 Search City")
    city = st.sidebar.text_input("Enter city name", city_name)
    unit = st.sidebar.selectbox("Select Temperature Unit", ("Fahrenheit", "Celsius"))
    st.sidebar.markdown("---")
    st.sidebar.write("⚡ **Powered by Open-Meteo API**")

    # Fetch weather data for the current location
    unit = unit.lower()
    with st.spinner("Fetching weather data..."):
        weather_data = get_weather(lat, lon, unit)
        hourly_weather = get_hourly_weather(lat, lon, unit)

    if city:
        # Fetch coordinates for the entered city
        lat, lon, address = get_coordinates(city)

        if lat and lon and address:
            st.sidebar.success(f"📍 Selected: {address}")

            # Fetch weather data for the selected city
            weather_data = get_weather(lat, lon, unit)
            if weather_data:
                # Display current weather metrics
                display_current_weather(weather_data["current"], unit)

            hourly_weather = get_hourly_weather(lat, lon, unit)
            if hourly_weather:
                # Display hourly weather trends
                display_hourly_weather(hourly_weather, unit)

            # Fetch and display sunrise and sunset times
            sunrise_sunset_data = get_sunrise_sunset(lat, lon)
            if sunrise_sunset_data:
                display_sunrise_sunset(sunrise_sunset_data)

            # Example 5-day weather forecast data (this should come from another API or static data)
            forecast_data = {
                "Date": ['Monday, Apr 07', 'Tuesday, Apr 08', 'Wednesday, Apr 09', 'Thursday, Apr 10', 'Friday, Apr 11'],
                "Weather": ['Clear Sky', 'Partly Cloudy', 'Rainy', 'Sunny', 'Cloudy'],
                "Min Temp (°C)": [12, 15, 14, 16, 13],
                "Max Temp (°C)": [22, 25, 23, 28, 26],
                "Precipitation (%)": [0, 20, 80, 0, 30]
            }

            # Convert forecast data to DataFrame for visualization
            df = pd.DataFrame(forecast_data)

            # Display the 5-day weather forecast table
            st.markdown("### 5-Day Weather Forecast")
            st.dataframe(df)  # Display the DataFrame as a table
        else:
            st.warning("Invalid city or location not found. Please try again.")

    else:
        st.warning("City not entered. Default location weather data will be shown.")
        # If no city is entered, the default location will be used (from IP location)
        if weather_data:
            display_current_weather(weather_data["current"], unit)
        if hourly_weather:
            display_hourly_weather(hourly_weather, unit)

        # Fetch and display sunrise and sunset times for the default location
        sunrise_sunset_data = get_sunrise_sunset(lat, lon)
        if sunrise_sunset_data:
            display_sunrise_sunset(sunrise_sunset_data)



if __name__ == "__main__":
    main()

