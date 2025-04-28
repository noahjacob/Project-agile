import pytest
from weather_dashboard import get_weather, get_coordinates

def test_get_coordinates_valid_city():
    lat, lon, address = get_coordinates("New York")
    assert lat is not None
    assert lon is not None
    assert "New York" in address

def test_get_coordinates_invalid_city():
    lat, lon, address = get_coordinates("Th")
    assert lat is None
    assert lon is None
    assert address is None