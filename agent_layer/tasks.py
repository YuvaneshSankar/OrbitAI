from agents import PlannerAgent, ResearchAgent, SummarizerAgent

def run_planner_day_plan(user_id, access_token):
    planner = PlannerAgent()
    return planner.plan_day(user_id, access_token)

def run_research_news_search(query="technology"):
    research = ResearchAgent()
    return research.fetch_news(query)

def run_summarizer_daily_briefing(text):
    summarizer = SummarizerAgent()
    return summarizer.summarize(text)
