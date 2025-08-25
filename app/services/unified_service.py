import logging
from typing import Dict, Any, Optional, List

from app.agent.opportunity_intake_advisor_agent import OpportunityIntakeAdvisorAgent
from app.agent.opportunity_intake_creation_agent import OpportunityIntakeCreationAgent
from app.agent.router_agent import RouterAgent
from app.config.conversation_store import ConversationStore


logger = logging.getLogger(__name__)


class UnifiedService:
    def __init__(self):
        self.router_agent = RouterAgent()
        self.opportunity_intake_advisor_agent = OpportunityIntakeAdvisorAgent()
        self.opportunity_intake_creation_agent = OpportunityIntakeCreationAgent()

    def handle_request(self, user_input: str, conversation_store: ConversationStore):
        logger.info(f"Handling request: {user_input}")

        try:
            agent_choice = self.router_agent.route_request(
                user_input, conversation_store
            )

            logger.info(f"Router chose: {agent_choice}")

            match agent_choice:
                case "OPPORTUNITY_INTAKE_CREATION_AGENT":
                    return OpportunityIntakeCreationAgent(), "opportunity_intake_creation_agent"
                case _:
                    return OpportunityIntakeAdvisorAgent(), "opportunity_intake_advisor_agent"

        except Exception as e:
            logger.error(f"Request handling failed: {e}")
            return self._handle_opportunity_intake_advisor_request(user_input)

    def _handle_opportunity_intake_advisor_request(self, user_input: str) -> OpportunityIntakeAdvisorAgent:
        logger.info("Handling opportunity intake advisor request")
        return OpportunityIntakeAdvisorAgent()
