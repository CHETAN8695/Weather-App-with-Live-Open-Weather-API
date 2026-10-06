"""Tkinter user interface for the Weather App."""

import queue
import threading
import tkinter as tk
from tkinter import ttk

import weather_api as api


class WeatherApp:
    def __init__(self, root, units="metric"):
        self.root = root
        self.root.title("Weather App")
        self.root.geometry("520x560")
        self.root.minsize(520, 560)

        self.city_var = tk.StringVar()
        self.units_var = tk.StringVar(value=units)
        self.status_var = tk.StringVar(value="Enter a city and press Search.")
        self.title_var = tk.StringVar()
        self.temp_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        self.details_var = tk.StringVar()

        # Results from the background thread arrive through this queue
        self.results = queue.Queue()

        self._build_ui()
        self.root.after(100, self._poll_results)

    # ---------- UI layout ----------
    def _build_ui(self):
        pad = {"padx": 12, "pady": 6}

        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill="x", **pad)

        entry = ttk.Entry(search_frame, textvariable=self.city_var, font=("Segoe UI", 12))
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        entry.bind("<Return>", lambda event: self.search())
        entry.focus()

        self.search_btn = ttk.Button(search_frame, text="Search", command=self.search)
        self.search_btn.pack(side="left")

        units_frame = ttk.Frame(self.root)
        units_frame.pack(fill="x", **pad)
        ttk.Radiobutton(units_frame, text="Celsius (°C)", value="metric",
                        variable=self.units_var).pack(side="left", padx=(0, 12))
        ttk.Radiobutton(units_frame, text="Fahrenheit (°F)", value="imperial",
                        variable=self.units_var).pack(side="left")

        ttk.Label(self.root, textvariable=self.status_var,
                  foreground="#555555").pack(fill="x", **pad)

        current = ttk.LabelFrame(self.root, text="Current Weather")
        current.pack(fill="x", **pad)
        ttk.Label(current, textvariable=self.title_var,
                  font=("Segoe UI", 15, "bold")).pack(pady=(8, 0))
        ttk.Label(current, textvariable=self.temp_var,
                  font=("Segoe UI", 28, "bold")).pack()
        ttk.Label(current, textvariable=self.desc_var,
                  font=("Segoe UI", 12)).pack()
        ttk.Label(current, textvariable=self.details_var,
                  font=("Segoe UI", 10)).pack(pady=(4, 10))

        forecast = ttk.LabelFrame(self.root, text="5-Day Forecast")
        forecast.pack(fill="both", expand=True, **pad)

        columns = ("date", "min", "max", "humidity", "condition")
        self.table = ttk.Treeview(forecast, columns=columns, show="headings", height=5)
        headings = {"date": "Date", "min": "Min", "max": "Max",
                    "humidity": "Humidity", "condition": "Condition"}
        widths = {"date": 90, "min": 60, "max": 60, "humidity": 70, "condition": 170}
        for col in columns:
            self.table.heading(col, text=headings[col])
            self.table.column(col, width=widths[col], anchor="center")
        self.table.pack(fill="both", expand=True, padx=6, pady=6)

    # ---------- Actions ----------
    def search(self):
        city = self.city_var.get().strip()
        if not city:
            self.status_var.set("Please enter a city name.")
            return

        self.search_btn.config(state="disabled")
        self.status_var.set(f"Fetching weather for {city}...")

        # The network call runs in a thread so the window never freezes
        threading.Thread(
            target=self._fetch, args=(city, self.units_var.get()), daemon=True
        ).start()

    def _fetch(self, city, units):
        """Runs in a background thread. Never touches the UI directly."""
        try:
            current = api.get_current_weather(city, units)
            forecast = api.get_forecast(city, units)
            self.results.put(("ok", current, forecast, units))
        except api.WeatherError as error:
            self.results.put(("error", str(error)))
        except Exception as error:  # last-resort safety net
            self.results.put(("error", f"Unexpected error: {error}"))

    def _poll_results(self):
        """Runs on the main thread every 100 ms and updates the UI."""
        try:
            item = self.results.get_nowait()
        except queue.Empty:
            pass
        else:
            self.search_btn.config(state="normal")
            if item[0] == "ok":
                _, current, forecast, units = item
                self._show_weather(current, forecast, units)
            else:
                self.status_var.set(f"⚠ {item[1]}")
        self.root.after(100, self._poll_results)

    def _show_weather(self, current, forecast, units):
        temp_sym, speed_unit = api.units_symbols(units)
        self.status_var.set("Updated successfully.")
        self.title_var.set(f"{current['city']}, {current['country']}")
        self.temp_var.set(f"{current['temp']:.1f}{temp_sym}")
        self.desc_var.set(current["description"])
        self.details_var.set(
            f"Feels like {current['feels_like']:.1f}{temp_sym}  |  "
            f"Humidity {current['humidity']}%  |  "
            f"Wind {current['wind_speed']} {speed_unit}"
        )

        self.table.delete(*self.table.get_children())
        for day in forecast:
            self.table.insert("", "end", values=(
                day["date"],
                f"{day['temp_min']:.1f}{temp_sym}",
                f"{day['temp_max']:.1f}{temp_sym}",
                f"{day['humidity']}%",
                day["description"],
            ))


def run_gui(units="metric"):
    root = tk.Tk()
    WeatherApp(root, units)
    root.mainloop()
