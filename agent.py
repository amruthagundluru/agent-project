"""Personal assistant agent.

Step 3: the agent loop. This file defines what the assistant is told (SYSTEM), which
tools it can use (TOOLS), how to run one of those tools (run_tool), and the loop
that asks the model and runs its tools (ask).
"""

import datetime
import json
import argparse

from anthropic import Anthropic, beta_tool
from anthropic.lib.tools import ToolError
from dotenv import load_dotenv

import toolbox

# Read the .env file so ANTHROPIC_API_KEY is available.
load_dotenv()

# The client talks to the Anthropic API. It reads the key from the environment.
client = Anthropic()

# The model we will ask questions with.
MODEL = "claude-haiku-5-5"

# The most times the agent may ask the model for a reply in one question.
# This stops a loop that never ends.
MAX_STEPS = 8


# The system prompt: instructions that tell the model how to behave.
# The f-string puts today's date in, because the model doesn't know what day it is.
SYSTEM = f"""You are a friendly personal assistant for weather, my trips and my reminders.
Today's date is {datetime.date.today().isoformat()}.

Rules:
- Use your tools to get information. Never guess the weather, a trip or a date.
- If I mention a trip but don't say where or when, check my trips with get_my_trips first.
- Only add a reminder when I ask for one. If the day isn't clear, ask me which day.
- If a question has nothing to do with weather, trips or reminders, politely say that
  you can only help with those.
- If a tool returns an error, explain it in plain words and don't retry the same call.
- Never state the weather, a trip or a reminder that a tool didn't actually return.
- Keep answers short and friendly."""


# The tools the model may ask us to use. Each one is a plain dict with:
#   name:         the name the model uses to ask for the tool
#   description:  what the tool does, what it returns and when to use it
#   input_schema: a JSON Schema that describes the inputs the tool needs
TOOLS = [
    {
        "name": "get_weather",
        "description": (
            "Get live weather for a city: the current temperature and sky, and the "
            "forecast for each of the next 7 days. Use this whenever I ask about the "
            "weather. The city is a name only, like Atlanta or Hyderabad."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name only, like Atlanta or Hyderabad.",
                },
            },
            "required": ["city"],
        },
    },
    {
        "name": "get_my_trips",
        "description": (
            "Get my upcoming trips: the city, the leave and return dates, and why I am "
            "going. Call this first when I mention a trip without saying the city or "
            "the dates."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "add_reminder",
        "description": (
            "Save a reminder for a day. This changes my reminders, so use it only when "
            "I ask for one. The date must be in YYYY-MM-DD format, from today up to 30 "
            "days ahead. The tool fails if the date is in the past."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "What the reminder is about.",
                },
                "date": {
                    "type": "string",
                    "description": "The day for the reminder, in YYYY-MM-DD format.",
                },
            },
            "required": ["text", "date"],
        },
    },
]


# Questions for --test. Each one checks a different part of the agent.
TEST_QUESTIONS = [
    "Is it warmer in Chicago or Hyderabad right now?",
    "Do I need an umbrella on my next trip?",
    "Remind me to pack a warm coat the day before my Chicago trip.",
    "Remind me to renew my passport on 1 January 2020.",
    "Can you book me a flight to Chicago?",
]


def run_tool(name, tool_input):
    """Run one tool from toolbox.py and return its result as a JSON string.

    name is the tool's name, like "get_weather".
    tool_input is a dict with the tool's inputs, like {"city": "Atlanta"}.
    """
    if name == "get_weather":
        result = toolbox.get_weather(tool_input["city"])
    elif name == "get_my_trips":
        result = toolbox.get_my_trips()
    elif name == "add_reminder":
        result = toolbox.add_reminder(tool_input["text"], tool_input["date"])
    else:
        # The model asked for a tool we don't have.
        raise ValueError(f"Unknown tool: {name!r}")

    # Turn the Python dict into text, so the model can read it.
    return json.dumps(result)


def ask(question):
    """Answer a question, using tools as many times as the model needs.

    This is the agent loop:
      1. Send the question (and everything said so far) to the model.
      2. If the model is done, return its text answer.
      3. If the model wants tools, run them, send the results back, and go round again.
    """
    # The conversation so far. Each entry has a role ("user" or "assistant") and content.
    messages = [{"role": "user", "content": question}]

    for step in range(MAX_STEPS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=8000,
            system=SYSTEM,
            tools=TOOLS,
            messages=messages,
        )

        # Keep the model's whole reply in the conversation, so it remembers what it asked for.
        messages.append({"role": "assistant", "content": response.content})

        # stop_reason tells us why the model stopped. "tool_use" means it wants a tool run.
        if response.stop_reason != "tool_use":
            # The model is done. Join the text pieces of its reply into one string.
            return "".join(block.text for block in response.content if block.type == "text")

        # The model wants tools. Run each one and collect the results.
        results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  -> {block.name}({json.dumps(block.input)})")
                # If the tool fails, send the error back to the model instead of crashing.
                try:
                    output = run_tool(block.name, block.input)
                    is_error = False
                except (LookupError, ValueError, ConnectionError) as e:
                    output = f"Error: {e}"
                    is_error = True
                print(f"  <- {output}")
                # Each result must say which tool call it answers, using the same id.
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output,
                    "is_error": is_error,
                })

        # Send all the results back in one user message, then go round again.
        messages.append({"role": "user", "content": results})

    # The loop ran MAX_STEPS times and the model still wanted more tools.
    return (f"Sorry, I couldn't finish that within {MAX_STEPS} steps. "
            "Could you ask it a different way?")


# The same three tools, written for the SDK's Tool Runner.
# @beta_tool reads the function's name, type hints, docstring and Args: section
# and builds the tool definition for us, so we don't write TOOLS dicts for these.
# Each function calls the matching function in toolbox.py and returns JSON text.

@beta_tool
def get_weather(city: str) -> str:
    """Get live weather for a city: the current temperature and sky, and the forecast for each of the next 7 days. Use this whenever I ask about the weather. The city is a name only, like Atlanta or Hyderabad.

    Args:
        city: The city name only, like Atlanta or Hyderabad.
    """
    try:
        return json.dumps(toolbox.get_weather(city))
    except (LookupError, ValueError, ConnectionError) as e:
        # ToolError tells the runner the tool failed, so the model sees the message.
        raise ToolError(str(e))


@beta_tool
def get_my_trips() -> str:
    """Get my upcoming trips: the city, the leave and return dates, and why I am going. Call this first when I mention a trip without saying the city or the dates.
    """
    try:
        return json.dumps(toolbox.get_my_trips())
    except (LookupError, ValueError, ConnectionError) as e:
        raise ToolError(str(e))


@beta_tool
def add_reminder(text: str, date: str) -> str:
    """Save a reminder for a day. This changes my reminders, so use it only when I ask for one. The date must be in YYYY-MM-DD format, from today up to 30 days ahead. The tool fails if the date is in the past.

    Args:
        text: What the reminder is about.
        date: The day for the reminder, in YYYY-MM-DD format.
    """
    try:
        return json.dumps(toolbox.add_reminder(text, date))
    except (LookupError, ValueError, ConnectionError) as e:
        raise ToolError(str(e))


def ask_with_runner(question):
    """Answer a question with the SDK's Tool Runner.

    The runner does the same loop as ask(): it calls the model, runs the tools,
    sends the results back, and stops when the model is done.
    """
    runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=8000,
        system=SYSTEM,
        tools=[get_weather, get_my_trips, add_reminder],
        max_iterations=MAX_STEPS,
        messages=[{"role": "user", "content": question}],
    )

    # Looping over the runner gives us each message the model sends back.
    last_message = None
    for message in runner:
        # Show each tool the model asked for, in the same style as ask().
        for block in message.content:
            if block.type == "tool_use":
                print(f"  -> {block.name}({json.dumps(block.input)})")
        last_message = message

    # The last message holds the final answer.
    return "".join(block.text for block in last_message.content if block.type == "text")


def main():
    # argparse reads options from the command line, like --try-tools or a question.
    parser = argparse.ArgumentParser(description="Personal assistant agent.")
    parser.add_argument(
        "question",
        nargs="?",
        help='A question in quotes, like "What is the weather in Atlanta?"',
    )
    parser.add_argument(
        "--try-tools",
        action="store_true",
        help="Run the tools directly once, without calling the model.",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run the test questions in TEST_QUESTIONS one after another.",
    )
    parser.add_argument(
        "--runner",
        action="store_true",
        help="Use the SDK's Tool Runner (ask_with_runner) instead of the ask() loop.",
    )
    args = parser.parse_args()

    # Pick which agent loop to use: the Tool Runner, or our own ask() loop.
    ask_fn = ask_with_runner if args.runner else ask

    if args.test:
        # Ask each test question in turn, with a blank line between them.
        for i, question in enumerate(TEST_QUESTIONS):
            if i > 0:
                print()
            print(f"You: {question}")
            answer = ask_fn(question)
            print(f"Assistant: {answer}")
    elif args.try_tools:
        print(run_tool("get_weather", {"city": "Atlanta"}))
        print(run_tool("get_my_trips", {}))
    elif args.question:
        print(f"You: {args.question}")
        answer = ask_fn(args.question)
        print(f"Assistant: {answer}")
    else:
        print('Try: python agent.py "a question"  or  python agent.py --try-tools')


if __name__ == "__main__":
    main()
