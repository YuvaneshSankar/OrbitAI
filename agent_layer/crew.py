import tasks

def save_briefing_to_md(filename: str, briefing_text: str):
    with open(filename, "w", encoding="utf-8") as md_file:
        md_file.write("# Daily Briefing\n\n")
        md_file.write(briefing_text)


class CrewAIOrchestrator:
    def __init__(self, user_id, access_token):
        self.user_id = user_id
        self.access_token = access_token

    def daily_workflow(self):
        print("Running Planner Agent...")
        plan_summary = tasks.run_planner_day_plan(self.user_id, self.access_token)

        print("Running Research Agent...")
        news = tasks.run_research_news_search("latest AI and productivity")

        print("Running Summarizer Agent...")
        combined_text = f"Plan Summary:\n{plan_summary}\n\nNews:\n{news}"
        briefing = tasks.run_summarizer_daily_briefing(combined_text)

        # Save briefing to markdown file
        save_briefing_to_md("daily_briefing.md", briefing)

        return {
            "planner_summary": plan_summary,
            "news": news,
            "daily_briefing": briefing,
        }


def main():
    user_id = "user123"
    access_token = "your_valid_google_calendar_access_token_here"

    crew = CrewAIOrchestrator(user_id, access_token)
    report = crew.daily_workflow()

    print("\n=== CrewAI Daily Workflow Report ===")
    print("Planner Summary:\n", report["planner_summary"])
    print("\nNews:\n", report["news"])
    print("\nDaily Briefing:\n", report["daily_briefing"])


if __name__ == "__main__":
    main()
