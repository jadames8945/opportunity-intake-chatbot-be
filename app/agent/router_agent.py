import logging
from typing import Any

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.agent.prompts.router_prompts import (
    ROUTER_ROLE,
    AVAILABLE_AGENTS,
    ROUTING_RULES,
    ROUTING_EXAMPLES,
    RESPONSE_FORMAT,
    ROUTER_INSTRUCTIONS,
)

logger = logging.getLogger(__name__)


class RouterAgent:

    def __init__(self):
        self.prompt = self._build_prompt()

    def _build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
            {ROUTER_ROLE}

            {AVAILABLE_AGENTS}

            {ROUTING_RULES}

            {ROUTING_EXAMPLES}

            {RESPONSE_FORMAT}

            {ROUTER_INSTRUCTIONS}
            
            Context available to you:
            {{chat_history}}
            """,
                ),
                ("human", "{user_input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

    def route_request(self, user_input: str, conversation_store=None) -> str:
        try:
            chat_history = ""

            if conversation_store:
                recent_messages = conversation_store.get_last_n_messages(n=10)
                if recent_messages:
                    chat_history = "\n".join(
                        [f"{msg.get('type', msg.get('role', 'unknown'))}: {msg['content']}" for msg in recent_messages]
                    )

                    logger.info(
                        f"Router got {len(recent_messages)} messages for session {conversation_store.session_id}")

            agent = create_tool_calling_agent(
                llm=ChatOpenAI(
                    model="gpt-4.1-mini",
                    temperature=0.1
                ),
                prompt=self.prompt,
                tools=[]
            )

            agent_executor = AgentExecutor(
                agent=agent,
                tools=[],
                verbose=True
            )

            response: dict[str, Any] = agent_executor.invoke({"user_input": user_input, "chat_history": chat_history})

            agent_choice = response.get("output", "OPPORTUNITY_INTAKE_ADVISOR_AGENT")

            logger.info(f"Router response: '{response}' -> cleaned: '{agent_choice}'")

            valid_agents = ["OPPORTUNITY_INTAKE_CREATION_AGENT", "OPPORTUNITY_INTAKE_ADVISOR_AGENT"]

            return agent_choice if any(agent in agent_choice for agent in valid_agents) else "OPPORTUNITY_INTAKE_ADVISOR_AGENT"

        except Exception as e:
            logger.error(f"Routing failed: {e}")
            return "OPPORTUNITY_INTAKE_ADVISOR_AGENT"
