# Personal assistant agent: project plan

This is a small learning project. The user is a beginner. Build it one step at a time.

## Goal

`agent.py` is a personal assistant. It answers a question by calling tools:

- `get_weather`: live weather
- `get_my_trips`: the user's upcoming trips
- `add_reminder`: adds a reminder

## Files

- `toolbox.py` is provided and must **never be edited**. `agent.py` imports it and calls `toolbox.get_weather`, `toolbox.get_my_trips` and `toolbox.add_reminder`.
- `agent.py` is the only file to create or change.
- `.env` holds `ANTHROPIC_API_KEY`. Do not read it aloud or print it. Never show the key to the user and never write it into code.
- `.venv/` is the project's virtual environment. Do not change it.
- Do not change any other file unless the user asks.

## Environment

- Python 3.10 or newer.
- Run everything from this folder, using the `.venv` virtual environment.
- Libraries (already installed): `anthropic` and `python-dotenv`.
- Model: `claude-haiku-5-5`.

## Structure of agent.py (build in this order)

One file, built step by step:

1. `SYSTEM`: the system prompt, as a string.
2. `TOOLS`: the tool definitions as plain dicts (name, description, input_schema).
3. `run_tool(name, tool_input)`: calls the matching `toolbox` function and returns its result.
4. `ask(question)`: the agent loop on the Messages API. Send the question, check for `tool_use` blocks, run the tools, send `tool_result` blocks back, and repeat until the model stops asking for tools.
5. `ask_with_runner(question)`: the same job using the SDK's Tool Runner.
6. `main()`: uses `argparse` to read the question from the command line.

Load `.env` with `python-dotenv`. Do not hard-code the key.

## Rules for the code

- Keep it simple and well commented for a beginner.
- No classes and no agent frameworks.
- Only build the step the user asks for.
- After each change, tell the user the exact command to test it.

## Working style

- Do not write Python until the user asks for a specific step.
- Report what was changed and how to test it.
