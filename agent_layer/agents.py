from langchain.agents import initialize_agent, Tool
from langchain_community.chat_models import ChatOpenAI
from tools import TOOLS

llm = ChatOpenAI(temperature=0.5)

def make_tool(tool):
    return Tool(
        name=tool.name,
        func=tool._run,
        description=tool.description,
    )

langchain_tools = [make_tool(tool) for tool in TOOLS]

class PlannerAgent:
    def __init__(self):
        self.agent = initialize_agent(
            langchain_tools,
            llm,
            agent="zero-shot-react-description",
            verbose=True,
            handle_parsing_errors=True
        )

    def get_today_events(self, user_id, access_token):
        resp = self.agent.run(
            f"List today's Google Calendar events with times from access token: {access_token}. Output as bullet points."
        )
        return resp.strip().split('\n') if resp else []

    def get_priority_tasks(self, user_id, access_token):
        resp = self.agent.run(
            f"List priority tasks for today from Todoist using token: {access_token}. Output as bullet points."
        )
        return resp.strip().split('\n') if resp else []

class ResearchAgent:
    def __init__(self):
        self.agent = initialize_agent(
            langchain_tools,
            llm,
            agent="zero-shot-react-description",
            verbose=True,
            handle_parsing_errors=True
        )

    def fetch_news_list(self, topic):
        resp = self.agent.run(
            f"List top 3 news headlines about {topic}. Output as bullet points."
        )
        return resp.strip().split('\n') if resp else []

class SummarizerAgent:
    def __init__(self):
        self.agent = initialize_agent(
            langchain_tools,
            llm,
            agent="zero-shot-react-description",
            verbose=True,
            handle_parsing_errors=True
        )

    def summarize_to_list(self, text):
        resp = self.agent.run(
            f"Given this content:\n{text}\nOutput 3-4 actionable suggestions as bullet points."
        )
        return resp.strip().split('\n') if resp else []
