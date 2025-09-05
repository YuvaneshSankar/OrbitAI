import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGODB_URL = os.getenv("MONGODB_URL")
NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")  # This is actually your Page ID

llm = ChatOpenAI(api_key=OPENAI_API_KEY, temperature=0.7)

class FetchCalendarEventsTool(BaseTool):
    name: str = "fetch_calendar_events"
    description: str = "Fetch today's calendar events from MongoDB."

    def _run(self, _input: str = None) -> str:
        try:
            client = MongoClient(MONGODB_URL)
            db = client["OrbitAI"]
            collection = db["OrbitAI"]
            
            today = datetime.now().strftime("%Y-%m-%d")
            events = []
            
            # Extract calendar events from MongoDB
            for record in collection.find():
                for key, value in record.items():
                    if 'calendar' in key.lower() or 'event' in key.lower() or 'meeting' in key.lower():
                        if isinstance(value, str) and len(value) > 10:
                            events.append(value)
            
            if not events:
                return "No calendar events found for today."
            
            # Use LLM to format events with IST timings
            prompt = f"""
            Extract and format today's calendar events from this data: {events[:5]}
            
            Requirements:
            - Only show events for today ({today})
            - Convert all times to IST (Indian Standard Time)
            - Format as: "Event Name at HH:MM AM/PM"
            - If no specific time, show as "Event Name (All day)"
            - Maximum 5 events
            - One event per line
            """
            
            response = llm([HumanMessage(content=prompt)])
            return response.content
            
        except Exception as e:
            return f"Error fetching calendar events: {str(e)}"

    async def _arun(self, _input: str = None) -> str:
        raise NotImplementedError()

class FetchNotionTasksTool(BaseTool):
    name: str = "fetch_notion_tasks"
    description: str = "Fetch priority tasks from Notion page."

    def _run(self, _input: str = None) -> str:
        try:
            headers = {
                "Authorization": f"Bearer {NOTION_API_TOKEN}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28"
            }
            
            # Use NOTION_DATABASE_ID as the page ID (since you stored it that way)
            page_id = NOTION_DATABASE_ID
            url = f"https://api.notion.com/v1/blocks/{page_id}/children"
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                return "Error fetching Notion tasks."
            
            data = response.json()
            tasks = []
            
            # Extract text from numbered_list_item and paragraph blocks
            for block in data.get("results", []):
                if block.get("type") == "numbered_list_item":
                    rich_text = block.get("numbered_list_item", {}).get("rich_text", [])
                    for text_obj in rich_text:
                        content = text_obj.get("plain_text", "").strip()
                        if content:
                            tasks.append(content)
                elif block.get("type") == "paragraph":
                    rich_text = block.get("paragraph", {}).get("rich_text", [])
                    for text_obj in rich_text:
                        content = text_obj.get("plain_text", "").strip()
                        if content:
                            tasks.append(content)
                            
            return "\n".join(tasks) if tasks else "No tasks found in Notion page."
            
        except Exception as e:
            return f"Error fetching Notion tasks: {str(e)}"

    async def _arun(self, _input: str = None) -> str:
        raise NotImplementedError()

class FetchNewsAndWeatherTool(BaseTool):
    name: str = "fetch_news_weather"
    description: str = "Fetch top news and weather information."

    def _run(self, _input: str = None) -> str:
        try:
            # Fetch news
            news_url = "https://saurav.tech/NewsAPI/top-headlines/category/general/in.json"
            news_response = requests.get(news_url)
            news_data = news_response.json()
            
            # Fetch weather
            weather_url = "https://api.open-meteo.com/v1/forecast?latitude=12.9165&longitude=79.1325&current=temperature_2m,wind_speed_10m,relative_humidity_2m&hourly=temperature_2m,precipitation"
            weather_response = requests.get(weather_url)
            weather_data = weather_response.json()
            
            # Format news
            news_items = []
            for article in news_data.get('articles', [])[:3]:
                title = article.get('title', 'No title')
                news_items.append(title)
            
            # Format weather
            current_weather = weather_data.get('current', {})
            temp = current_weather.get('temperature_2m', 'N/A')
            humidity = current_weather.get('relative_humidity_2m', 'N/A')
            wind = current_weather.get('wind_speed_10m', 'N/A')
            
            weather_summary = f"Temperature: {temp}°C, Humidity: {humidity}%, Wind: {wind} m/s"
            
            # Use LLM to format news and weather
            prompt = f"""
            Format this news and weather data:
            
            News headlines: {news_items}
            Weather: {weather_summary}
            
            Requirements:
            - Show 2 most important news items as bullet points
            - Add 1-2 weather-related bullet points
            - Keep it concise and relevant
            - Focus on actionable information
            """
            
            response = llm([HumanMessage(content=prompt)])
            return response.content
            
        except Exception as e:
            return f"Error fetching news and weather: {str(e)}"

    async def _arun(self, _input: str = None) -> str:
        raise NotImplementedError()

class GenerateSuggestionsTool(BaseTool):
    name: str = "generate_suggestions"
    description: str = "Generate personalized suggestions based on events, tasks, news, and weather."

    def _run(self, input_data: str) -> str:  # Changed to single input parameter
        try:
            # The input_data should be a formatted string with all the information
            prompt = f"""
            Based on the following information, generate 3-4 personalized actionable suggestions:
            
            {input_data}
            
            Guidelines for suggestions:
            1. For meetings: Suggest follow-ups, preparation tips, or related actions
            2. For tasks: Provide study tips, optimal timing, or resource recommendations
            3. Weather-related: Suggest best times for outdoor activities or precautions
            4. News-related: Connect current events to user's tasks/meetings if relevant
            
            Format as bullet points with actionable advice.
            Make suggestions specific and practical.
            Consider timing, weather, and task relationships.
            
            Examples:
            - If there's a basketball task and rain forecast: "Consider rescheduling outdoor activities to 2-4 PM when rain probability is lowest"
            - If studying linked lists: "Focus on implementation patterns and common interview questions for linked list problems"
            - If client meeting: "Prepare follow-up action items and consider scheduling next review meeting"
            """
            
            response = llm([HumanMessage(content=prompt)])
            return response.content
            
        except Exception as e:
            return f"Error generating suggestions: {str(e)}"

    async def _arun(self, input_data: str) -> str:
        raise NotImplementedError()


TOOLS = [FetchCalendarEventsTool(), FetchNotionTasksTool(), FetchNewsAndWeatherTool(), GenerateSuggestionsTool()]
