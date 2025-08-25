import logging
import uuid
from typing import Dict, Any, List, Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.agent.prompts.opportunity_intake_creation_prompts import (
    OPPORTUNITY_INTAKE_ROLE, 
    OPPORTUNITY_INTAKE_CAPABILITIES, 
    OPPORTUNITY_INTAKE_GUIDELINES, 
    OPPORTUNITY_INTAKE_FORMAT
)
from app.config.conversation_store import ConversationStore
from app.schemas.opportunity_response import OpportunityResponse
from common.utils.llm_util import invoke_llm_with_string_prompt, validate_agent_response

logger = logging.getLogger(__name__)


class OpportunityIntakeCreationAgent:
    def __init__(self) -> None:
        self.prompt = self.build_prompt()

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
                    {OPPORTUNITY_INTAKE_ROLE}

                    {OPPORTUNITY_INTAKE_CAPABILITIES}
                    
                    {OPPORTUNITY_INTAKE_GUIDELINES}
                   
                    {OPPORTUNITY_INTAKE_FORMAT}
                    
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
            self,
            conversation_store: ConversationStore,
            user_input: str
    ) -> Optional[Dict[str, Any]]:
        chat_history = conversation_store.get_last_n_messages(n=10)

        try:
            formatted_prompt = self.prompt.format(
                query=user_input,
                chat_history=chat_history,
            )

            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model="gpt-4o-mini", streaming=False)
            response = llm.invoke(formatted_prompt)

            if response.content:
                conversation_store.add_conversation_turn(
                    user_input=user_input,
                    assistant_response=response.content
                )

                return OpportunityResponse.build_opportunity_result(
                    user_input=user_input,
                    opportunity_content=response.content,
                )
            else:
                raise Exception("Opportunity intake advisor agent returned no response")

        except Exception as e:
            logger.warning(f"Opportunity intake advisor agent failed, using fallback: {e}")
            return self._build_fallback_response(
                user_input=user_input,
                content={"error": "Chat failed. Please try again."}
            )

    def _build_fallback_response(
            self,
            user_input: str,
            content: Dict[str, Any]
    ) -> Dict[str, Any]:
        return OpportunityResponse.build_opportunity_result(
            user_input=user_input,
            opportunity_content="I'm sorry, I encountered an error. Please try again.",
        )
