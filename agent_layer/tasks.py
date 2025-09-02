# from agents import PlannerAgent, ResearchAgent, SummarizerAgent

# def run_planner_day_plan(user_id, access_token):
#     planner = PlannerAgent()
#     return planner.plan_day(user_id, access_token)

# def run_research_news_search(query="technology"):
#     research = ResearchAgent()
#     return research.fetch_news(query)

# def run_summarizer_daily_briefing(text):
#     summarizer = SummarizerAgent()
#     return summarizer.summarize(text)


from agents import PlannerAgent, ResearchAgent, SummarizerAgent

def run_planner_events(user_id, access_token):
    planner = PlannerAgent()
    events = planner.get_today_events(user_id, access_token)
    return events  # must be a list of strings

def run_planner_tasks(user_id, access_token):
    planner = PlannerAgent()
    tasks = planner.get_priority_tasks(user_id, access_token)
    return tasks  # must be a list of strings

def run_research_news_search(query="technology"):
    research = ResearchAgent()
    news = research.fetch_news_list(query)
    return news  # must be a list of strings

def run_summarizer_suggestions(events, tasks, news):
    summarizer = SummarizerAgent()
    prompt = (
        "Based on the following events, tasks and news, provide 3-4 personalized suggestions for the user:\n"
        f"Events: {events}\nTasks: {tasks}\nNews: {news}"
    )
    suggestions = summarizer.summarize_to_list(prompt)
    return suggestions
