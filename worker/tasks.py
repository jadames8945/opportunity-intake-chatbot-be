import logging

from worker.config import worker_app

logger = logging.getLogger(__name__)


@worker_app.task(name="save_chat_history_task")
def save_chat_history_task(title: str, chat_history: list):
    try:
        from app.services.chat_history_service import ChatHistoryService

        service = ChatHistoryService()
        success = service.save_to_mongodb(title, chat_history)

        if success:
            logger.info(f"Successfully saved chat history: {title}")
        else:
            logger.error(f"Failed to save chat history: {title}")

        return success

    except Exception as e:
        logger.exception(f"Error in save_chat_history_task: {e}")
        return False


@worker_app.task(name="invoke_unified_stream")
def invoke_unified_stream(user_input: str, session: str, result_channel: str, chat_history: list = None) -> bool:
    try:
        from app.services.unified_service import UnifiedService
        from worker.streaming_handler import handle_agent_streaming
        from app.infrastructure import infra

        conversation_store = infra.get_conversation_store(session_id=session)
        
        if chat_history:
            conversation_store.clear_history()
            conversation_store.set_messages(chat_history)

        unified_service = UnifiedService()

        agent, agent_name = unified_service.handle_request(
            user_input=user_input,
            conversation_store=conversation_store
        )

        success = handle_agent_streaming(
            user_input=user_input,
            agent_instance=agent,
            agent_name=agent_name,
            result_channel=result_channel,
            session=session,
            conversation_store=conversation_store,
        )

        return success

    except Exception as e:
        logger.exception(f"Unified streaming task failed: {e}")
        return False
