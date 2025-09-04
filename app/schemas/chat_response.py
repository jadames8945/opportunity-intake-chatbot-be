from typing import Any, Dict, Optional

from pydantic import BaseModel


class ChatResponseData(BaseModel):
    """Response data for chat interactions"""

    message: str
    success: bool = True
    error_message: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat agent interactions"""

    agent_name: str = "Chat Assistant"
    request_id: Optional[str] = None
    user_input: str
    response_data: ChatResponseData
    error_message: Optional[str] = None

    @staticmethod
    def build_chat_result(
        user_input: str,
        message: str,
        request_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Helper to build a chat response"""
        response_data = ChatResponseData(
            message=message, success=success, error_message=error_message
        )

        chat_response = ChatResponse(
            request_id=request_id,
            user_input=user_input,
            response_data=response_data,
            error_message=error_message,
        )

        return chat_response.model_dump(mode="json")

    @staticmethod
    def build_error_result(
        user_input: str, error_message: str, request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Helper to build an error chat response"""
        return ChatResponse.build_chat_result(
            user_input=user_input,
            message="I'm sorry, I encountered an error. Please try again.",
            request_id=request_id,
            success=False,
            error_message=error_message,
        )
