import logging
from typing import Dict, List

from common.redis_infrastructure import infra
from common.utils.llm_util import format_chat_history_for_prompt
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.config.conversation_store import ConversationStore
from app.services.airtable_cache import AirtableCache

logger = logging.getLogger(__name__)


def handle_agent_streaming(
    user_input: str,
    agent_instance,
    agent_name: str,
    result_channel: str,
    session_id: str,
    conversation_store: ConversationStore,
) -> bool:
    try:

        chat_history = (
            conversation_store.get_all_messages()
            if agent_name == "opportunity_intake_advisor_agent"
            else conversation_store.get_last_n_messages(10)
        )

        logger.info(f"session_id:{session_id} chat history: {chat_history}")

        return _handle_streaming_response(
            user_input=user_input,
            agent_instance=agent_instance,
            agent_name=agent_name,
            result_channel=result_channel,
            session_id=session_id,
            conversation_store=conversation_store,
            chat_history=chat_history,
        )

    except Exception as e:
        logger.exception(f"Agent response handling failed for {agent_name}: {e}")
        return False


def get_formatted_prompt(
    user_input: str,
    agent_name: str,
    prompt: ChatPromptTemplate,
    chat_history: List[Dict[str, str]],
) -> str:
    if agent_name == "opportunity_intake_advisor_agent":
        return prompt.format(
            query=user_input,
            airtable_context=AirtableCache().get_data(),
            chat_history=format_chat_history_for_prompt(chat_history),
        )

    return prompt.format(
        query=user_input, chat_history=format_chat_history_for_prompt(chat_history)
    )


def _handle_streaming_response(
    user_input: str,
    agent_instance,
    agent_name: str,
    result_channel: str,
    session_id: str,
    conversation_store,
    chat_history: List[Dict[str, str]],
) -> bool:
    try:
        prompt: ChatPromptTemplate = agent_instance.prompt

        formatted_prompt = get_formatted_prompt(
            user_input=user_input,
            agent_name=agent_name,
            prompt=prompt,
            chat_history=chat_history,
        )

        llm = ChatOpenAI(model="gpt-4.1-mini", streaming=True)

        full_response = ""
        buffer = ""
        chunk_size = 15

        for chunk in llm.stream(formatted_prompt):
            if chunk.content:
                full_response += chunk.content
                buffer += chunk.content

                if len(buffer) >= chunk_size:
                    _publish_chunk(
                        chunk=buffer,
                        channel=result_channel,
                        agent_name=agent_name,
                        progress="streaming",
                    )
                    buffer = ""

        if buffer:
            _publish_chunk(
                chunk=buffer,
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

            logger.info(
                f"Streaming completed for {agent_name} in session: {session_id}"
            )
            return True

        return True

    except Exception as e:
        logger.exception(f"Streaming failed for {agent_name}: {e}")
        return False


def _publish_chunk(
    chunk: str, channel: str, agent_name: str, progress: str, final_result: dict = None
) -> bool:
    redis_client = infra.redis_client

    message = {"agent_name": str(agent_name), "progress": progress, "chunk": chunk}

    if final_result:
        message.update(final_result)

    redis_client.xadd(channel, message, maxlen=1000, approximate=True)
    return True
