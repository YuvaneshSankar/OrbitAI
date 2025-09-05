from langchain.agents import initialize_agent, Tool
from langchain_openai import ChatOpenAI
from tools import TOOLS
import os

llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), temperature=0.5)

def make_tool(tool):
    return Tool(
        name=tool.name,
        func=tool._run,
        description=tool.description,
    )

langchain_tools = [make_tool(tool) for tool in TOOLS]

class CalendarAgent:
    def __init__(self):
        self.agent = initialize_agent(
            langchain_tools,
            llm,
            agent="zero-shot-react-description",
            verbose=False,
            handle_parsing_errors=True
        )

    def get_today_events(self):
        return self.agent.run("Fetch today's calendar events with IST timings. Format as event name and time.")

class TaskAgent:
    def __init__(self):
        self.agent = initialize_agent(
            langchain_tools,
            llm,
            agent="zero-shot-react-description", 
            verbose=False,
            handle_parsing_errors=True
        )

    def get_priority_tasks(self):
        return self.agent.run("Fetch priority tasks from Notion database. Show as bullet points.")

class NewsWeatherAgent:
    def __init__(self):
        self.agent = initialize_agent(
            langchain_tools,
            llm,
            agent="zero-shot-react-description",
            verbose=False, 
            handle_parsing_errors=True
        )

    def get_news_weather(self):
        return self.agent.run("Fetch top news and current weather information. Format as bullet points.")

class SuggestionsAgent:
    def __init__(self):
        self.agent = initialize_agent(
            langchain_tools,
            llm,
            agent="zero-shot-react-description",
            verbose=False,
            handle_parsing_errors=True
        )

    def generate_suggestions(self, events, tasks, news_weather):
        return self.agent.run(f"Generate personalized suggestions based on: Events: {events}, Tasks: {tasks}, News/Weather: {news_weather}")
