import logging
from typing import Any, Dict, List, Optional

from common.utils.llm_util import invoke_llm_with_string_prompt
from langchain_core.prompts import ChatPromptTemplate

from app.agent.prompts.opportunity_intake_advisor_prompts import (
    CHAT_CAPABILITIES,
    CHAT_GUIDELINES,
    CHAT_ROLE,
    RESPONSE_FORMAT,
)
from app.caches.conversation_store import ConversationStore
from app.schemas.opportunity_response import OpportunityResponse

logger = logging.getLogger(__name__)


class OpportunityIntakeAdvisorAgent:
    def __init__(self) -> None:
        self.prompt = self.build_prompt()

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
                    {CHAT_ROLE}

                    {CHAT_CAPABILITIES}
                    
                    {CHAT_GUIDELINES}
                    
                    {RESPONSE_FORMAT}
                    
                    Chat History:
                    {{chat_history}}
                    
                    Airtable Context:
                    {{airtable_context}}
                    
                    User Query:
                    {{query}}
                    """,
                ),
            ]
        )

    def generate_response(
        self, conversation_store: ConversationStore, user_input: str
    ) -> Optional[Dict[str, Any]]:
        chat_history: List[Dict[str, Any]] = conversation_store.get_last_n_messages(
            n=10
        )

        try:
            response_content = invoke_llm_with_string_prompt(
                prompt=self.prompt,
                user_input=user_input,
                chat_history=chat_history,
            )

            if response_content:
                conversation_store.add_conversation_turn(
                    user_input=user_input, assistant_response=response_content
                )

                return OpportunityResponse.build_opportunity_result(
                    user_input=user_input,
                    opportunity_content=response_content,
                )
            else:
                raise Exception("Opportunity intake advisor agent returned no response")

        except Exception as e:
            logger.warning(
                f"Opportunity intake advisor agent failed, using fallback: {e}"
            )
            return self._build_fallback_response(
                user_input=user_input,
                content={"error": "Chat failed. Please try again."},
            )

    def _build_fallback_response(
        self, user_input: str, content: Dict[str, Any]
    ) -> Dict[str, Any]:
        return OpportunityResponse.build_opportunity_result(
            user_input=user_input,
            opportunity_content="I'm sorry, I encountered an error. Please try again.",
        )
