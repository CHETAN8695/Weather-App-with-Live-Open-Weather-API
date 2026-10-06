"""Weather App - entry point.

Usage:
    python main.py                      # interactive CLI
    python main.py Hyderabad            # one-off lookup
    python main.py London --units imperial
    python main.py --gui                # Tkinter window
"""

import argparse

import weather_api as api


def print_report(current, forecast, units):
    """Display the weather in a clean, readable format in the terminal."""
    temp_sym, speed_unit = api.units_symbols(units)
    title = f"Weather in {current['city']}, {current['country']}"

    print()
    print("=" * 50)
    print(f" {title}")
    print("=" * 50)
    print(f" Condition   : {current['description']}")
    print(f" Temperature : {current['temp']:.1f}{temp_sym} "
          f"(feels like {current['feels_like']:.1f}{temp_sym})")
    print(f" Humidity    : {current['humidity']}%")
    print(f" Pressure    : {current['pressure']} hPa")
    print(f" Wind        : {current['wind_speed']} {speed_unit}")

    print()
    print(" 5-Day Forecast")
    print(" " + "-" * 48)
    print(f" {'Date':<12}{'Min':>8}{'Max':>8}{'Humid.':>8}  Condition")
    for day in forecast:
        print(
            f" {day['date']:<12}"
            f"{day['temp_min']:>7.1f}°"
            f"{day['temp_max']:>7.1f}°"
            f"{day['humidity']:>7}%"
            f"  {day['description']}"
        )
    print()


def show_weather(city, units):
    """Fetch and print the weather. Errors are shown as friendly messages."""
    try:
        current = api.get_current_weather(city, units)
        forecast = api.get_forecast(city, units)
    except api.WeatherError as error:
        print(f"\n[!] {error}\n")
        return
    print_report(current, forecast, units)


def interactive_loop(units):
    """Keep asking for cities until the user types 'q'."""
    print("Weather App (type 'q' to quit)")
    while True:
        city = input("Enter city name: ").strip()
        if city.lower() in ("q", "quit", "exit"):
            print("Goodbye!")
            break
        if not city:
            print("Please enter a city name.")
            continue
        show_weather(city, units)


def main():
    parser = argparse.ArgumentParser(description="Live weather using the OpenWeather API")
    parser.add_argument("city", nargs="*", help="City name (e.g. Hyderabad)")
    parser.add_argument(
        "--units",
        choices=["metric", "imperial"],
        default="metric",
        help="metric = °C, imperial = °F (default: metric)",
    )
    parser.add_argument("--gui", action="store_true", help="Open the Tkinter window")
    args = parser.parse_args()

    if args.gui:
        from gui import run_gui  # imported here so the CLI works without Tkinter

        run_gui(args.units)
    elif args.city:
        show_weather(" ".join(args.city), args.units)
    else:
        interactive_loop(args.units)


if __name__ == "__main__":
    main()
