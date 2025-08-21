import os
from typing import Optional
from libs.utils.langfuse_manager import (
    LangfusePromptName,
    LangFusePromptManager,
    PromptSource,
)


async def build_map_prompts_cfg(
    tags: list[str],
    prompt_source: Optional[PromptSource] = None,
    model_name: Optional[str] = None,
):
    map_prompts_cfg = dict()

    map_prompts_cfg[LangfusePromptName.SIMPLE_REACT_SYSTEM_PROMPT] = (
        await LangFusePromptManager.build_msg(
            name=LangfusePromptName.SIMPLE_REACT_SYSTEM_PROMPT,
            tags=tags,
            config={
                "model_name": "gpt-4.1-2025-04-14",
                "temperature": 0.0,
                "base_url": None,
            },
            return_config=True,
            prompt_source=prompt_source,
        )
    )

    if model_name:
        map_prompts_cfg[LangfusePromptName.SIMPLE_REACT_SYSTEM_PROMPT][1][
            "model_name"
        ] = model_name
        map_prompts_cfg[LangfusePromptName.SIMPLE_REACT_SYSTEM_PROMPT][1][
            "base_url"
        ] = os.getenv("OLLAMA_BASE_URL")

    return map_prompts_cfg
