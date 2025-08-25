import json
import logging
from langchain_openai import ChatOpenAI
from common.redis_infrastructure import infra
from common.utils.llm_util import format_chat_history_for_prompt

logger = logging.getLogger(__name__)


def handle_agent_streaming(
    user_input: str,
    agent_instance,
    agent_name: str,
    result_channel: str,
    session: str,
    conversation_store=None,
    chat_history: list = None,
) -> bool:
    try:
        if conversation_store is None:
            from app.infrastructure import infra

            conversation_store = infra.get_conversation_store(session_id=session)

        if chat_history is None:
            chat_history = conversation_store.get_last_n_messages(15)

        # Only stream for the creation agent, not the advisor
        if agent_name == "opportunity_intake_creation_agent":
            return _handle_streaming_response(
                user_input, agent_instance, agent_name, result_channel, 
                session, conversation_store, chat_history
            )
        else:
            # For advisor agent, generate response without streaming
            return _handle_non_streaming_response(
                user_input, agent_instance, agent_name, result_channel,
                session, conversation_store, chat_history
            )

    except Exception as e:
        logger.exception(f"Agent response handling failed for {agent_name}: {e}")
        return False


def _handle_streaming_response(
    user_input: str,
    agent_instance,
    agent_name: str,
    result_channel: str,
    session: str,
    conversation_store,
    chat_history: list,
) -> bool:
    """Handle streaming response for creation agent"""
    try:
        prompt = agent_instance.prompt

        formatted_prompt = prompt.format(
            query=user_input,
            chat_history=format_chat_history_for_prompt(chat_history)
        )

        llm = ChatOpenAI(model="gpt-4.1-mini", streaming=True)

        full_response = ""

        for chunk in llm.stream(formatted_prompt):
            if chunk.content:
                full_response += chunk.content
                _publish_chunk(
                    chunk=chunk.content,
                    channel=result_channel,
                    agent_name=agent_name,
                    progress="streaming",
                )

        if full_response:
            conversation_store.add_conversation_turn(
                user_input=user_input, assistant_response=full_response
            )

            result = {"agent_name": agent_name, "content": full_response}

            _publish_chunk(
                chunk="",
                channel=result_channel,
                agent_name=agent_name,
                progress="complete",
                final_result=result,
            )

            logger.info(f"Streaming completed for {agent_name} in session: {session}")
            return True

        return True

    except Exception as e:
        logger.exception(f"Streaming failed for {agent_name}: {e}")
        return False


def _handle_non_streaming_response(
    user_input: str,
    agent_instance,
    agent_name: str,
    result_channel: str,
    session: str,
    conversation_store,
    chat_history: list,
) -> bool:
    """Handle non-streaming response for advisor agent"""
    try:
        # Generate response using the agent's method
        response = agent_instance.generate_response(conversation_store, user_input)
        
        if response:
            # Publish the complete response immediately
            _publish_chunk(
                chunk="",
                channel=result_channel,
                agent_name=agent_name,
                progress="complete",
                final_result=response,
            )
            
            logger.info(f"Non-streaming response completed for {agent_name} in session: {session}")
            return True
        else:
            logger.error(f"Advisor agent returned no response for {agent_name}")
            return False

    except Exception as e:
        logger.exception(f"Non-streaming response failed for {agent_name}: {e}")
        return False


def _publish_chunk(
    chunk: str, channel: str, agent_name: str, progress: str, final_result: dict = None
) -> bool:
    redis_client = infra.redis_client

    message = {"agent_name": str(agent_name), "progress": progress, "chunk": chunk}

    if final_result:
        message["result"] = json.dumps(final_result)

    redis_client.xadd(channel, message, maxlen=1000, approximate=True)
    return True
