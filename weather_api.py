"""OpenWeather API client.

Handles the REST calls, JSON parsing and error handling so that the CLI and
the Tkinter GUI can both reuse the same code.
"""

import os
from collections import Counter, defaultdict
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()  # reads OPENWEATHER_API_KEY from the .env file

BASE_URL = "https://api.openweathermap.org/data/2.5"
TIMEOUT_SECONDS = 10


class WeatherError(Exception):
    """Any problem getting weather data. The message is safe to show to users."""


def units_symbols(units):
    """Return (temperature symbol, wind speed unit) for the chosen unit system."""
    if units == "imperial":
        return "°F", "mph"
    return "°C", "m/s"


def _get_api_key():
    key = os.getenv("OPENWEATHER_API_KEY")
    if not key:
        raise WeatherError(
            "API key not found. Add OPENWEATHER_API_KEY=your_key to a .env file."
        )
    return key


def _request(endpoint, city, units):
    """Send a GET request to OpenWeather and return the parsed JSON."""
    params = {"q": city, "appid": _get_api_key(), "units": units}

    try:
        response = requests.get(
            f"{BASE_URL}/{endpoint}", params=params, timeout=TIMEOUT_SECONDS
        )
    except requests.exceptions.ConnectionError as exc:
        raise WeatherError("No internet connection. Please check your network.") from exc
    except requests.exceptions.Timeout as exc:
        raise WeatherError("The request timed out. Please try again.") from exc
    except requests.exceptions.RequestException as exc:
        raise WeatherError(f"Network error: {exc}") from exc

    if response.status_code == 401:
        raise WeatherError(
            "Invalid API key. (New keys can take up to 2 hours to activate.)"
        )
    if response.status_code == 404:
        raise WeatherError(f"City '{city}' not found. Check the spelling.")
    if response.status_code == 429:
        raise WeatherError("Too many requests. Please wait a minute and retry.")
    if not response.ok:
        raise WeatherError(f"API error (HTTP {response.status_code}).")

    try:
        return response.json()
    except ValueError as exc:
        raise WeatherError("The API returned an invalid response.") from exc


def get_current_weather(city, units="metric"):
    """Return the current weather for a city as a simple dictionary."""
    data = _request("weather", city, units)
    try:
        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"].title(),
        }
    except (KeyError, IndexError, TypeError) as exc:
        raise WeatherError("Unexpected data format received from the API.") from exc


def get_forecast(city, units="metric", days=5):
    """Return a daily forecast (list of dicts).

    OpenWeather's free plan gives a forecast every 3 hours for 5 days, so we
    group those entries by date and compute min/max temperature, average
    humidity and the most common weather description for each day.
    """
    data = _request("forecast", city, units)

    by_day = defaultdict(lambda: {"temps": [], "humidity": [], "desc": []})
    try:
        for entry in data["list"]:
            day = entry["dt_txt"][:10]  # "2026-10-07 12:00:00" -> "2026-10-07"
            by_day[day]["temps"].append(entry["main"]["temp"])
            by_day[day]["humidity"].append(entry["main"]["humidity"])
            by_day[day]["desc"].append(entry["weather"][0]["description"])
    except (KeyError, IndexError, TypeError) as exc:
        raise WeatherError("Unexpected data format received from the API.") from exc

    forecast = []
    for day in sorted(by_day)[:days]:
        info = by_day[day]
        label = datetime.strptime(day, "%Y-%m-%d").strftime("%a, %d %b")
        forecast.append(
            {
                "date": label,
                "temp_min": min(info["temps"]),
                "temp_max": max(info["temps"]),
                "humidity": round(sum(info["humidity"]) / len(info["humidity"])),
                "description": Counter(info["desc"]).most_common(1)[0][0].title(),
            }
        )
    return forecast
