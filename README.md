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

<!-- To be filled in after running the tests. -->
