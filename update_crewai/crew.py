import tasks
from datetime import datetime
from debug_calendar import get_todays_calendar_events  # Import the function

def save_briefing_to_md(filename: str, events: str, priority_tasks: str, news_weather: str, suggestions: str):
    today_date = datetime.now().strftime("%B %d, %Y")
    
    content = f"""# Daily Briefing

Your personalized overview for today

## 📅 Today's Events

{events}

## ✅ Priority Tasks

{priority_tasks}

## 📰 Top News

{news_weather}

## 💡 Suggestions

{suggestions}

---
*Generated on {today_date}*
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Daily briefing saved to {filename}")

class DailyBriefingCrew:
    def __init__(self):
        pass

    def run_daily_workflow(self):
        print("🚀 Starting Daily Briefing Generation...")
        
        print("📅 Fetching calendar events...")
        events = get_todays_calendar_events()  # Use your working function instead
        
        print("✅ Fetching priority tasks...")
        priority_tasks = tasks.get_priority_tasks()
        
        print("📰 Fetching news and weather...")
        news_weather = tasks.get_news_and_weather()
        
        print("💡 Generating suggestions...")
        suggestions = tasks.generate_suggestions(events, priority_tasks, news_weather)
        
        # Save to markdown file
        save_briefing_to_md("daily_briefing.md", events, priority_tasks, news_weather, suggestions)
        
        return {
            "events": events,
            "tasks": priority_tasks, 
            "news_weather": news_weather,
            "suggestions": suggestions
        }
