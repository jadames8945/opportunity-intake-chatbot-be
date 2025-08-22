import logging
import uuid
from typing import Dict, Any, List, Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.agent.prompts.opportunity_intake_prompts import OPPORTUNITY_ROLE, OPPORTUNITY_GOALS, OPPORTUNITY_STRUCTURE, RESPONSE_FORMAT
from app.config.conversation_store import ConversationStore
from app.schemas.opportunity_response import OpportunityResponse
from common.utils.llm_util import invoke_llm_with_string_prompt, validate_agent_response

logger = logging.getLogger(__name__)


class OpportunityIntakeAgent:
    def __init__(self) -> None:
        self.prompt = self.build_prompt()

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
                    {OPPORTUNITY_ROLE}

                    {OPPORTUNITY_GOALS}
                    
                    {OPPORTUNITY_STRUCTURE}
                   
                    {RESPONSE_FORMAT}
                    
                    Chat History:
                    {{chat_history}}
                    
                    User Query:
                    {{query}}
                    """,
                ),
                ("human", "{query}"),
            ]
        )

    def generate_response(
        self, conversation_store: ConversationStore, user_input: str
    ) -> Optional[Dict[str, Any]]:
        chat_history = conversation_store.get_last_n_messages(n=15)

        try:
            response_content = invoke_llm_with_string_prompt(
                prompt=self.prompt,
                user_input=user_input,
                chat_history=chat_history,
                model="gpt-4.1-mini",
            )

            if response_content:
                conversation_store.add_conversation_turn(
                    user_input=user_input,
                    assistant_response=response_content,
                )

                return OpportunityResponse.build_opportunity_result(
                    user_input=user_input,
                    opportunity_content=response_content,
                )
            else:
                raise Exception("Opportunity intake agent returned no response")
        except Exception as e:
            logger.exception(f"Opportunity intake agent encountered an error {e}")
            return None

    def _build_fallback_response(
        self, user_input: str, content: str
    ) -> Dict[str, Any]:
        return OpportunityResponse.build_opportunity_result(
            user_input=user_input, opportunity_content=content
        ) 