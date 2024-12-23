# tests/test_unit.py
import pytest
from app import get_coordinates, get_weather_data

def test_get_coordinates_valid():
    lat, lon = get_coordinates("Chicago", "Illinois", "USA")
    assert lat is not None and lon is not None

def test_get_coordinates_invalid():
    lat, lon = get_coordinates("FakeCity", "FakeState", "FakeCountry")
    assert lat is None and lon is None

def test_get_weather_data_valid():
    weather = get_weather_data("Chicago", "Illinois", "USA")
    assert weather is not None
    assert 'current_temp' in weather
    assert 'daily' in weather

def test_get_weather_data_invalid():
    weather = get_weather_data("FakeCity", "FakeState", "FakeCountry")
    assert weather is None
