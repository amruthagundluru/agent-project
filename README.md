# Personal assistant agent

`agent.py` is a small personal assistant. You ask it a question, and it answers by calling tools. It is a learning project, built one step at a time.

## What it does

The agent can use three tools:

- **`get_weather(city)`**: live weather for a city, now and for the next 7 days. The weather comes from [Open-Meteo](https://open-meteo.com/), a free weather service that needs no key.
- **`get_my_trips()`**: your upcoming trips. These come from a pretend calendar in `toolbox.py`.
- **`add_reminder(text, date)`**: saves a reminder for a day from today up to 30 days ahead. Reminders are pretend too: they are kept only while the program runs.

`toolbox.py` holds these tools and must not be edited. `agent.py` imports it and calls its functions.

Two ways to run the agent loop:

- **`ask(question)`**: the agent loop written by hand, on the Messages API.
- **`ask_with_runner(question)`**: the same job using the SDK's Tool Runner.

The loop stops after `MAX_STEPS` (8) model calls, so it can't run forever.

## Install

Requires Python 3.10 or newer.

```
python -m venv .venv
.venv\Scripts\activate
pip install anthropic python-dotenv
```

Create a file named `.env` in this folder with your API key:

```
ANTHROPIC_API_KEY=your-key-here
```

Keep `.env` private. It is listed in `.gitignore`, so git won't upload it.

## Run

Ask one question:

```
python agent.py "Is it warmer in Chicago or Hyderabad right now?"
```

Run the built-in test questions:

```
python agent.py --test
```

Use the SDK's Tool Runner instead of the hand-written loop:

```
python agent.py --runner "What trips do I have coming up?"
python agent.py --test --runner
```

Run the tools directly, without the model:

```
python agent.py --try-tools
```

## What I saw

1. What's the weather in Piler in India, Andhra Pradesh State?

What's the weather in Piler in India, Andhra Pradesh State?
  -> get_weather({"city": "Piler"})
  <- {"place": "Piler, Grisons, Switzerland", "now": {"temperature": "22 F (-6 C)", "sky": "Cloudy"}, ..
Assistant: The weather service returned **Piler in Grisons, Switzerland**, not Piler in Andhra Pradesh, India. I can only look up a city by name, so I can't pick the Indian location. Here's the Swiss Piler:

If you meant the Indian town, you could give me a nearby larger city and I can check that instead.

2. What's the weather in New YORK? (WIFI OFF)

You: What's the weather in New YORK
Traceback (most recent call last):
  File "C:\Users\Sunitha\OneDrive\Desktop\Muthyalu\Practice\agent-project\.venv\Lib\site-packages\httpx2\_transports\default.py", line 95, in map_httpcore_exceptions
    yield
  File "C:\Users\Sunitha\OneDrive\Desktop\Muthyalu\Practice\agent-project\.venv\Lib\site-packages\httpx2\_transports\default.py", line 242, in handle_request
    resp = self._pool.handle_request(req)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

3. Remind me about my next trip in Summer 2027?

Remind me about my next trip in Summer 2027
  -> get_my_trips({})
  <- {"today": "2026-11-24", "trips": [{"city": "Chicago", "leaves": "2026-11-26", "returns": "2026-11-28", "why": "Work conference"}, {"city": "Hyderabad", "leaves": "2026-11-30", "returns": "2026-12-14", "why": "Family visit"}]}
Assistant: I checked your trips, and none are in summer 2027. Your upcoming trips are:

- **Chicago** (work conference): Nov 26 to Nov 28, 2026
- **Hyderabad** (family visit): Nov 30 to Dec 14, 2026

Did you mean one of these? If so, tell me which one and what day you'd like the reminder. Or if you have a summer 2027 trip planned that isn't in your list, tell me the city and dates and I can set the reminder for a day you choose.


