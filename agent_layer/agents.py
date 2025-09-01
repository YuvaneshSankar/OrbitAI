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
        self.agent = initialize_agent(langchain_tools, llm, agent="zero-shot-react-description", verbose=True)

    def plan_day(self, user_id, access_token):
        # Pass only the access token string to tool
        return self.agent.run(access_token)

class ResearchAgent:
    def __init__(self):
        self.agent = initialize_agent(langchain_tools, llm, agent="zero-shot-react-description", verbose=True)

    def fetch_news(self, topic: str):
        return self.agent.run(f"Search news related to {topic}")

class SummarizerAgent:
    def __init__(self):
        self.agent = initialize_agent(langchain_tools, llm, agent="zero-shot-react-description", verbose=True)

    def summarize(self, text: str):
        return self.agent.run(f"Summarize the following text:\n{text}")
