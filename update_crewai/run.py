import os
from dotenv import load_dotenv
from crew import DailyBriefingCrew

load_dotenv()

def main():
    print("=" * 50)
    print("🌅 DAILY BRIEFING GENERATOR")
    print("=" * 50)
    
    crew = DailyBriefingCrew()
    
    try:
        briefing = crew.run_daily_workflow()
        
        print("\n" + "=" * 50)
        print("✅ Daily Briefing Generated Successfully!")
        print("📄 Check daily_briefing.md for the full report")
        print("=" * 50)
        
        # Optional: Print preview
        print("\n📋 PREVIEW:")
        print("-" * 30)
        print("📅 Events:", briefing["events"][:100] + "...")
        print("✅ Tasks:", briefing["tasks"][:100] + "...")
        print("📰 News:", briefing["news_weather"][:100] + "...")
        print("💡 Suggestions:", briefing["suggestions"][:100] + "...")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
