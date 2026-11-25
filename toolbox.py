"""Toolbox: three small functions your agent's tools will call.

    get_weather(city)          -> live weather for a city, now and for the next 7 days
    get_my_trips()             -> your upcoming trips, from a pretend calendar
    add_reminder(text, date)   -> saves a reminder for a day

get_weather is real: it asks Open-Meteo, a free weather service that needs no key and
no sign-up. The trips and reminders are pretend: they live in this file and start
fresh every time you run your program, so you can't break anything.

Each function returns a dict. When something is wrong (a place that doesn't exist, a
date in the past) it raises an error with a message that says why.
"""

import datetime
import json
from urllib.parse import urlencode
from urllib.request import urlopen

TODAY = datetime.date.today()


def _days_from_today(n):
    return (TODAY + datetime.timedelta(days=n)).isoformat()


# Your pretend calendar. The dates move with today, so the trips are always coming up.
TRIPS = [
    {"city": "Chicago", "leaves": _days_from_today(2), "returns": _days_from_today(4), "why": "Work conference"},
    {"city": "Hyderabad", "leaves": _days_from_today(6), "returns": _days_from_today(20), "why": "Family visit"},
]

REMINDERS = []

# Open-Meteo describes the sky with a number. These are the plain words for them.
SKY = {
    0: "Clear", 1: "Mostly clear", 2: "Partly cloudy", 3: "Cloudy", 45: "Fog", 48: "Fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle", 61: "Light rain", 63: "Rain",
    65: "Heavy rain", 66: "Freezing rain", 67: "Freezing rain", 71: "Light snow", 73: "Snow",
    75: "Heavy snow", 77: "Snow", 80: "Showers", 81: "Showers", 82: "Heavy showers",
    85: "Snow showers", 86: "Snow showers", 95: "Thunderstorm", 96: "Thunderstorm", 99: "Thunderstorm",
}


def _fetch(url, params):
    """Call a web address and return its JSON answer as a dict."""
    try:
        with urlopen(url + "?" + urlencode(params), timeout=10) as response:
            return json.load(response)
    except OSError as e:
        raise ConnectionError(f"Couldn't reach the weather service ({e}). Check your internet connection.")


def _temp(celsius):
    return f"{round(celsius * 9 / 5 + 32)} F ({round(celsius)} C)"


def get_weather(city: str) -> dict:
    """Live weather for one city: right now, and each of the next 7 days."""
    # 1. Turn the city name into a place on the map. "Chicago, IL" is searched as "Chicago".
    name = city.split(",")[0].strip()
    found = _fetch("https://geocoding-api.open-meteo.com/v1/search", {"name": name, "count": 1})
    if not found.get("results"):
        raise LookupError(f"No place called {city!r}. Use a city name, like Atlanta or Hyderabad.")
    place = found["results"][0]

    # 2. Ask for the weather at that place.
    data = _fetch("https://api.open-meteo.com/v1/forecast", {
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "current": "temperature_2m,weather_code",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "auto",
        "forecast_days": 7,
    })

    # 3. Keep only what a person would want to know, in plain words.
    now, daily = data["current"], data["daily"]
    days = []
    for i, day in enumerate(daily["time"]):
        rain = daily["precipitation_probability_max"][i]
        days.append({
            "date": day,
            "sky": SKY.get(daily["weather_code"][i], "Mixed"),
            "high": _temp(daily["temperature_2m_max"][i]),
            "low": _temp(daily["temperature_2m_min"][i]),
            "chance_of_rain": "unknown" if rain is None else f"{rain}%",
        })
    where = ", ".join(x for x in [place["name"], place.get("admin1"), place.get("country")] if x)
    return {
        "place": where,
        "now": {"temperature": _temp(now["temperature_2m"]), "sky": SKY.get(now["weather_code"], "Mixed")},
        "next_7_days": days,
    }


def get_my_trips() -> dict:
    """Your upcoming trips, from the pretend calendar above."""
    return {"today": TODAY.isoformat(), "trips": TRIPS}


def add_reminder(text: str, date: str) -> dict:
    """Save a reminder for a day. Raises ValueError when the date isn't allowed."""
    try:
        day = datetime.date.fromisoformat(date)
    except ValueError:
        raise ValueError(f"{date!r} isn't a date. Use YYYY-MM-DD, like {_days_from_today(1)}.")
    if day < TODAY:
        raise ValueError(f"{day} is in the past. Today is {TODAY}.")
    if day > TODAY + datetime.timedelta(days=30):
        raise ValueError(f"{day} is too far ahead. Reminders can be at most 30 days from today ({TODAY}).")
    if not text.strip():
        raise ValueError("A reminder needs some text.")
    REMINDERS.append({"text": text.strip(), "date": day.isoformat()})
    return {"reminder_id": len(REMINDERS), "text": text.strip(), "date": day.isoformat(), "status": "saved"}
