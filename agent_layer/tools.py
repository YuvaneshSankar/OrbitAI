import os
import requests
from dotenv import load_dotenv
from langchain.tools import BaseTool
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
TODOIST_API_TOKEN = os.getenv("TASKS_API_TOKEN")
NOTION_INTEGRATION_TOKEN = os.getenv("INTERNAL_INTEGRATION_SECRET")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_ACCESS_KEY")
SEMANTIC_SCHOLAR_API_KEY = os.getenv("")

llm = ChatOpenAI(temperature=0.5, openai_api_key=OPENAI_API_KEY)

class FetchCalendarEventsTool(BaseTool):
    name: str = "fetch_calendar_events"
    description: str = "Fetch calendar events using a valid OAuth access token."

    def _run(self, access_token: str) -> str:
        print(f"[DEBUG] Using Google Calendar Access Token: {access_token[:20]}...")  # Debug token partial
        url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
        headers = {"Authorization": f"Bearer {access_token.strip()}"}
        params = {"maxResults": 50, "orderBy": "startTime", "singleEvents": "true"}

        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        events = r.json()

        # Format event list with summary and start time
        lines = []
        for event in events.get("items", []):
            start = event.get("start", {})
            start_str = start.get("dateTime") or start.get("date") or "Unknown time"
            summary = event.get("summary", "No Title")
            lines.append(f"{summary} at {start_str}")

        return "\n".join(lines) if lines else "No events found."

    async def _arun(self, access_token: str) -> str:
        raise NotImplementedError("Async not implemented.")

class FetchTasksTool(BaseTool):
    name: str = "fetch_tasks"
    description: str = "Fetch tasks for a user from Todoist."

    def _run(self, _input: str) -> str:
        headers = {"Authorization": f"Bearer {TODOIST_API_TOKEN}"}
        r = requests.get("https://api.todoist.com/rest/v2/tasks", headers=headers)
        r.raise_for_status()
        tasks = r.json()
        # Format task list (assuming each task has 'content')
        lines = [task.get("content", "Untitled task") for task in tasks]
        return "\n".join(lines) if lines else "No tasks found."

    async def _arun(self, _input: str) -> str:
        raise NotImplementedError()

class SearchNewsTool(BaseTool):
    name: str = "search_news"
    description: str = "Search news headlines by query."

    def _run(self, query: str) -> str:
        url = "https://newsapi.org/v2/everything"
        params = {"q": query, "apiKey": NEWS_API_KEY, "pageSize": 5}
        r = requests.get(url, params=params)
        r.raise_for_status()
        articles = r.json().get("articles", [])
        titles = [a["title"] for a in articles]
        return "\n".join(titles) if titles else "No news found."

    async def _arun(self, query: str) -> str:
        raise NotImplementedError()

class SummarizeTextTool(BaseTool):
    name: str = "summarize_text"
    description: str = "Summarize provided text using OpenAI."

    def _run(self, text: str) -> str:
        response = llm([HumanMessage(content=f"Summarize this: {text}")])
        return response.content

    async def _arun(self, text: str) -> str:
        raise NotImplementedError()

TOOLS = [FetchCalendarEventsTool(), FetchTasksTool(), SearchNewsTool(), SummarizeTextTool()]   
