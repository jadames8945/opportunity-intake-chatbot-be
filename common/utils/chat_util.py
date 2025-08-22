from typing import List, Dict, Any


def convert_contexts_to_base_messages(retrieved_contexts, default_role="user"):
    return [{"role": default_role, "content": ctx} for ctx in retrieved_contexts]


def chat_history_to_str(chat_history):
    return "\n".join(f"{msg['role']}: {msg['content']}" for msg in chat_history)


def docs_to_chat_history(relevant_docs: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    return [
        {
            "role": doc.get("metadata", {}).get("role", "user"),
            "content": doc.get("content", ""),
        }
        for doc in relevant_docs
    ]


MAX_HISTORY = 100


def trim_vector_store(vector_store: List[Dict[str, str]]):
    if len(vector_store) > MAX_HISTORY:
        del vector_store[:-MAX_HISTORY]
