import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import json
import os


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
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,apparent_temperature,weather_code&wind_speed_unit=mph&temperature_unit={unit}"
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
def display_hourly_weather(hourly_weather, unit, hours):
    # Convert data to DataFrame for visualization
    df = pd.DataFrame({
        "Time": pd.to_datetime(hourly_weather["time"]),  # Convert timestamps
        "Temperature": hourly_weather["temperature_2m"],
        "Humidity": hourly_weather["relative_humidity_2m"]
    })
    current_time = datetime.now()
    future_time = current_time + timedelta(hours=hours)

    # Filter the DataFrame to only include data within the next 12 hours
    df = df[(df["Time"] >= current_time) & (df["Time"] <= future_time)]

    # Split 'Time' into 'Date' and 'Hour' for easier use in the tooltip
    df["Date"] = df["Time"].dt.strftime("%b %d, %Y")
    df["Hour"] = df["Time"].dt.strftime("%I:%M %p")  # Format as Hour:Minute

    # Plot the chart using Plotly
    fig = px.line(df, x="Time", y=["Temperature", "Humidity"], title="Hourly Temperature & Humidity Trend")

    # Update hover template for Temperature
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

def get_7_day_forecast(lat, lon, unit='metric'):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode&temperature_unit={unit}&timezone=auto"
    response = requests.get(url)


    if response.status_code == 200:
        return response.json()

    else:
        st.error("Failed to fetch forecast data.")
        return None

def display_7_day_forecast(lat, lon, unit):
    forecast_data = get_7_day_forecast(lat, lon, unit)
    daily_data = forecast_data["daily"]


    df = pd.DataFrame({
            "Date": pd.to_datetime(daily_data["time"]).strftime('%A, %b %d'),
            "Max Temp": daily_data["temperature_2m_max"],
            "Min Temp ": daily_data["temperature_2m_min"],
            "Precipitation Probability (%)": daily_data["precipitation_probability_max"],
            "Weather Code": daily_data["weathercode"]
    })


    weather_code_mapping = {
                0: "Clear sky ☀️",
                1: "Mainly clear 🌤️",
                2: "Partly cloudy ⛅",
                3: "Overcast ☁️",
                45: "Fog 🌫️",
                48: "Depositing rime fog 🌫️",
                51: "Light drizzle 🌦️",
                53: "Moderate drizzle 🌧️",
                55: "Dense drizzle 🌧️",
                61: "Slight rain 🌦️",
                63: "Moderate rain 🌧️",
                65: "Heavy rain 🌧️",
                71: "Slight snow fall ❄️",
                73: "Moderate snow fall ❄️",
                75: "Heavy snow fall ❄️",
                80: "Slight rain showers 🌦️",
                81: "Moderate rain showers 🌧️",
                82: "Violent rain showers ⛈️",
                95: "Thunderstorm ⛈️",
                96: "Thunderstorm with slight hail ⛈️",
                99: "Thunderstorm with heavy hail ⛈️"
            }

    # Replacing 'Weather Code' numbers with text and Icons
    df["Weather"] = df["Weather Code"].map(weather_code_mapping)
    df = df.drop(columns=["Weather Code"])

    st.markdown("### 7-Day Weather Forecast")
    df.index= df.index+1
    st.dataframe(df)

# Function to get sunrise and sunset times
def get_sunrise_sunset(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=sunrise,sunset&timezone=auto"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()  # Return the response in JSON format
    else:
        st.error("Failed to fetch sunrise and sunset data.")  # Error handling
        return None


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

def user_login():
    st.sidebar.markdown("### 🙋 User Login")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_email = ""

    # Check query params on load
    params = st.query_params
    if not st.session_state.logged_in and "email" in params:
        st.session_state.user_email = params["email"]
        st.session_state.logged_in = True

    if not st.session_state.logged_in:
        user_email_input = st.sidebar.text_input("Enter your email to login", key="email_input")
        if st.sidebar.button("Login"):
            if user_email_input:
                st.session_state.logged_in = True
                st.session_state.user_email = user_email_input
                st.query_params["email"] = user_email_input  # Save in URL
                st.sidebar.success(f"Logged in as {user_email_input}")
                st.rerun()
            else:
                st.sidebar.error("Please enter a valid email.")
    else:
        st.sidebar.success(f"Welcome, {st.session_state.user_email}")
        if st.sidebar.button("Logout"):
            st.session_state.clear() # Clear all session state variables on logout
            st.query_params.clear()  # Clear from URL
            st.rerun()

    return st.session_state.logged_in, st.session_state.user_email


FAV_FILE = "favorites.csv"

# Load favorites from CSV
def load_favorites():
    if os.path.exists(FAV_FILE):
        return pd.read_csv(FAV_FILE)
    else:
        return pd.DataFrame(columns=["user", "city"])

# Save favorites to CSV
def save_favorites(fav_df):
    fav_df.to_csv(FAV_FILE, index=False)


def manage_favorites(city, user):
    """
    Displays favorite city management section inside the sidebar.
    Returns the updated city based on user selection.
    """

     # Load favorites from file into session_state if missing
    if "favorites_df" not in st.session_state:
        st.session_state["favorites_df"] = load_favorites()

    df = st.session_state["favorites_df"]
    user_favorites = df[df["user"] == user]

    # Add to Favorites button
    if st.sidebar.button("⭐ Add to Favorites"):
        if city:
            if city not in user_favorites["city"].values:
                if len(user_favorites) < 5:
                    new_entry = pd.DataFrame([{"user": user, "city": city}])
                    df = pd.concat([df, new_entry], ignore_index=True)
                    save_favorites(df)
                    st.session_state["favorites_df"] = df  # Update session_state
                    st.success(f"'{city}' added to favorites!")
                else:
                    st.error("❌ You can only save 5 favorite cities!")
            else:
                st.warning("⚠️ City already in favorites!")

    # Reload user_favorites after possible add/remove
    df = load_favorites()
    st.session_state["favorites_df"] = df
    user_favorites = df[df["user"] == user]

    # Show Favorites and actions
    if not user_favorites.empty:
        fav_city = st.sidebar.selectbox("⭐ Choose Favorite", user_favorites["city"].tolist())

        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.sidebar.button("🔄 Load Favorite"):
                city = fav_city
                st.success(f"Loaded favorite: {fav_city}")
        with col2:
            if st.sidebar.button("🗑️ Remove Favorite"):
                df = df[~((df["user"] == user) & (df["city"] == fav_city))]
                save_favorites(df)
                st.session_state["favorites_df"] = df
                st.success(f"Removed favorite: {fav_city}")
                st.rerun()
                

    return city

SETTINGS_FILE = "settings.csv"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        return pd.read_csv(SETTINGS_FILE)
    else:
        return pd.DataFrame(columns=["user", "unit"])

def save_settings(settings_df):
    settings_df.to_csv(SETTINGS_FILE, index=False)


# Main execution
def main():
    city_name, lat, lon = get_current_location()

    # Set page layout
    st.set_page_config(page_title="Weather Dashboard", layout="centered")

    # Page header
    st.markdown("<h1 style='text-align: center;'>Weather Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>{datetime.now().strftime('%A, %B %d, %Y')}</h4>", unsafe_allow_html=True)

    # Sidebar for city search and more features.
    params = st.query_params
    if "email" in params:
        st.session_state.user_email = params["email"]
        st.session_state.logged_in = True

    logged_in, user_email = user_login()

    # You can now use `logged_in` and `user_email` throughout your app
    if logged_in:
        settings_df = load_settings()
        user_settings = settings_df[settings_df["user"] == user_email]

        if "unit" not in st.session_state:
            if not user_settings.empty:
                st.session_state.unit = user_settings["unit"].iloc[0]
            else:
                st.session_state.unit = "fahrenheit"  # Default
        
    
        st.sidebar.header("🔍 Search City")
        city = st.sidebar.text_input("Enter city name", city_name)
        unit = st.sidebar.selectbox("Select Temperature Unit", ("Fahrenheit", "Celsius"),
                            index=0 if st.session_state.unit == "fahrenheit" else 1)
        st.session_state.unit = unit

        # Save or update unit preference for the user
        if not user_settings.empty:
            if user_settings["unit"].iloc[0] != st.session_state.unit:
                settings_df.loc[settings_df["user"] == user_email, "unit"] = st.session_state.unit
                save_settings(settings_df)
        else:
            new_setting = pd.DataFrame([{"user": user_email, "unit": st.session_state.unit}])
            settings_df = pd.concat([settings_df, new_setting], ignore_index=True)
            save_settings(settings_df)

        # Forecast graph range slider.
        options = [12, 24, 36, 48]
        labels = ["12 Hours", "24 Hours", "36 Hours", "48 Hours"]

        selected_label = st.sidebar.select_slider(
            "Forecast Range:",
            options=labels,
            value=labels[0]
        )

        # Map label back to value
        value_map = dict(zip(labels, options))
        selected_value = value_map[selected_label]

        city = manage_favorites(city, user_email)

        st.sidebar.markdown("---")
        st.sidebar.write("⚡ **Powered by Open-Meteo API**")

        # Fetch weather data for current location
        unit = unit.lower()
        with st.spinner("Fetching weather data..."):
            weather_data = get_weather(lat, lon, unit)
            hourly_weather = get_hourly_weather(lat, lon, unit)

        if city:
            lat, lon, address = get_coordinates(city)

            if lat and lon and address:

                st.sidebar.success(f"📍 Selected: {address}")

                weather_data = get_weather(lat, lon, unit)
                if weather_data:
                    # Display current weather metrics
                    display_current_weather(weather_data["current"], unit)

                hourly_weather = get_hourly_weather(lat, lon, unit)
                if hourly_weather:
                    # Display hourly weather trends
                    display_hourly_weather(hourly_weather, unit, selected_value)

                # Fetch and display sunrise and sunset times
                sunrise_sunset_data = get_sunrise_sunset(lat, lon)
                if sunrise_sunset_data:
                    display_sunrise_sunset(sunrise_sunset_data)

                display_7_day_forecast(lat, lon, unit)

                # After fetching weather data
                current_weather_code = weather_data["current"]["weather_code"]

    # Proceed with weather data, user-specific features, etc.
    else:
        st.info("Please log in to view weather data.")


if __name__ == "__main__":
    main()

