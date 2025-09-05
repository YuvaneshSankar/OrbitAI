import os
from dotenv import load_dotenv
from crew import CrewAIOrchestrator

load_dotenv()

def main():
    user_id = "user123"
    gcal_token = os.getenv("GOOGLE_CALENDAR_ACCESS_TOKEN")
    print(f"[DEBUG] Loaded GOOGLE_CALENDAR_ACCESS_TOKEN: {gcal_token[:20]}...")

    crew = CrewAIOrchestrator(user_id, gcal_token)
    report = crew.daily_workflow()

    print("\n=== Personal AI Copilot Report ===")
    print("Today's Events:\n", "\n".join(report["events"]))
    print("\nPriority Tasks:\n", "\n".join(report["tasks"]))
    print("\nNews:\n", "\n".join(report["news"]))
    print("\nSuggestions:\n", "\n".join(report["suggestions"]))

if __name__ == "__main__":
    main()
