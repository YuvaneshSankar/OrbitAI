import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from dateutil import parser
import pytz

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGODB_URL = os.getenv("MONGODB_URL")
NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

llm = ChatOpenAI(api_key=OPENAI_API_KEY, temperature=0.7)

class FetchCalendarEventsTool(BaseTool):
    name: str = "fetch_calendar_events"
    description: str = "Fetch today's calendar events from MongoDB."

    def _run(self, _input: str = None) -> str:
        try:
            client = MongoClient(MONGODB_URL)
            db = client["OrbitAI"]
            collection = db["OrbitAI"]
            
            # Get today's date in IST
            ist = pytz.timezone('Asia/Kolkata')
            today = datetime.now(ist).date()
            
            todays_events = []
            unique_events = set()
            
            # Extract calendar events from ALL records
            for record in collection.find():
                for key, value in record.items():
                    if key == '_id':
                        continue
                    
                    # Calendar events are stored as FIELD NAMES starting with "calendar:"
                    if key.startswith('calendar:') and 'id:' in key and len(key) > 50:
                        # Extract event data from the key itself
                        calendar_key = key.replace('calendar: ', '')
                        
                        # Parse the multiline event data
                        lines = calendar_key.split('\n')
                        event_data = {}
                        
                        for line in lines:
                            if ':' in line and len(line) > 3:
                                parts = line.split(':', 1)
                                if len(parts) == 2:
                                    k = parts[0].strip()
                                    v = parts[1].strip()
                                    event_data[k] = v
                        
                        # Check if this is a valid calendar event
                        if 'name' in event_data and 'start' in event_data and 'id' in event_data:
                            event_id = event_data['id']
                            event_name = event_data['name']
                            start_time_str = event_data['start']
                            
                            # Skip duplicates
                            if event_id in unique_events:
                                continue
                            unique_events.add(event_id)
                            
                            try:
                                # Parse the datetime with timezone awareness
                                event_dt = parser.parse(start_time_str)
                                event_dt_ist = event_dt.astimezone(ist)
                                
                                # Check if this event is for today
                                if event_dt_ist.date() == today:
                                    time_str = event_dt_ist.strftime("%I:%M %p")
                                    todays_events.append(f"• {event_name} at {time_str}")
                                    
                            except Exception as e:
                                # Fallback: check string date match
                                today_str = today.strftime("%Y-%m-%d")
                                if today_str in start_time_str:
                                    todays_events.append(f"• {event_name}")
            
            if not todays_events:
                return "No calendar events found for today."
            
            return "\n".join(todays_events)
            
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
            
            page_id = NOTION_DATABASE_ID
            url = f"https://api.notion.com/v1/blocks/{page_id}/children"
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                return "Error fetching Notion tasks."
            
            data = response.json()
            tasks = []
            
            for block in data.get("results", []):
                if block.get("type") == "numbered_list_item":
                    rich_text = block.get("numbered_list_item", {}).get("rich_text", [])
                    for text_obj in rich_text:
                        content = text_obj.get("plain_text", "").strip()
                        if content:
                            tasks.append(f"• {content}")
                elif block.get("type") == "paragraph":
                    rich_text = block.get("paragraph", {}).get("rich_text", [])
                    for text_obj in rich_text:
                        content = text_obj.get("plain_text", "").strip()
                        if content:
                            tasks.append(f"• {content}")
                            
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
            for article in news_data.get('articles', [])[:2]:
                title = article.get('title', 'No title')
                news_items.append(f"• {title}")
            
            # Format weather
            current_weather = weather_data.get('current', {})
            temp = current_weather.get('temperature_2m', 'N/A')
            humidity = current_weather.get('relative_humidity_2m', 'N/A')
            wind = current_weather.get('wind_speed_10m', 'N/A')
            
            weather_info = f"• Temperature: {temp}°C, Humidity: {humidity}%, Wind: {wind} m/s"
            
            # Combine news and weather
            result = news_items + [weather_info]
            return "\n".join(result)
            
        except Exception as e:
            return f"Error fetching news and weather: {str(e)}"

    async def _arun(self, _input: str = None) -> str:
        raise NotImplementedError()

class GenerateSuggestionsTool(BaseTool):
    name: str = "generate_suggestions"
    description: str = "Generate personalized suggestions based on events, tasks, news, and weather."

    def _run(self, input_data: str) -> str:
        try:
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
