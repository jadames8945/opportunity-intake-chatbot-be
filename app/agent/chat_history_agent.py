import logging
from typing import List, Dict

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.agent.prompts.chat_history_prompts import CHAT_HISTORY_ROLE, RESPONSE_FORMAT
from common.utils.llm_util import format_chat_history_for_prompt

logger = logging.getLogger(__name__)


class ChatHistoryAgent:
    def __init__(self) -> None:
        self.prompt = self.build_prompt()

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
                    {CHAT_HISTORY_ROLE}
                    
                    {RESPONSE_FORMAT}
                    
                    Chat History:
                    {{chat_history}}
                    
                    User Query:
                    {{query}}
                    """,
                ),
            ]
        )

    def get_chat_history_title_stream(self, chat_history: List[Dict[str, str]]):
        try:
            formatted_prompt = self.prompt.format(
                query="Generate a concise title for this conversation",
                chat_history=format_chat_history_for_prompt(chat_history)
            )

            llm = ChatOpenAI(
                model="gpt-4o-mini",
                streaming=True
            )

            return llm.stream(formatted_prompt)

        except Exception as e:
            logger.error(f"Failed to generate chat history title: {e}")
            return None
