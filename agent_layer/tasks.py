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
    # Convert lists into plain text strings
    events_text = "\n".join(events)
    tasks_text = "\n".join(tasks)
    news_text = "\n".join(news)

    prompt = (
        f"Based on the following events:\n{events_text}\n\n"
        f"and these tasks:\n{tasks_text}\n\n"
        f"and these news headlines:\n{news_text}\n\n"
        "Provide 3-4 actionable personalized suggestions as bullet points."
    )

    suggestions = summarizer.summarize_to_list(prompt)
    return suggestions
