from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.models.lite_llm import LiteLlm
from mcp import StdioServerParameters
from env import NOTION_TOKEN
from .prompt import DESCRIPTION, INSTRUCTION



root_agent = Agent(
    model="gemini-2.5-flash",
    name="notion_assistant",
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=["-y","@notionhq/notion-mcp-server"],
                    env={"NOTION_TOKEN": NOTION_TOKEN}
                ),
                timeout=15
            )
        )
    ]
)
