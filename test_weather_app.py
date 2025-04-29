import pytest
from weather_dashboard import get_weather, get_coordinates, get_current_location, get_hourly_weather, get_sunrise_sunset, get_7_day_forecast

# Test 1: Valid city coordinates
def test_get_coordinates_valid_city():
    lat, lon, address = get_coordinates("New York")
    assert lat is not None
    assert lon is not None
    assert "New York" in address

# Test 2: Invalid city coordinates
def test_get_coordinates_invalid_city():
    lat, lon, address = get_coordinates("Th")
    assert lat is None
    assert lon is None
    assert address is None

# Test 3: Get current location
def test_get_current_location():
    city, lat, lon = get_current_location()
    assert isinstance(city, str)
    assert isinstance(lat, float)
    assert isinstance(lon, float)
    assert lat != 0.0 and lon != 0.0

# Test 4: Get weather for valid location
def test_get_weather_valid():
    city, lat, lon = get_current_location()
    weather = get_weather(lat, lon)
    assert weather is not None
    assert "current" in weather

# Test 5: Get hourly weather for valid location
def test_get_hourly_weather_valid():
    city, lat, lon = get_current_location()
    hourly = get_hourly_weather(lat, lon)
    assert hourly is not None
    assert "time" in hourly
    assert "temperature_2m" in hourly
    assert "relative_humidity_2m" in hourly

# Test 6: Get sunrise and sunset for valid location
def test_get_sunrise_sunset_valid():
    city, lat, lon = get_current_location()
    data = get_sunrise_sunset(lat, lon)
    assert data is not None
    assert "daily" in data
    assert "sunrise" in data["daily"]
    assert "sunset" in data["daily"]

# Test 7: Get 7-day forecast for valid location
def test_get_7_day_forecast_valid():
    city, lat, lon = get_current_location()
    forecast = get_7_day_forecast(lat, lon)
    if forecast is None:
        pytest.skip("API did not return forecast data, skipping test.")
    assert "daily" in forecast
    assert "temperature_2m_max" in forecast["daily"]
    assert "temperature_2m_min" in forecast["daily"]
