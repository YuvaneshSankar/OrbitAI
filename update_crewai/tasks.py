from agents import CalendarAgent, TaskAgent, NewsWeatherAgent, SuggestionsAgent

def get_calendar_events():
    agent = CalendarAgent()
    return agent.get_today_events()

def get_priority_tasks():
    agent = TaskAgent()
    return agent.get_priority_tasks()

def get_news_and_weather():
    agent = NewsWeatherAgent()
    return agent.get_news_weather()

def generate_suggestions(events, tasks, news_weather):
    agent = SuggestionsAgent()
    return agent.generate_suggestions(events, tasks, news_weather)
