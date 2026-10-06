# Weather App with Live OpenWeather API

A Python capstone project that connects to a real-world cloud API
(OpenWeather) to show live city weather and a 5-day forecast, in either a
command-line interface or a Tkinter window.

## Features
- REST API integration using the `requests` library
- JSON response parsing (current weather + 3-hourly forecast grouped into daily summaries)
- Clean CLI output and a Tkinter GUI (`--gui`)
- Celsius / Fahrenheit support
- Friendly error handling (wrong city, bad API key, no internet, timeout, rate limit)
- API key stored in a `.env` file, not in the code
- Unit tests with mocked API responses

## Project structure
```
weather-app/
├── main.py              # entry point (CLI + --gui switch)
├── weather_api.py       # API calls, JSON parsing, error handling
├── gui.py               # Tkinter interface
├── tests/
│   └── test_weather_api.py
├── requirements.txt
├── .env.example         # template for your API key
├── .gitignore
└── README.md
```

## Setup
1. Get a free API key at https://openweathermap.org/api (sign up, then API keys tab).
   New keys can take up to 2 hours to activate.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and paste your key:
   ```
   OPENWEATHER_API_KEY=your_real_key
   ```

## Run
```
python main.py                       # interactive CLI
python main.py Hyderabad             # single lookup
python main.py London --units imperial
python main.py --gui                 # Tkinter window
```

## Run tests
```
python -m unittest discover tests
```
