import tasks

def save_briefing_to_md(filename: str, briefing_dict: dict):
    lines = []
    lines.append("# Daily Briefing\n")
    lines.append("Your personalized overview for today\n\n")

    if briefing_dict.get("events"):
        lines.append("## :calendar: Today's Events\n")
        for event in briefing_dict["events"]:
            lines.append(f"- {event}")
        lines.append("")

    if briefing_dict.get("tasks"):
        lines.append("## :clipboard: Priority Tasks\n")
        for task in briefing_dict["tasks"]:
            lines.append(f"- {task}")
        lines.append("")

    if briefing_dict.get("news"):
        lines.append("## :newspaper: Top News\n")
        for item in briefing_dict["news"]:
            lines.append(f"- {item}")
        lines.append("")

    if briefing_dict.get("suggestions"):
        lines.append("## :bulb: Suggestions\n")
        for suggestion in briefing_dict["suggestions"]:
            lines.append(f"- {suggestion}")
        lines.append("")

    with open(filename, "w", encoding="utf-8") as md_file:
        md_file.write("\n".join(lines))

class CrewAIOrchestrator:
    def __init__(self, user_id, access_token):
        self.user_id = user_id
        self.access_token = access_token

    def daily_workflow(self):
        print("Getting calendar events...")
        events = tasks.run_planner_events(self.user_id, self.access_token)

        print("Getting priority tasks...")
        tasks_list = tasks.run_planner_tasks(self.user_id, self.access_token)

        print("Getting news...")
        news = tasks.run_research_news_search("latest AI and productivity")

        print("Getting suggestions...")
        suggestions = tasks.run_summarizer_suggestions(events, tasks_list, news)

        briefing = {
            "events": events,
            "tasks": tasks_list,
            "news": news,
            "suggestions": suggestions,
        }

        save_briefing_to_md("daily_briefing.md", briefing)
        print("Saved daily briefing to daily_briefing.md")

        return briefing

# CLI demo if needed
def main():
    import os
    user_id = "user123"
    access_token = os.getenv("GOOGLE_CALENDAR_ACCESS_TOKEN")
    crew = CrewAIOrchestrator(user_id, access_token)
    briefing = crew.daily_workflow()

    print("\n=== Daily Briefing ===")
    for section, items in briefing.items():
        print(f"\n{section.capitalize()}:")
        for item in items:
            print("-", item)

if __name__ == "__main__":
    main()
