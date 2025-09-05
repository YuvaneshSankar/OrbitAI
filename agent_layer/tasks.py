from agents import PlannerAgent, ResearchAgent, SummarizerAgent

def run_planner_events(user_id, access_token):
    planner = PlannerAgent()
    events = planner.get_today_events(user_id, access_token)
    print(f"[DEBUG] Planner events: {events}")
    return events

def run_planner_tasks(user_id, access_token):
    planner = PlannerAgent()
    tasks = planner.get_priority_tasks(user_id, access_token)
    print(f"[DEBUG] Planner tasks: {tasks}")
    return tasks

def run_research_news_search(query="technology"):
    research = ResearchAgent()
    news = research.fetch_news_list(query)
    print(f"[DEBUG] Research news: {news}")
    return news

def run_summarizer_suggestions(events, tasks, news):
    summarizer = SummarizerAgent()
    events_text = "\n".join(events)
    tasks_text = "\n".join(tasks)
    news_text = "\n".join(news)

    prompt = (
        f"Based on the following events:\n{events_text}\n\n"
        f"and these tasks:\n{tasks_text}\n\n"
        f"and these news headlines:\n{news_text}\n\n"
        "Provide 3-4 actionable personalized suggestions as bullet points."
    )
    print(f"[DEBUG] Summarizer prompt:\n{prompt}")

    suggestions = summarizer.summarize_to_list(prompt)
    print(f"[DEBUG] Suggestions: {suggestions}")
    return suggestions
