import os
from dotenv import load_dotenv
from crew import CrewAIOrchestrator

load_dotenv()

def main():
    user_id = "user123"
    gcal_token = os.getenv("GOOGLE_CALENDAR_ACCESS_TOKEN") 

    crew = CrewAIOrchestrator(user_id, gcal_token)
    report = crew.daily_workflow()

    print("\n=== Personal AI Copilot Report ===")
    print("Planner Summary:\n", report['planner_summary'])
    print("\nNews:\n", report['news'])
    print("\nDaily Briefing:\n", report['daily_briefing'])

if __name__ == "__main__":
    main()
