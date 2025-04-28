import pytest
import pandas as pd
from weather_dashboard import get_weather, get_coordinates, load_favorites

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

def test_load_save_favorites(tmp_path):
    # Create dummy data
    df = pd.DataFrame([{"user": "test@example.com", "city": "TestCity"}])
    test_file = tmp_path / "favorites.csv"
    df.to_csv(test_file, index=False)

    # Replace file path temporarily
    global FAV_FILE
    FAV_FILE_ORIG = FAV_FILE
    FAV_FILE = str(test_file)

    loaded_df = load_favorites()
    assert not loaded_df.empty
    assert loaded_df.iloc[0]["city"] == "TestCity"

    # Reset
    FAV_FILE = FAV_FILE_ORIG