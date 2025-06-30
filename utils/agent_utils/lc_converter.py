from typing import Dict, List

from langchain_core.messages import BaseMessage, AIMessage, HumanMessage


MAP_DEF_TO_LC = {"assistant": AIMessage, "user": HumanMessage}


def convert_to_lc_messages(messages: List[Dict]) -> List[BaseMessage]:
    return [
        MAP_DEF_TO_LC[m.get("role")](content=m.get("content"))
        for m in messages
        if m.get("role") in MAP_DEF_TO_LC
    ]
