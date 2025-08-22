import json
import logging
from typing import Optional, Dict, Any, List

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


def invoke_llm_with_prompt(
    prompt: ChatPromptTemplate,
    user_input: str,
    chat_history: List[Dict[str, str]],
    parser: Optional[PydanticOutputParser] = None,
    model: str = "gpt-4o-mini",
    streaming: bool = False,
    **kwargs,
) -> Dict[str, Any]:
    """
    Standardized LLM invocation for all agents.

    Args:
        prompt: The formatted prompt template
        user_input: User's input query
        chat_history: Previous conversation history
        parser: Optional Pydantic parser for response validation
        model: OpenAI model to use
        streaming:
        **kwargs: Additional prompt variables

    Returns:
        Parsed response as dictionary
    """
    try:
        formatted_prompt = prompt.format(
            query=user_input,
            chat_history=format_chat_history_for_prompt(chat_history),
            **kwargs,
        )

        llm = ChatOpenAI(
            model=model, 
            streaming=streaming,
            model_kwargs={"response_format": {"type": "json_object"}}
        )

        response = llm.invoke(formatted_prompt)

        if parser:
            parsed_response = parser.parse(response.content)
            return parsed_response.model_dump()
        else:
            return json.loads(response.content)

    except Exception as e:
        logger.exception(f"LLM invocation failed: {e}")
        raise


def invoke_llm_with_string_prompt(
    prompt: ChatPromptTemplate,
    user_input: str,
    chat_history: List[Dict[str, str]],
    model: str = "gpt-4o-mini",
    streaming: bool = False,
    **kwargs,
) -> str:
    """
    LLM invocation for agents that return plain text (not JSON).

    Args:
        prompt: The formatted prompt template
        user_input: User's input query
        chat_history: Previous conversation history
        model: OpenAI model to use
        streaming: Whether to enable streaming responses
        **kwargs: Additional prompt variables

    Returns:
        Raw text response from LLM
    """
    try:
        formatted_prompt = prompt.format(
            query=user_input,
            chat_history=format_chat_history_for_prompt(chat_history),
            **kwargs,
        )

        llm = ChatOpenAI(
            model=model, 
            streaming=streaming
        )

        response = llm.invoke(formatted_prompt)
        return response.content

    except Exception as e:
        logger.exception(f"LLM invocation failed: {e}")
        raise


def validate_agent_response(
    response: Optional[Dict[str, Any]],
    user_input: str,
    agent_name: str,
    build_result_func,
    **kwargs,
) -> Dict[str, Any]:
    """
    Standardized response validation for all agents.

    Args:
        response: Parsed response from LLM
        user_input: Original user input
        agent_name: Name of the agent for logging
        build_result_func: Function to build fallback result
        **kwargs: Additional arguments for build_result_func

    Returns:
        Validated response dictionary
    """
    try:
        if not response:
            raise Exception(f"{agent_name} failed: No parsed response.")

        logger.info(f"{agent_name} response: {response}")
        return response

    except Exception as e:
        logger.warning(
            f"LLM did not return valid JSON for {agent_name}, using fallback error object: {e}"
        )

        return build_result_func(
            user_input=user_input,
            content={"error": f"Invalid output: {str(e)}"},
            success=False,
            **kwargs,
        )


def format_chat_history_for_prompt(chat_history: List[Dict[str, str]]) -> str:
    """
    Format chat history for inclusion in prompts.

    Args:
        chat_history: List of chat messages

    Returns:
        Formatted chat history string
    """
    if not chat_history:
        return "No previous conversation history."

    formatted_history = []
    for msg in chat_history:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        formatted_history.append(f"{role.capitalize()}: {content}")

    return "\n".join(formatted_history)
